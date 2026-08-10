"""Django admin configuration for openedx_events_2_n8n."""

from django.contrib import admin

from openedx_events_2_n8n.models import WebhookConfig


@admin.register(WebhookConfig)
class WebhookConfigAdmin(admin.ModelAdmin):
    """Expose per-event webhook configuration to operators."""

    list_display = ("event", "url", "is_active", "modified")
    list_filter = ("is_active",)
    search_fields = ("event",)
