"""Initial migration for admin-configurable webhook URLs."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Create the WebhookConfig model."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="WebhookConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "event",
                    models.CharField(
                        db_index=True,
                        help_text=(
                            "The openedx-events event_type this webhook applies to, e.g. "
                            "org.openedx.learning.student.registration.completed.v1"
                        ),
                        max_length=255,
                        unique=True,
                    ),
                ),
                ("url", models.URLField()),
                ("is_active", models.BooleanField(default=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
