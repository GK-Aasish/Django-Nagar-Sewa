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


class NoticeComment(models.Model):
    notice = models.ForeignKey(
        Notice,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notice_comments'
    )
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.notice}"
