"""
openedx_events_2_n8n Django application initialization.
"""

from django.apps import AppConfig


class OpenedxEvents2N8nConfig(AppConfig):
    """
    Configuration for the openedx_events_2_n8n Django application.
    """

    name = "openedx_events_2_n8n"

    plugin_app = {
        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
            "cms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
        },
    }

    def ready(self):
        """Perform initialization tasks required for the plugin."""
        from openedx_events_2_n8n import handlers  # pylint: disable=unused-import, import-outside-toplevel
