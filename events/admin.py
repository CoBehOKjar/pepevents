from django.contrib import admin

from .models import Event

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
