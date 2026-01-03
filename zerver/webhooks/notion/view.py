from collections.abc import Callable
from typing import Any

import requests
from django.http import HttpRequest
from django.http.response import HttpResponse
from pydantic import Json

from zerver.decorator import webhook_view
from zerver.lib.exceptions import UnsupportedWebhookEventTypeError
from zerver.lib.response import json_success
from zerver.lib.typed_endpoint import JsonBodyPayload, typed_endpoint
from zerver.lib.validator import WildValue, check_dict, check_list, check_none_or, check_string
from zerver.lib.webhooks.common import OptionalUserSpecifiedTopicStr, check_send_webhook_message
from zerver.models import UserProfile

NOTION_VERIFICATION_TOKEN_MESSAGE = """
This is a webhook configuration test message from Notion.

Your verification token is: `{token}`

Please copy this token and paste it into your Notion webhook configuration to complete the setup.
""".strip()


def get_notion_api_headers(notion_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2025-09-03",
        "Content-Type": "application/json",
    }


def extract_page_title(page_data: dict[str, Any]) -> str:
    if not page_data or "properties" not in page_data:
        return "Untitled Page"

    properties = page_data.get("properties", {})

    # The title of the page is stored in the properties dictionary can be nested which is not given straight forward key.
    # Try common title property names first (most pages use these)
    for common_name in ["title", "Title", "Name", "name"]:
        if common_name in properties:
            prop_value = properties[common_name]
            if isinstance(prop_value, dict) and prop_value.get("type") == "title":
                title_content = prop_value.get("title", [])
                if title_content and isinstance(title_content, list) and len(title_content) > 0:
                    plain_text = title_content[0].get("plain_text")
                    if plain_text:
                        return plain_text

    # Fallback: iterate through all properties (rare case)
    for prop_value in properties.values():
        if isinstance(prop_value, dict) and prop_value.get("type") == "title":
            title_content = prop_value.get("title", [])
            if title_content and isinstance(title_content, list) and len(title_content) > 0:
                plain_text = title_content[0].get("plain_text")
                if plain_text:
                    return plain_text

    return "Untitled Page"


def extract_database_title(database_data: dict[str, Any]) -> str:
    if not database_data:
        return "Untitled Database"

    # Database titles are in a simpler structure than pages so straight forward look up in the titles array.
    title_list = database_data.get("title", [])
    if title_list and isinstance(title_list, list):
        for title_obj in title_list:
            if isinstance(title_obj, dict):
                plain_text = title_obj.get("plain_text")
                if plain_text:
                    return plain_text

    return "Untitled Database"


def get_page_title(notion_token: str, page_id: str) -> str:
    if not notion_token:
        return page_id  # Fallback to ID if no token provided

    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = get_notion_api_headers(notion_token)

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            page_data = response.json()
            return extract_page_title(page_data)
        else:
            return page_id  # Fallback to ID
    except Exception:
        return page_id  # Fallback to ID


def get_database_title(notion_token: str, database_id: str) -> str:
    if not notion_token:
        return database_id  # Fallback to ID if no token provided

    url = f"https://api.notion.com/v1/databases/{database_id}"
    headers = get_notion_api_headers(notion_token)

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            database_data = response.json()
            return extract_database_title(database_data)
        else:
            return database_id  # Fallback to ID
    except Exception:
        return database_id  # Fallback to ID


def get_user_name(notion_token: str, user_id: str) -> str:
    if not user_id:
        return "Notion User"
    if not notion_token:
        return f"user: {user_id}"
    url = f"https://api.notion.com/v1/users/{user_id}"
    headers = get_notion_api_headers(notion_token)

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            user_data = response.json()

            name = user_data.get("name")
            if name:
                return name

            # Fallback: Try to extract name from email for person type
            if user_data.get("type") == "person":
                person = user_data.get("person", {})
                email = person.get("email", "")
                if email:
                    name = email.split("@")[0].replace(".", " ").title()
                    return name

            return f"user: {user_id}"
        else:
            return f"user: {user_id}"
    except Exception:
        return f"user: {user_id}"


def get_author_name(payload: WildValue, notion_token: str) -> str:
    authors = payload.get("authors")
    if authors:
        # authors is a list - get the first one
        authors_list = authors.tame(
            check_list(check_dict([("id", check_string), ("type", check_string)]))
        )
        if authors_list and len(authors_list) > 0:
            first_author = authors_list[0]
            user_id = first_author.get("id")

            if user_id and isinstance(user_id, str):
                author_name = get_user_name(notion_token, user_id)

                # If there are multiple authors, add count (to avoid multiple api calls to fetch each author)
                if len(authors_list) > 1:
                    others_count = len(authors_list) - 1
                    return f"{author_name} (+{others_count} other{'s' if others_count > 1 else ''})"

                return author_name

    return ""


def get_page_content_updated_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    page_id = payload["entity"]["id"].tame(check_string)
    if not page_id:
        return ("Notion Page", "Page content was updated")
    page_title = get_page_title(notion_token, page_id)
    author = get_author_name(payload, notion_token)

    if author:
        body = f"**{author}** updated page **{page_title}** content"
    else:
        body = f"Page **{page_title}** content was updated"

    return (f"page: {page_title}", body)


def get_page_created_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    page_id = payload["entity"]["id"].tame(check_string)
    if not page_id:
        return ("Notion Page", "New page was created")
    page_title = get_page_title(notion_token, page_id)
    author = get_author_name(payload, notion_token)

    if author:
        body = f"**{author}** created page **{page_title}**"
    else:
        body = f"New page **{page_title}** was created"

    return (f"page: {page_title}", body)


def get_page_deleted_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    page_id = payload["entity"]["id"].tame(check_string)
    if not page_id:
        return ("Notion Page", "Page was moved to trash")
    page_title = get_page_title(notion_token, page_id)
    author = get_author_name(payload, notion_token)

    if author:
        body = f"**{author}** moved page **{page_title}** to trash"
    else:
        body = f"Page **{page_title}** was moved to trash"

    return (f"page: {page_title}", body)


def get_page_locked_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    page_id = payload["entity"]["id"].tame(check_string)
    if not page_id:
        return ("Notion Page", "Page was locked")
    page_title = get_page_title(notion_token, page_id)
    author = get_author_name(payload, notion_token)

    if author:
        body = f"**{author}** locked page **{page_title}**"
    else:
        body = f"Page **{page_title}** was locked"

    return (f"page: {page_title}", body)


def get_page_moved_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    page_id = payload["entity"]["id"].tame(check_string)
    if not page_id:
        return ("Notion Page", "Page was moved")
    page_title = get_page_title(notion_token, page_id)
    author = get_author_name(payload, notion_token)

    if author:
        body = f"**{author}** moved page **{page_title}**"
    else:
        body = f"Page **{page_title}** was moved"

    return (f"page: {page_title}", body)


def get_page_properties_updated_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    page_id = payload["entity"]["id"].tame(check_string)
    if not page_id:
        return ("Notion Page", "Page properties were updated")
    page_title = get_page_title(notion_token, page_id)
    author = get_author_name(payload, notion_token)

    if author:
        body = f"**{author}** updated page **{page_title}** properties"
    else:
        body = f"Page **{page_title}** properties were updated"

    return (f"page: {page_title}", body)


def get_page_undeleted_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    page_id = payload["entity"]["id"].tame(check_string)
    if not page_id:
        return ("Notion Page", "Page was restored from trash")
    page_title = get_page_title(notion_token, page_id)
    author = get_author_name(payload, notion_token)

    if author:
        body = f"**{author}** restored page **{page_title}** from trash"
    else:
        body = f"Page **{page_title}** was restored from trash"

    return (f"page: {page_title}", body)


def get_page_unlocked_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    page_id = payload["entity"]["id"].tame(check_string)
    if not page_id:
        return ("Notion Page", "Page was unlocked")
    page_title = get_page_title(notion_token, page_id)
    author = get_author_name(payload, notion_token)

    if author:
        body = f"**{author}** unlocked page **{page_title}**"
    else:
        body = f"Page **{page_title}** was unlocked"

    return (f"page: {page_title}", body)


def get_database_content_updated_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    database_id = payload["entity"]["id"].tame(check_string)
    if not database_id:
        return ("Notion Database", "Database content was updated")
    database_title = get_database_title(notion_token, database_id)
    author = get_author_name(payload, notion_token)

    body = (
        f"**{author}** updated database **{database_title}** content"
        if author
        else f"Database **{database_title}** content was updated"
    )
    return (f"db: {database_title}", body)


def get_database_created_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    database_id = payload["entity"]["id"].tame(check_string)
    if not database_id:
        return ("Notion Database", "New database was created")
    database_title = get_database_title(notion_token, database_id)
    author = get_author_name(payload, notion_token)

    body = (
        f"**{author}** created database **{database_title}**"
        if author
        else f"New database **{database_title}** was created"
    )
    return (f"db: {database_title}", body)


def get_database_deleted_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    database_id = payload["entity"]["id"].tame(check_string)
    if not database_id:
        return ("Notion Database", "Database was moved to trash")
    database_title = get_database_title(notion_token, database_id)
    author = get_author_name(payload, notion_token)

    body = (
        f"**{author}** moved database **{database_title}** to trash"
        if author
        else f"Database **{database_title}** was moved to trash"
    )
    return (f"db: {database_title}", body)


def get_database_moved_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    database_id = payload["entity"]["id"].tame(check_string)
    if not database_id:
        return ("Notion Database", "Database was moved")
    database_title = get_database_title(notion_token, database_id)
    author = get_author_name(payload, notion_token)

    body = (
        f"**{author}** moved database **{database_title}**"
        if author
        else f"Database **{database_title}** was moved"
    )
    return (f"db: {database_title}", body)


def get_database_schema_updated_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    database_id = payload["entity"]["id"].tame(check_string)
    if not database_id:
        return ("Notion Database", "Database schema was updated")
    database_title = get_database_title(notion_token, database_id)
    author = get_author_name(payload, notion_token)

    body = (
        f"**{author}** updated database **{database_title}** schema"
        if author
        else f"Database **{database_title}** schema was updated"
    )
    return (f"db: {database_title}", body)


def get_database_undeleted_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    database_id = payload["entity"]["id"].tame(check_string)
    if not database_id:
        return ("Notion Database", "Database was restored from trash")
    database_title = get_database_title(notion_token, database_id)
    author = get_author_name(payload, notion_token)

    body = (
        f"**{author}** restored database **{database_title}** from trash"
        if author
        else f"Database **{database_title}** was restored from trash"
    )
    return (f"db: {database_title}", body)


def get_data_source_content_updated_message(
    payload: WildValue, notion_token: str
) -> tuple[str, str]:
    data_source_id = payload["entity"]["id"].tame(check_string)
    if not data_source_id:
        return ("Notion Data Source", "Data source content was updated")
    data_source_title = get_database_title(notion_token, data_source_id)
    author = get_author_name(payload, notion_token)

    body = (
        f"**{author}** updated data source **{data_source_title}** content"
        if author
        else f"Data source **{data_source_title}** content was updated"
    )
    return (f"ds: {data_source_title}", body)


def get_data_source_created_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    data_source_id = payload["entity"]["id"].tame(check_string)
    if not data_source_id:
        return ("Notion Data Source", "New data source was created")
    data_source_title = get_database_title(notion_token, data_source_id)
    author = get_author_name(payload, notion_token)

    body = (
        f"**{author}** created data source **{data_source_title}**"
        if author
        else f"New data source **{data_source_title}** was created"
    )
    return (f"ds: {data_source_title}", body)


def get_data_source_deleted_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    data_source_id = payload["entity"]["id"].tame(check_string)
    if not data_source_id:
        return ("Notion Data Source", "Data source was moved to trash")
    data_source_title = get_database_title(notion_token, data_source_id)
    author = get_author_name(payload, notion_token)

    body = (
        f"**{author}** moved data source **{data_source_title}** to trash"
        if author
        else f"Data source **{data_source_title}** was moved to trash"
    )
    return (f"ds: {data_source_title}", body)


def get_data_source_moved_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    data_source_id = payload["entity"]["id"].tame(check_string)
    if not data_source_id:
        return ("Notion Data Source", "Data source was moved")
    data_source_title = get_database_title(notion_token, data_source_id)
    author = get_author_name(payload, notion_token)

    body = (
        f"**{author}** moved data source **{data_source_title}**"
        if author
        else f"Data source **{data_source_title}** was moved"
    )
    return (f"ds: {data_source_title}", body)


def get_data_source_schema_updated_message(
    payload: WildValue, notion_token: str
) -> tuple[str, str]:
    data_source_id = payload["entity"]["id"].tame(check_string)
    if not data_source_id:
        return ("Notion Data Source", "Data source schema was updated")
    data_source_title = get_database_title(notion_token, data_source_id)
    author = get_author_name(payload, notion_token)

    body = (
        f"**{author}** updated data source **{data_source_title}** schema"
        if author
        else f"Data source **{data_source_title}** schema was updated"
    )
    return (f"ds: {data_source_title}", body)


def get_data_source_undeleted_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    data_source_id = payload["entity"]["id"].tame(check_string)
    if not data_source_id:
        return ("Notion Data Source", "Data source was restored from trash")
    data_source_title = get_database_title(notion_token, data_source_id)
    author = get_author_name(payload, notion_token)

    body = (
        f"**{author}** restored data source **{data_source_title}** from trash"
        if author
        else f"Data source **{data_source_title}** was restored from trash"
    )
    return (f"ds: {data_source_title}", body)


def get_comment_created_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    author = get_author_name(payload, notion_token)

    # Get page ID from data.page_id field
    page_id = payload.get("data", {}).get("page_id").tame(check_none_or(check_string))

    if page_id:
        page_title = get_page_title(notion_token, page_id)

        # Check if comment is on a block or page
        parent_type = (
            payload.get("data", {}).get("parent", {}).get("type").tame(check_none_or(check_string))
        )

        if parent_type == "block":
            body = (
                f"**{author}** added a comment on a block in **{page_title}**"
                if author
                else f"New comment on a block in **{page_title}**"
            )
        else:
            body = (
                f"**{author}** added a comment on **{page_title}**"
                if author
                else f"New comment on **{page_title}**"
            )

        return (f"page: {page_title}", body)

    body = f"**{author}** added a comment" if author else "New comment was added"
    return ("Notion Update", body)


def get_comment_deleted_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    author = get_author_name(payload, notion_token)

    page_id = payload.get("data", {}).get("page_id").tame(check_none_or(check_string))

    if page_id:
        page_title = get_page_title(notion_token, page_id)
        body = (
            f"**{author}** deleted a comment on **{page_title}**"
            if author
            else f"Comment deleted on **{page_title}**"
        )
        return (f"page: {page_title}", body)

    body = f"**{author}** deleted a comment" if author else "Comment was deleted"
    return ("Notion Update", body)


def get_comment_updated_message(payload: WildValue, notion_token: str) -> tuple[str, str]:
    author = get_author_name(payload, notion_token)

    page_id = payload.get("data", {}).get("page_id").tame(check_none_or(check_string))

    if page_id:
        page_title = get_page_title(notion_token, page_id)
        body = (
            f"**{author}** updated a comment on **{page_title}**"
            if author
            else f"Comment updated on **{page_title}**"
        )
        return (f"page: {page_title}", body)

    body = f"**{author}** updated a comment" if author else "Comment was updated"
    return ("Notion Update", body)


EVENT_TO_FUNCTION_MAPPER: dict[str, Callable[[WildValue, str], tuple[str, str]]] = {
    # Page events
    "page.content_updated": get_page_content_updated_message,
    "page.created": get_page_created_message,
    "page.deleted": get_page_deleted_message,
    "page.locked": get_page_locked_message,
    "page.moved": get_page_moved_message,
    "page.properties_updated": get_page_properties_updated_message,
    "page.undeleted": get_page_undeleted_message,
    "page.unlocked": get_page_unlocked_message,
    # Database events (legacy, pre-2025-09-03 API)
    "database.content_updated": get_database_content_updated_message,
    "database.created": get_database_created_message,
    "database.deleted": get_database_deleted_message,
    "database.moved": get_database_moved_message,
    "database.schema_updated": get_database_schema_updated_message,
    "database.undeleted": get_database_undeleted_message,
    # Data source events (new in 2025-09-03 API)
    "data_source.content_updated": get_data_source_content_updated_message,
    "data_source.created": get_data_source_created_message,
    "data_source.deleted": get_data_source_deleted_message,
    "data_source.moved": get_data_source_moved_message,
    "data_source.schema_updated": get_data_source_schema_updated_message,
    "data_source.undeleted": get_data_source_undeleted_message,
    # Comment events
    "comment.created": get_comment_created_message,
    "comment.deleted": get_comment_deleted_message,
    "comment.updated": get_comment_updated_message,
}

ALL_EVENT_TYPES = list(EVENT_TO_FUNCTION_MAPPER.keys())


def handle_verification_request(
    request: HttpRequest, user_profile: UserProfile, payload: WildValue
) -> HttpResponse:
    """Handle Notion webhook verification handshake."""
    verification_token = payload.get("verification_token").tame(check_string)
    message_body = NOTION_VERIFICATION_TOKEN_MESSAGE.format(token=verification_token)
    topic = "Notion"
    check_send_webhook_message(request, user_profile, topic, message_body)
    return json_success(request)


def is_verification(payload: WildValue) -> bool:
    """Check if this is a verification handshake from Notion."""
    return payload.get("verification_token").tame(check_none_or(check_string)) is not None


@webhook_view("Notion", all_event_types=ALL_EVENT_TYPES)
@typed_endpoint
def api_notion_webhook(
    request: HttpRequest,
    user_profile: UserProfile,
    *,
    payload: JsonBodyPayload[WildValue],
    notion_token: str = "",  # For Notion API calls to get page titles
    user_specified_topic: OptionalUserSpecifiedTopicStr = None,
    map_pages_to_topics: Json[bool] = False,  # Route pages to separate topics
) -> HttpResponse:
    if is_verification(payload):
        return handle_verification_request(request, user_profile, payload)

    event_type = payload.get("type").tame(check_string)

    if event_type not in EVENT_TO_FUNCTION_MAPPER:
        raise UnsupportedWebhookEventTypeError(event_type)

    handler_function = EVENT_TO_FUNCTION_MAPPER[event_type]
    topic_name, body = handler_function(payload, notion_token)

    if user_specified_topic:
        topic_name = user_specified_topic
    elif not map_pages_to_topics:
        topic_name = "Notion"

    check_send_webhook_message(
        request, user_profile, topic_name, body, complete_event_type=event_type
    )
    return json_success(request)
