"""Django admin configuration for openedx_events_2_n8n."""

from django.contrib import admin

from openedx_events_2_n8n.models import WebhookConfig


@admin.register(WebhookConfig)
class WebhookConfigAdmin(admin.ModelAdmin):
    """Expose per-event webhook configuration to operators."""

    list_display = ("event", "event_value", "url", "is_active", "modified")
    list_filter = ("is_active",)
    search_fields = ("event",)

    @admin.display(description="Event value")
    def event_value(self, obj):
        """Show the raw event_type string (list_display renders 'event' as its label)."""
        return obj.event
