# Generated migration to add author field to Event model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nagar_app', '0003_rename_date_event_event_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='author',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='created_events',
                to=settings.AUTH_USER_MODEL
            ),
            preserve_default=False,
        ),
    ]
