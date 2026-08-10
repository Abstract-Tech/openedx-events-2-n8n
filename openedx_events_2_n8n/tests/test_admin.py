"""Tests for the openedx_events_2_n8n admin registration."""

from django.contrib import admin
from django.test import TestCase

from openedx_events_2_n8n.models import WebhookConfig


class WebhookConfigAdminTest(TestCase):
    """Tests for the WebhookConfig admin registration."""

    def test_webhook_config_is_registered(self):
        """WebhookConfig should be registered in Django admin."""
        self.assertIn(WebhookConfig, admin.site._registry)  # pylint: disable=protected-access

    def test_list_display_shows_operator_relevant_fields(self):
        """The admin list view should show the fields operators need."""
        model_admin = admin.site._registry[WebhookConfig]  # pylint: disable=protected-access

        self.assertEqual(
            model_admin.list_display,
            ("event", "url", "is_active", "modified"),
        )
