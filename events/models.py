from django.db import models
from django.db.models import Q
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
    CREATOR = "CREATOR", "Создатель"        #Full access to event
    SUPPORT = "SUPPORT", "Ст. Организатор"  #Full access without delete
    ORGANIZER = "ORGANIZER", "Организатор"  #Access to manage members
    PLAYER = "PLAYER", "Участник"


def _has_role(event, profile, roles):
    event_member = EventMember.objects.filter(event=event, profile=profile).first()

    if not event_member:
        return False

    return event_member.role in roles

class Event(models.Model):
    slug = models.SlugField(
        "Ссылка",
        unique=True,
        blank=True,
        help_text="Используется в URL для ссылки на страницу ивента. Например: peepo-hui",
    )

    name = models.CharField(
        "Название",
        max_length=100,
    )

    description = models.TextField(
        "Краткое описание",
        max_length=500,
        blank=True,
    )

    info = models.TextField(
        "Информация",
        max_length=20000,
        blank=True,
        help_text="Все подробности об ивенте",
    )

    rules = models.TextField(
        "Правила",
        max_length=40000,
        blank=True,
        help_text="Все правила ивента",
    )

    allow_team_creation = models.BooleanField(
        "Разрешить участникам создавать свои команды",
        default=True,
        help_text="Если нет - участники смогут присоедениться только к существующим командам",
    )

    start_datetime = models.DateTimeField(
        "Время начала ивента",
        blank=True,
        null=True,
    )

    end_datetime = models.DateTimeField(
        "Время окончания ивента",
        blank=True,
        null=True,
        help_text="Примерное или точное",
    )

    max_players = models.IntegerField(
        "Максимум участников",
        null=True,
        blank=True,
        help_text="Организаторы вне команд не учитываются"
    )

    max_teams = models.IntegerField(
        "Максимум команд",
        null=True,
        blank=True,
    )

    min_players_per_team = models.IntegerField(
        "Минимум участников в команде",
        null=True,
        blank=True,
    )

    max_players_per_team = models.IntegerField(
        "Максимум участников в команде",
        null=True,
        blank=True,
    )

    status = models.CharField(
        "Текущий статус ивента",
        max_length=20,
        choices=Statuses.choices,
        default=Statuses.WIP,
    )

    #Permissions check
    def can_delete(self, profile):
        return _has_role(self, profile, ["CREATOR"])

    def can_edit(self, profile):
        return _has_role(self, profile, ["CREATOR", "SUPPORT"])

    def can_manage(self, profile):
        return _has_role(self, profile, ["CREATOR", "SUPPORT", "ORGANIZER"])

    def can_join(self, profile):
        if self.can_manage(profile):
            return True
        return self.status not in ("ONGOING", "FINISHED")

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
        verbose_name="Ивент команды",
    )

    name = models.CharField(
        "Название команды",
        max_length=50,
    )

    color = models.CharField(
        "Цвет кманды",
        max_length=7,
        null=True,
        blank=True,
        help_text="Цвет в HEX: #ff0000",
    )

    max_players = models.IntegerField(
        "Максимум участников в команде",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.event.name} - {self.name}"


class EventMember(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name="Ивент участника",
    )

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="membership",
        verbose_name="Профиль участника",
    )

    minecraft_account = models.ForeignKey(
        MinecraftAccount,
        on_delete=models.CASCADE,
        verbose_name="Аккаунт участника",
    )

    role = models.CharField(
        "Роль участника",
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
        verbose_name="Команда участника",
    )

    joined_at = models.DateTimeField(
        "Время присоединения к ивенту",
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "profile"],
                name="unique_event_member",
            )
        ]

    def clean(self):
        if self.event.max_players:
            qs = self.event.members.all()
            qs = qs.exclude(Q(pk=self.pk) | (Q(team__isnull=True) & ~Q(role="PLAYER")))

            count = qs.count()

            if count >= self.event.max_players:
                raise ValidationError(
                    "В ивенте уже максимальное число участников!"
                )

        if self.team and self.team.event != self.event:
            raise ValidationError(
                "Команда должна принадлежать выбранному ивенту."
            )

        if self.team and self.team.max_players:
            qs = self.team.members.all()
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            count = qs.count()

            if count >= self.team.max_players:
                raise ValidationError(
                    "В команде уже максимальное число участников!"
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