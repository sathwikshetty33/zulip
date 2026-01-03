from zerver.lib.test_classes import WebhookTestCase


class NotionWebhookTest(WebhookTestCase):
    CHANNEL_NAME = "notion"
    URL_TEMPLATE = "/api/v1/external/notion?stream={stream}&api_key={api_key}"
    WEBHOOK_DIR_NAME = "notion"

    def test_verification_request(self) -> None:
        """Test that verification handshake works correctly."""
        expected_topic_name = "Notion"
        expected_message = """
This is a webhook configuration test message from Notion.

Your verification token is: `secret_tMrlL1qK5vuQAh1b6cZGhFChZTSYJlce98V0pYn7yBl`

Please copy this token and paste it into your Notion webhook configuration to complete the setup.
""".strip()

        self.check_webhook(
            "verification",
            expected_topic_name,
            expected_message,
            content_type="application/json",
        )

    # Page event tests
    def test_page_created(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** created page **153104cd-477e-809d-8dc4-ff2d96ae3090**"

        self.check_webhook(
            "page_created",
            expected_topic_name,
            expected_message,
        )

    def test_page_content_updated(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** updated page **0ef104cd-477e-80e1-8571-cfd10e92339a** content"

        self.check_webhook(
            "page_content_updated",
            expected_topic_name,
            expected_message,
        )

    def test_page_properties_updated(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** updated page **153104cd-477e-809d-8dc4-ff2d96ae3090** properties"

        self.check_webhook(
            "page_properties_updated",
            expected_topic_name,
            expected_message,
        )

    def test_page_moved(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** moved page **154104cd-477e-8030-9989-d4daf352d900**"

        self.check_webhook(
            "page_moved",
            expected_topic_name,
            expected_message,
        )

    def test_page_deleted(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** moved page **153104cd-477e-8001-935c-c4b11828dfbd** to trash"

        self.check_webhook(
            "page_deleted",
            expected_topic_name,
            expected_message,
        )

    def test_page_undeleted(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** restored page **153104cd-477e-8001-935c-c4b11828dfbd** from trash"

        self.check_webhook(
            "page_undeleted",
            expected_topic_name,
            expected_message,
        )

    def test_page_locked(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** locked page **153104cd-477e-8001-935c-c4b11828dfbd**"

        self.check_webhook(
            "page_locked",
            expected_topic_name,
            expected_message,
        )

    def test_page_unlocked(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** unlocked page **153104cd-477e-8001-935c-c4b11828dfbd**"

        self.check_webhook(
            "page_unlocked",
            expected_topic_name,
            expected_message,
        )

    # Database event tests
    def test_database_created(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** created database **153104cd-477e-80eb-ae76-e1c2a32c7b35**"

        self.check_webhook(
            "database_created",
            expected_topic_name,
            expected_message,
        )

    def test_database_content_updated(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** updated database **15b104cd-477e-80c2-84a0-c32cefba5cff** content"

        self.check_webhook(
            "database_content_updated",
            expected_topic_name,
            expected_message,
        )

    def test_database_moved(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** moved database **153104cd-477e-80eb-ae76-e1c2a32c7b35**"

        self.check_webhook(
            "database_moved",
            expected_topic_name,
            expected_message,
        )

    def test_database_deleted(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** moved database **153104cd-477e-80eb-ae76-e1c2a32c7b35** to trash"

        self.check_webhook(
            "database_deleted",
            expected_topic_name,
            expected_message,
        )

    def test_database_undeleted(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** restored database **153104cd-477e-80eb-ae76-e1c2a32c7b35** from trash"

        self.check_webhook(
            "database_undeleted",
            expected_topic_name,
            expected_message,
        )

    def test_database_schema_updated(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** updated database **153104cd-477e-80eb-ae76-e1c2a32c7b35** schema"

        self.check_webhook(
            "database_schema_updated",
            expected_topic_name,
            expected_message,
        )

    # Data source event tests
    def test_data_source_content_updated(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** updated data source **15b104cd-477e-80c2-84a0-c32cefba5cff** content"

        self.check_webhook(
            "data_source_content_updated",
            expected_topic_name,
            expected_message,
        )

    def test_data_source_created(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** created data source **263104cd-477e-804b-8c32-000b2fcd241a**"

        self.check_webhook(
            "data_source_created",
            expected_topic_name,
            expected_message,
        )

    def test_data_source_deleted(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** moved data source **263104cd-477e-804b-8c32-000b2fcd241a** to trash"

        self.check_webhook(
            "data_source_deleted",
            expected_topic_name,
            expected_message,
        )

    def test_data_source_moved(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** moved data source **263104cd-477e-8025-aae1-000b58fc5834**"

        self.check_webhook(
            "data_source_moved",
            expected_topic_name,
            expected_message,
        )

    def test_data_source_schema_updated(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** updated data source **153104cd-477e-80eb-ae76-e1c2a32c7b35** schema"

        self.check_webhook(
            "data_source_schema_updated",
            expected_topic_name,
            expected_message,
        )

    def test_data_source_undeleted(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** restored data source **263104cd-477e-8025-aae1-000b58fc5834** from trash"

        self.check_webhook(
            "data_source_undeleted",
            expected_topic_name,
            expected_message,
        )

    # Comment event tests
    def test_comment_created(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** added a comment on **0ef104cd-477e-80e1-8571-cfd10e92339a**"

        self.check_webhook(
            "comment_created",
            expected_topic_name,
            expected_message,
        )

    def test_comment_created_on_block(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** added a comment on a block in **0ef104cd-477e-80e1-8571-cfd10e92339a**"

        self.check_webhook(
            "comment_created_on_block",
            expected_topic_name,
            expected_message,
        )

    def test_comment_updated(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** updated a comment on **0ef104cd-477e-80e1-8571-cfd10e92339a**"

        self.check_webhook(
            "comment_updated",
            expected_topic_name,
            expected_message,
        )

    def test_comment_deleted(self) -> None:
        expected_topic_name = "Notion"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** deleted a comment on **0ef104cd-477e-80e1-8571-cfd10e92339a**"

        self.check_webhook(
            "comment_deleted",
            expected_topic_name,
            expected_message,
        )

    # map_pages_to_topics tests - topic should be entity ID/page title when enabled
    def test_page_created_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "page: 153104cd-477e-809d-8dc4-ff2d96ae3090"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** created page **153104cd-477e-809d-8dc4-ff2d96ae3090**"

        self.check_webhook(
            "page_created",
            expected_topic_name,
            expected_message,
        )

    def test_page_content_updated_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "page: 0ef104cd-477e-80e1-8571-cfd10e92339a"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** updated page **0ef104cd-477e-80e1-8571-cfd10e92339a** content"

        self.check_webhook(
            "page_content_updated",
            expected_topic_name,
            expected_message,
        )

    def test_database_created_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "db: 153104cd-477e-80eb-ae76-e1c2a32c7b35"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** created database **153104cd-477e-80eb-ae76-e1c2a32c7b35**"

        self.check_webhook(
            "database_created",
            expected_topic_name,
            expected_message,
        )

    def test_comment_created_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "page: 0ef104cd-477e-80e1-8571-cfd10e92339a"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** added a comment on **0ef104cd-477e-80e1-8571-cfd10e92339a**"

        self.check_webhook(
            "comment_created",
            expected_topic_name,
            expected_message,
        )

    def test_page_properties_updated_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "page: 153104cd-477e-809d-8dc4-ff2d96ae3090"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** updated page **153104cd-477e-809d-8dc4-ff2d96ae3090** properties"

        self.check_webhook(
            "page_properties_updated",
            expected_topic_name,
            expected_message,
        )

    def test_page_moved_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "page: 154104cd-477e-8030-9989-d4daf352d900"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** moved page **154104cd-477e-8030-9989-d4daf352d900**"

        self.check_webhook(
            "page_moved",
            expected_topic_name,
            expected_message,
        )

    def test_page_deleted_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "page: 153104cd-477e-8001-935c-c4b11828dfbd"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** moved page **153104cd-477e-8001-935c-c4b11828dfbd** to trash"

        self.check_webhook(
            "page_deleted",
            expected_topic_name,
            expected_message,
        )

    def test_page_undeleted_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "page: 153104cd-477e-8001-935c-c4b11828dfbd"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** restored page **153104cd-477e-8001-935c-c4b11828dfbd** from trash"

        self.check_webhook(
            "page_undeleted",
            expected_topic_name,
            expected_message,
        )

    def test_page_locked_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "page: 153104cd-477e-8001-935c-c4b11828dfbd"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** locked page **153104cd-477e-8001-935c-c4b11828dfbd**"

        self.check_webhook(
            "page_locked",
            expected_topic_name,
            expected_message,
        )

    def test_page_unlocked_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "page: 153104cd-477e-8001-935c-c4b11828dfbd"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** unlocked page **153104cd-477e-8001-935c-c4b11828dfbd**"

        self.check_webhook(
            "page_unlocked",
            expected_topic_name,
            expected_message,
        )

    def test_database_content_updated_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "db: 15b104cd-477e-80c2-84a0-c32cefba5cff"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** updated database **15b104cd-477e-80c2-84a0-c32cefba5cff** content"

        self.check_webhook(
            "database_content_updated",
            expected_topic_name,
            expected_message,
        )

    def test_database_moved_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "db: 153104cd-477e-80eb-ae76-e1c2a32c7b35"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** moved database **153104cd-477e-80eb-ae76-e1c2a32c7b35**"

        self.check_webhook(
            "database_moved",
            expected_topic_name,
            expected_message,
        )

    def test_database_deleted_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "db: 153104cd-477e-80eb-ae76-e1c2a32c7b35"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** moved database **153104cd-477e-80eb-ae76-e1c2a32c7b35** to trash"

        self.check_webhook(
            "database_deleted",
            expected_topic_name,
            expected_message,
        )

    def test_database_undeleted_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "db: 153104cd-477e-80eb-ae76-e1c2a32c7b35"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** restored database **153104cd-477e-80eb-ae76-e1c2a32c7b35** from trash"

        self.check_webhook(
            "database_undeleted",
            expected_topic_name,
            expected_message,
        )

    def test_database_schema_updated_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "db: 153104cd-477e-80eb-ae76-e1c2a32c7b35"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** updated database **153104cd-477e-80eb-ae76-e1c2a32c7b35** schema"

        self.check_webhook(
            "database_schema_updated",
            expected_topic_name,
            expected_message,
        )

    def test_data_source_content_updated_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "ds: 15b104cd-477e-80c2-84a0-c32cefba5cff"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** updated data source **15b104cd-477e-80c2-84a0-c32cefba5cff** content"

        self.check_webhook(
            "data_source_content_updated",
            expected_topic_name,
            expected_message,
        )

    def test_data_source_created_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "ds: 263104cd-477e-804b-8c32-000b2fcd241a"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** created data source **263104cd-477e-804b-8c32-000b2fcd241a**"

        self.check_webhook(
            "data_source_created",
            expected_topic_name,
            expected_message,
        )

    def test_data_source_deleted_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "ds: 263104cd-477e-804b-8c32-000b2fcd241a"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** moved data source **263104cd-477e-804b-8c32-000b2fcd241a** to trash"

        self.check_webhook(
            "data_source_deleted",
            expected_topic_name,
            expected_message,
        )

    def test_data_source_moved_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "ds: 263104cd-477e-8025-aae1-000b58fc5834"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** moved data source **263104cd-477e-8025-aae1-000b58fc5834**"

        self.check_webhook(
            "data_source_moved",
            expected_topic_name,
            expected_message,
        )

    def test_data_source_schema_updated_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "ds: 153104cd-477e-80eb-ae76-e1c2a32c7b35"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** updated data source **153104cd-477e-80eb-ae76-e1c2a32c7b35** schema"

        self.check_webhook(
            "data_source_schema_updated",
            expected_topic_name,
            expected_message,
        )

    def test_data_source_undeleted_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "ds: 263104cd-477e-8025-aae1-000b58fc5834"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** restored data source **263104cd-477e-8025-aae1-000b58fc5834** from trash"

        self.check_webhook(
            "data_source_undeleted",
            expected_topic_name,
            expected_message,
        )

    def test_comment_created_on_block_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "page: 0ef104cd-477e-80e1-8571-cfd10e92339a"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** added a comment on a block in **0ef104cd-477e-80e1-8571-cfd10e92339a**"

        self.check_webhook(
            "comment_created_on_block",
            expected_topic_name,
            expected_message,
        )

    def test_comment_updated_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "page: 0ef104cd-477e-80e1-8571-cfd10e92339a"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** updated a comment on **0ef104cd-477e-80e1-8571-cfd10e92339a**"

        self.check_webhook(
            "comment_updated",
            expected_topic_name,
            expected_message,
        )

    def test_comment_deleted_with_map_pages_to_topics(self) -> None:
        self.url = self.build_webhook_url(map_pages_to_topics="true")
        expected_topic_name = "page: 0ef104cd-477e-80e1-8571-cfd10e92339a"
        expected_message = "**user: c7c11cca-1d73-471d-9b6e-bdef51470190** deleted a comment on **0ef104cd-477e-80e1-8571-cfd10e92339a**"

        self.check_webhook(
            "comment_deleted",
            expected_topic_name,
            expected_message,
        )
