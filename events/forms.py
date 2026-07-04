from django import forms
from django.forms.models import inlineformset_factory

from .models import Event, MinecraftAccount, Team

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