from django.contrib.auth.decorators import login_required
from django.db.models import Model
from django.shortcuts import render, redirect, get_object_or_404
from .models import Event


def event_list(request):
    events = Event.objects.all()

    return render(
        request,
        "events/events.html",
        {
            "events": events,
        },
    )

def new_event(request):
    pass

def event_page(request, slug):
    event = get_object_or_404(Event, slug=slug)

    return render(
        request,
        "events/event_page.html",
        {
            "event": event,
        }
    )