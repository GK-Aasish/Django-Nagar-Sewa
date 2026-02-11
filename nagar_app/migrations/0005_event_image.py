# Generated migration to add image field to Event model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nagar_app', '0004_event_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='event_images/'),
        ),
    ]
