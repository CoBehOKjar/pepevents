from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    discord_id = models.BigIntegerField(unique=True)

    username = models.CharField(max_length=32)

    global_name = models.CharField(
        max_length=32,
        blank=True,
    )

    avatar = models.URLField(blank=True)

    minecraft_nick = models.CharField(
        max_length=16,
        blank=True,
    )

    is_organizer = models.BooleanField(default=False)

    def __str__(self):
        return self.username