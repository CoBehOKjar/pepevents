from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Аккаунт",
    )

    discord_id = models.BigIntegerField(
        "Discord ID",
        unique=True,
        null=True,
        blank=True,
    )

    username = models.CharField(
        "Имя пользователя",
        max_length=32,
        unique=True,
    )

    display_name = models.CharField(
        "Отображаемое имя",
        max_length=32,
        blank=True,
    )

    avatar = models.URLField(
        "Аватарка",
        blank=True
    )

    def __str__(self):
        return self.username


class MinecraftAccount(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="minecraft_accounts",
        verbose_name="Профиль",
    )

    uuid = models.UUIDField(
        "UUID аккаунта",
        unique=True,
        null=True,
        blank=True,
    )

    nickname = models.CharField(
        "Ник",
        max_length=16,
    )

    skin_avatar = models.URLField(
        "Аватарка скина",
        blank=True,
    )

    def __str__(self):
        return f"{self.nickname} ({self.profile.username})"