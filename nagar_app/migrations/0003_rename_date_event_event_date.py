# Generated migration for renaming Event.date to Event.event_date

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nagar_app', '0002_eventcategory_event_eventreaction_eventregistration_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='date',
            new_name='event_date',
        ),
    ]
