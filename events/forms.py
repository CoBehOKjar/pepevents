from django import forms
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError

from .models import Event, MinecraftAccount, Team

class EventJoinForm(forms.Form):
    minecraft_account = forms.ModelChoiceField(
        queryset=MinecraftAccount.objects.none(),
        label="Твой Minecraft аккаунт"
    )

    def __init__(self, *args, profile=None, event=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event

        if profile:
            self.fields["minecraft_account"].queryset = profile.minecraft_accounts.all()

        if event and event.allow_team_creation:
            self.fields["team_name"] = forms.CharField(
                label="Название новой команды",
                max_length=100,
                required=False,
            )
            self.fields["team_color"] = forms.CharField(
                label="Цвет (HEX)",
                max_length=7,
                required=False,
            )
            self.fields["team_max_players"] = forms.IntegerField(
                label="Максимум игроков в команде",
                required=False,
            )

    def clean(self):
        cleaned_data = super().clean()

        team_name = cleaned_data.get("team_name")
        team_color = cleaned_data.get("team_color")
        team_max_players = cleaned_data.get("team_max_players")

        if self.event and self.event.allow_team_creation and team_name:
            if Team.objects.filter(event=self.event, name=team_name).exists():
                self.add_error("team_name", "Команда с таким названием уже существует на этом ивенте.")

            if team_color and Team.objects.filter(event=self.event, color=team_color).exists():
                self.add_error("team_color", "Этот цвет уже занят другой командой.")

            if team_max_players and team_max_players > self.event.max_players_per_team:
                self.add_error("team_max_players", "Превышен лимит игроков на ивенте.")

        return cleaned_data


class EventForm(forms.ModelForm):
    minecraft_account = forms.ModelChoiceField(
        queryset=MinecraftAccount.objects.none()
    )

    class Meta:
        model = Event
        fields = [
            "name",
            "slug",
            "description",
            "info",
            "rules",
            "start_datetime",
            "end_datetime",
            "max_players",
            "max_teams",
            "max_players_per_team",
            "allow_team_creation",
            "status"
        ]

        widgets = {
            "start_datetime": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "end_datetime": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
        }

    def __init__(self, *args, profile=None, **kwargs):
        super().__init__(*args, **kwargs)

        if profile:
            self.fields["minecraft_account"].queryset = (
                profile.minecraft_accounts.all()
            )


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            "name",
            "color",
            "max_players",
        ]

TeamFormSet = inlineformset_factory(
    Event,
    Team,
    form=TeamForm,
    extra=1,
    can_delete=True,
)