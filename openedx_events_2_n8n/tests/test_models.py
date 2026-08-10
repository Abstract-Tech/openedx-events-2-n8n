"""Tests for the openedx_events_2_n8n models module."""

from django.core.cache import cache
from django.db import IntegrityError
from django.test import TestCase

from openedx_events_2_n8n.models import CACHE_KEY_TEMPLATE, WebhookConfig


class WebhookConfigTest(TestCase):
    """Tests for the WebhookConfig model and cache invalidation signals."""

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)

    def test_str(self):
        """The string representation should include the event and URL."""
        config = WebhookConfig.objects.create(
            event="org.openedx.learning.student.registration.completed.v1",
            url="https://n8n.example.com/webhook/registration",
        )

        self.assertEqual(
            str(config),
            "org.openedx.learning.student.registration.completed.v1 -> "
            "https://n8n.example.com/webhook/registration",
        )

    def test_is_active_defaults_to_true(self):
        """Rows should default to active."""
        config = WebhookConfig.objects.create(
            event="some.event",
            url="https://n8n.example.com/webhook/x",
        )

        self.assertTrue(config.is_active)

    def test_event_is_unique(self):
        """Only one row per event should be allowed."""
        WebhookConfig.objects.create(
            event="some.event",
            url="https://n8n.example.com/webhook/a",
        )

        with self.assertRaises(IntegrityError):
            WebhookConfig.objects.create(
                event="some.event",
                url="https://n8n.example.com/webhook/b",
            )

    def test_save_invalidates_cache_for_its_event(self):
        """Saving a row should clear any cached value for its event."""
        cache_key = CACHE_KEY_TEMPLATE.format(event="some.event")
        cache.set(cache_key, "https://stale.example.com", timeout=300)

        WebhookConfig.objects.create(
            event="some.event",
            url="https://n8n.example.com/webhook/a",
        )

        self.assertIsNone(cache.get(cache_key))

    def test_delete_invalidates_cache_for_its_event(self):
        """Deleting a row should clear any cached value for its event."""
        config = WebhookConfig.objects.create(
            event="some.event",
            url="https://n8n.example.com/webhook/a",
        )
        cache_key = CACHE_KEY_TEMPLATE.format(event="some.event")
        cache.set(cache_key, "https://n8n.example.com/webhook/a", timeout=300)

        config.delete()

        self.assertIsNone(cache.get(cache_key))

    def test_renaming_event_invalidates_old_event_cache(self):
        """Changing the event should invalidate the old event cache key too."""
        config = WebhookConfig.objects.create(
            event="old.event",
            url="https://n8n.example.com/webhook/a",
        )
        old_cache_key = CACHE_KEY_TEMPLATE.format(event="old.event")
        cache.set(old_cache_key, "https://n8n.example.com/webhook/a", timeout=300)

        config.event = "new.event"
        config.save()

        self.assertIsNone(cache.get(old_cache_key))
