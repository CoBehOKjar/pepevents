from django.contrib import admin

from .models import Event, EventMember, Team


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "name",
        "description",
        "start_datetime",
        "end_datetime",
        "max_players",
    )

    search_fields = (
        "slug",
        "name",
        "description",
    )

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "event",
        "name",
        "color",
        "max_players",
    )

    search_fields = (
        "event",
        "name",
        "color",
    )

@admin.register(EventMember)
class EventMemberAdmin(admin.ModelAdmin):
    list_display = (
        "event",
        "profile",
        "minecraft_account",
        "role",
        "team",
        "joined_at",
    )

    search_fields = (
        "event",
        "profile",
        "minecraft_account",
    )
