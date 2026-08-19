"""Django admin configuration for openedx_events_2_n8n."""

from django.contrib import admin

from openedx_events_2_n8n.models import WebhookConfig


@admin.register(WebhookConfig)
class WebhookConfigAdmin(admin.ModelAdmin):
    """Expose per-event webhook configuration to operators."""

    list_display = ("event", "event_value", "url", "auth_type", "is_active", "modified")
    list_filter = ("is_active", "auth_type")
    search_fields = ("event",)

    class Media:
        """Toggle auth credential fields based on the selected auth_type."""

        js = ("openedx_events_2_n8n/admin/webhookconfig.js",)

    fieldsets = (
        (None, {"fields": ("event", "url", "is_active")}),
        (
            "Authentication",
            {
                "fields": (
                    "auth_type",
                    "basic_auth_username",
                    "basic_auth_password",
                    "header_auth_name",
                    "header_auth_value",
                    "jwt_auth_secret",
                ),
                "description": "Fill in only the fields matching the selected auth type.",
            },
        ),
    )

    @admin.display(description="Event value")
    def event_value(self, obj):
        """Show the raw event_type string (list_display renders 'event' as its label)."""
        return obj.event
