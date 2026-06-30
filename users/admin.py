from django.contrib import admin

from .models import Profile, MinecraftAccount


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "display_name",
        "discord_id",
    )

    search_fields = (
        "username",
        "display_name",
        "discord_id",
    )


@admin.register(MinecraftAccount)
class MinecraftAccountAdmin(admin.ModelAdmin):
    list_display = (
        "nickname",
        "profile",
        "uuid",
    )