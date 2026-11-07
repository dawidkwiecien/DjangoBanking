import django.utils.timezone
from django.db import migrations, models


def mark_existing_settled(apps, schema_editor):
    Transfer = apps.get_model("banking", "Transfer")
    Transfer.objects.filter(status="completed", settled_at__isnull=True).update(
        settled_at=django.utils.timezone.now()
    )


class Migration(migrations.Migration):

    dependencies = [
        ("banking", "0003_transfer"),
    ]

    operations = [
        migrations.AddField(
            model_name="transfer",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("processing", "Processing"),
                    ("completed", "Completed"),
                    ("rejected", "Rejected"),
                ],
                default="completed",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="transfer",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="transfer",
            name="processing_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="transfer",
            name="realize_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="transfer",
            name="settled_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(mark_existing_settled, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="transfer",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("processing", "Processing"),
                    ("completed", "Completed"),
                    ("rejected", "Rejected"),
                ],
                default="pending",
                max_length=16,
            ),
        ),
    ]
