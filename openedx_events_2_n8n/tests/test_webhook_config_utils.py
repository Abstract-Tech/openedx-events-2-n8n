"""Tests for webhook configuration URL resolution."""

from django.core.cache import cache
from django.test import TestCase

from openedx_events_2_n8n.models import CACHE_KEY_TEMPLATE, WebhookConfig
from openedx_events_2_n8n.utils import get_webhook_url


class GetWebhookUrlTest(TestCase):
    """Tests for get_webhook_url."""

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
            get_webhook_url(self.event_type, self.fallback_url),
            "https://db.example.com/webhook/registration",
        )

    def test_returns_settings_fallback_when_no_db_override_exists(self):
        """Without a DB row, settings should still drive the webhook URL."""
        self.assertEqual(
            get_webhook_url(self.event_type, self.fallback_url),
            self.fallback_url,
        )

    def test_returns_settings_fallback_when_db_override_is_inactive(self):
        """Inactive DB rows should be ignored."""
        WebhookConfig.objects.create(
            event=self.event_type,
            url="https://db.example.com/webhook/registration",
            is_active=False,
        )

        self.assertEqual(
            get_webhook_url(self.event_type, self.fallback_url),
            self.fallback_url,
        )

    def test_returns_settings_fallback_when_db_url_is_blank(self):
        """Blank DB URLs should be treated as invalid and ignored."""
        WebhookConfig.objects.create(
            event=self.event_type,
            url="",
        )

        self.assertEqual(
            get_webhook_url(self.event_type, self.fallback_url),
            self.fallback_url,
        )

    def test_caches_empty_db_result_without_overriding_settings_fallback(self):
        """Cache should store the DB miss while preserving settings fallback."""
        cache_key = CACHE_KEY_TEMPLATE.format(event=self.event_type)

        self.assertEqual(
            get_webhook_url(self.event_type, self.fallback_url),
            self.fallback_url,
        )
        self.assertEqual(cache.get(cache_key), "")

    def test_uses_cached_db_value_without_hitting_database(self):
        """A cached DB URL should be reused directly on the next lookup."""
        cache_key = CACHE_KEY_TEMPLATE.format(event=self.event_type)
        cache.set(cache_key, "https://cached.example.com/webhook/registration", 300)

        self.assertEqual(
            get_webhook_url(self.event_type, self.fallback_url),
            "https://cached.example.com/webhook/registration",
        )
