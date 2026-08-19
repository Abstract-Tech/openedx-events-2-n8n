"""Database models for openedx_events_2_n8n."""

from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

CACHE_KEY_TEMPLATE = "openedx_events_2_n8n:webhook_url:{event}"


class WebhookConfig(models.Model):
    """Admin-configurable webhook URL for an openedx-events event type."""

    class Events(models.TextChoices):
        """List of openedx-events event types that can be configured."""

        STUDENT_REGISTRATION_COMPLETED = (
            "org.openedx.learning.student.registration.completed.v1",
            "Student registration completed",
        )
        COURSE_ENROLLMENT_CREATED = (
            "org.openedx.learning.course.enrollment.created.v1",
            "Student enrollment created",
        )
        PERSISTENT_GRADE_SUMMARY_CHANGED = (
            "org.openedx.learning.course.persistent_grade_summary.changed.v1",
            "Persistent grade summary changed",
        )

    event = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text=(
            "The openedx-events event_type this webhook applies to, e.g."
        ),
        choices=Events.choices,
    )
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event} -> {self.url}"


@receiver(pre_save, sender=WebhookConfig)
def invalidate_old_event_cache(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Clear the cache for the previous event when a row is repointed."""
    if not instance.pk:
        return
    try:
        old_event = WebhookConfig.objects.get(pk=instance.pk).event
    except WebhookConfig.DoesNotExist:
        return
    if old_event != instance.event:
        cache.delete(CACHE_KEY_TEMPLATE.format(event=old_event))


@receiver(post_save, sender=WebhookConfig)
def invalidate_cache_on_save(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Clear the cached URL for this event after create/update."""
    cache.delete(CACHE_KEY_TEMPLATE.format(event=instance.event))


@receiver(post_delete, sender=WebhookConfig)
def invalidate_cache_on_delete(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Clear the cached URL for this event after delete."""
    cache.delete(CACHE_KEY_TEMPLATE.format(event=instance.event))
