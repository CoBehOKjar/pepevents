from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Event, EventMember
from .forms import EventForm, TeamFormSet


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
    event = get_object_or_404(
        Event.objects.prefetch_related(
            "teams__members__minecraft_account"
        ),
        slug=slug
    )

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
        event_form = EventForm(request.POST, profile=request.user.profile)
        team_formset = TeamFormSet(request.POST, instance=Event())

        if event_form.is_valid() and team_formset.is_valid():
            event = event_form.save()

            team_formset.instance = event
            team_formset.save()

            minecraft_account = event_form.cleaned_data["minecraft_account"]

            EventMember.objects.create(
                event=event,
                profile=request.user.profile,
                role="CREATOR",
                minecraft_account=minecraft_account,
            )

            return redirect("event_page", slug=event.slug)

    else:
        event_form = EventForm(
            profile=request.user.profile,
        )
        team_formset = TeamFormSet(instance=Event())

    return render(
        request,
        "events/new_or_edit_event.html",
        {"event_form": event_form, "team_formset": team_formset}
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
        "events/new_or_edit_event.html",
        {"form": form}
    )