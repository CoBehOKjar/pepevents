from django import forms
from .models import Event, MinecraftAccount

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
        ]

    def __init__(self, *args, profile=None, **kwargs):
        super().__init__(*args, **kwargs)

        if profile:
            self.fields["minecraft_account"].queryset = (
                profile.minecraft_accounts.all()
            )