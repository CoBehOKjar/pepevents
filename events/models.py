from django.db import models
from django.core.exceptions import ValidationError
from slugify import slugify
from users.models import Profile, MinecraftAccount


class Statuses(models.TextChoices):
    WIP = "WIP", "Строится"
    RECRUITMENT = "RECRUITMENT", "Набор"
    READY = "READY", "Готов"
    ONGOING = "ONGOING", "Проводится"
    FINISHED = "FINISHED", "Завершён"

class Roles(models.TextChoices):
    CREATOR = "CREATOR", "Создатель"
    ORGANIZER = "ORGANIZER", "Организатор"
    PLAYER = "PLAYER", "Участник"


class Event(models.Model):
    slug = models.SlugField(
        unique=True,
        blank=True,
    )

    name = models.CharField(
        max_length=100,
        blank=True,
    )

    description = models.TextField(
        max_length=500,
        blank=True,
    )

    info = models.TextField(
        max_length=20000,
        blank=True,
    )

    rules = models.TextField(
        max_length=40000,
        blank=True,
    )

    start_datetime = models.DateTimeField(blank=True, null=True)

    end_datetime = models.DateTimeField(blank=True, null=True)

    max_players = models.IntegerField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Statuses.choices,
        default=Statuses.WIP,
    )

    def save(self, *args, **kwargs):
        if self.slug == "":
            self.slug = slugify(self.name)

        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Team(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="teams",
    )

    name = models.CharField(max_length=50)

    color = models.CharField(
        max_length=7,
        help_text="HEX color #ff0000",
    )

    max_players = models.IntegerField()

    def __str__(self):
        return f"{self.event.name} - {self.name}"


class EventMember(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="members",
    )

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="membership"
    )

    minecraft_account = models.ForeignKey(
        MinecraftAccount,
        on_delete=models.CASCADE,
    )

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.PLAYER,
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        related_name="members",
        null=True,
        blank=True,
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "profile"],
                name="unique_event_member",
            )
        ]

    def clean(self):
        if self.team and self.team.event != self.event:
            raise ValidationError(
                "Команда должна принадлежать выбранному ивенту."
            )

        if self.minecraft_account.profile != self.profile:
            raise ValidationError(
                "Minecraft-аккаунт должен принадлежать выбранному профилю."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.minecraft_account.nickname} ({self.profile.username}) - {self.event.name}"