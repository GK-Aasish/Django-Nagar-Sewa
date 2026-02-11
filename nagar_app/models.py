from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class NoticeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Notice(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        NoticeCategory,
        on_delete=models.PROTECT,
        related_name='notices'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posted_notices'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ReactionType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class NoticeReaction(models.Model):
    notice = models.ForeignKey(
        Notice,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notice_reactions'
    )
    reaction_type = models.ForeignKey(
        ReactionType,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('notice', 'user')

    def __str__(self):
        return f"{self.user} reacted {self.reaction_type} on {self.notice}"


class EventCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.PROTECT,
        related_name='events'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_events'
    )
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

    def __str__(self):
        return self.title


class EventReaction(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_reactions'
    )
    reaction_type = models.ForeignKey(
        ReactionType,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user} reacted {self.reaction_type} on {self.event}"


class EventRegistration(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_registrations'
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user} registered for {self.event}"


class Meeting(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    meeting_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_meetings'
    )

    def __str__(self):
        return self.title


class MeetingDocument(models.Model):
    DOCUMENT_TYPES = (
        ('minutes', 'Minutes'),
        ('agenda', 'Agenda'),
        ('report', 'Report'),
        ('attendance', 'Attendance'),
        ('presentation', 'Presentation'),
        ('budget', 'Budget'),
        ('other', 'Other'),
    )

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='meeting_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_documents'
    )

    def __str__(self):
        return f"{self.meeting} - {self.document_type}"
