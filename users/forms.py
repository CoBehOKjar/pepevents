from django import forms
from .models import MinecraftAccount

class MinecraftAccountForm(forms.ModelForm):
    class Meta:
        model = MinecraftAccount
        fields = ["nickname"]