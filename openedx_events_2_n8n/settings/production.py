"""
Production Django settings for openedx_events_2_n8n project.
"""


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open edX platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.N8N_REGISTRATION_WEBHOOK = getattr(settings, "ENV_TOKENS", {}).get(
        "N8N_REGISTRATION_WEBHOOK", settings.N8N_REGISTRATION_WEBHOOK
    )
    settings.N8N_ENROLLMENT_WEBHOOK = getattr(settings, "ENV_TOKENS", {}).get(
        "N8N_ENROLLMENT_WEBHOOK", settings.N8N_ENROLLMENT_WEBHOOK
    )
    settings.N8N_PERSISTENT_GRADE_COURSE_WEBHOOK = getattr(
        settings, "ENV_TOKENS", {}
    ).get(
        "N8N_PERSISTENT_GRADE_COURSE_WEBHOOK",
        settings.N8N_PERSISTENT_GRADE_COURSE_WEBHOOK,
    )
