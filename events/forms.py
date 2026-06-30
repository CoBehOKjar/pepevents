from django import forms
from .models import Event

class EventForm(forms.ModelForm):
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