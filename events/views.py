from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Event, EventMember
from .forms import EventForm


def event_list(request):
    events = Event.objects.all()

    return render(
        request,
        "events/events.html",
        {
            "events": events,
        },
    )

def event_page(request, slug):
    event = get_object_or_404(Event, slug=slug)

    return render(
        request,
        "events/event_page.html",
        {
            "event": event,
        }
    )

@login_required
def new_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, profile=request.user.profile)

        if form.is_valid():
            minecraft_account = form.cleaned_data["minecraft_account"]
            event = form.save()
            EventMember.objects.create(
                event=event,
                profile=request.user.profile,
                role="CREATOR",
                minecraft_account=minecraft_account,
            )

            return redirect("event_page", slug=event.slug)

    else:
        form = EventForm(
            profile=request.user.profile,
        )

    return render(
        request,
        "events/new_event.html",
        {"form": form}
    )

@login_required
def edit_event(request, slug):
    instance = get_object_or_404(Event, slug=slug)
    if request.method == "POST":
        form = EventForm(request.POST or None, instance=instance)
        event = None

        if form.is_valid():
            event = form.save()

            return redirect("event_page", slug=event.slug)

    else:
        form = EventForm()

    return render(
        request,
        "events/new_event.html",
        {"form": form}
    )