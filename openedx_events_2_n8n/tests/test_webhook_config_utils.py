"""Tests for webhook configuration resolution."""

from django.core.cache import cache
from django.test import TestCase

from openedx_events_2_n8n.models import CACHE_KEY_TEMPLATE, WebhookConfig
from openedx_events_2_n8n.utils import get_webhook_config


class GetWebhookConfigTest(TestCase):
    """Tests for get_webhook_config."""

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)
        self.event_type = "org.openedx.learning.student.registration.completed.v1"
        self.fallback_url = "https://settings.example.com/webhook/registration"

    def test_returns_database_url_when_active_override_exists(self):
        """An active DB override should take precedence over settings."""
        WebhookConfig.objects.create(
            event=self.event_type,
            url="https://db.example.com/webhook/registration",
        )

        self.assertEqual(
            get_webhook_config(self.event_type, self.fallback_url)["url"],
            "https://db.example.com/webhook/registration",
        )

    def test_returns_settings_fallback_when_no_db_override_exists(self):
        """Without a DB row, settings should still drive the webhook URL."""
        config = get_webhook_config(self.event_type, self.fallback_url)

        self.assertEqual(config["url"], self.fallback_url)
        self.assertEqual(config["auth_type"], WebhookConfig.AuthType.NONE)

    def test_returns_settings_fallback_when_db_override_is_inactive(self):
        """Inactive DB rows should be ignored."""
        WebhookConfig.objects.create(
            event=self.event_type,
            url="https://db.example.com/webhook/registration",
            is_active=False,
        )

        self.assertEqual(
            get_webhook_config(self.event_type, self.fallback_url)["url"],
            self.fallback_url,
        )

    def test_returns_settings_fallback_when_db_url_is_blank(self):
        """Blank DB URLs should be treated as invalid and ignored."""
        WebhookConfig.objects.create(
            event=self.event_type,
            url="",
        )

        self.assertEqual(
            get_webhook_config(self.event_type, self.fallback_url)["url"],
            self.fallback_url,
        )

    def test_caches_empty_db_result_without_overriding_settings_fallback(self):
        """Cache should store the DB miss while preserving settings fallback."""
        cache_key = CACHE_KEY_TEMPLATE.format(event=self.event_type)

        self.assertEqual(
            get_webhook_config(self.event_type, self.fallback_url)["url"],
            self.fallback_url,
        )
        self.assertIsNone(cache.get(cache_key))

    def test_uses_cached_db_value_without_hitting_database(self):
        """A cached DB config should be reused directly on the next lookup."""
        cache_key = CACHE_KEY_TEMPLATE.format(event=self.event_type)
        cache.set(
            cache_key,
            {
                "url": "https://cached.example.com/webhook/registration",
                "auth_type": WebhookConfig.AuthType.NONE,
                "basic_auth_username": "",
                "basic_auth_password": "",
                "header_auth_name": "",
                "header_auth_value": "",
                "jwt_auth_secret": "",
            },
            300,
        )

        self.assertEqual(
            get_webhook_config(self.event_type, self.fallback_url)["url"],
            "https://cached.example.com/webhook/registration",
        )

    def test_returns_configured_auth_fields(self):
        """DB-configured auth fields should be included in the resolved config."""
        WebhookConfig.objects.create(
            event=self.event_type,
            url="https://db.example.com/webhook/registration",
            auth_type=WebhookConfig.AuthType.HEADER,
            header_auth_name="Authorization",
            header_auth_value="secret-token",
        )

        config = get_webhook_config(self.event_type, self.fallback_url)

        self.assertEqual(config["auth_type"], WebhookConfig.AuthType.HEADER)
        self.assertEqual(config["header_auth_name"], "Authorization")
        self.assertEqual(config["header_auth_value"], "secret-token")
