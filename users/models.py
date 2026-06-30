from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    discord_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
    )

    username = models.CharField(
        max_length=32,
        unique=True,
    )

    display_name = models.CharField(
        max_length=32,
        blank=True,
    )

    avatar = models.URLField(blank=True)

    def __str__(self):
        return self.username


class MinecraftAccount(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="minecraft_accounts",
    )

    uuid = models.UUIDField(
        unique=True,
        null=True,
        blank=True,
    )

    nickname = models.CharField(max_length=16)

    skin_avatar = models.URLField(blank=True)

    def __str__(self):
        return f"{self.nickname} ({self.profile.username})"