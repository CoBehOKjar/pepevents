from os import name

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .models import Event, EventMember, Team, Roles
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

    current_member = None
    can_edit = False
    can_manage = False
    if request.user.is_authenticated:
        current_member = event.members.filter(profile=request.user.profile).first()
        can_edit = event.can_edit(request.user.profile)
        can_manage = event.can_manage(request.user.profile)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        account_id = request.POST.get("minecraft_account")
        minecraft_account = None
        if account_id:
            minecraft_account = request.user.profile.minecraft_accounts.filter(id=account_id).first()

        if can_manage:
            print("can_manage")
            member_id = request.POST.get("member_id")

            if member_id:
                print("has member_id")
                target_member = get_object_or_404(EventMember, id=member_id, event=event)

                #Creator edit protect
                if target_member.role == "CREATOR" and current_member.role != "CREATOR":
                    messages.error(request, "Только создатель может редактировать создателя!")
                    return redirect("event_page", slug=event.slug)

                if "action_role" in request.POST:
                    new_role = request.POST.get("new_role")
                    if new_role in dict(Roles.choices):
                        target_member.role = new_role
                        target_member.save()
                        messages.success(request, f"Роль {target_member.minecraft_account.nickname} изменена.")

                elif "action_team" in request.POST:
                    new_team_id = request.POST.get("new_team")
                    if new_team_id == "none":
                        target_member.team = None
                        target_member.save()
                        messages.success(request, f"{target_member.minecraft_account.nickname} исключён из команды.")
                    else:
                        target_team = get_object_or_404(Team, id=new_team_id, event=event)
                        if target_team.max_players is None or target_team.members.count() < target_team.max_players:
                            target_member.team = target_team
                            target_member.save()
                            messages.success(request, f"Участник переведён в {target_team.name}.")
                        else:
                            messages.error(request, "В этой команде нет мест!")

                elif "action_kick" in request.POST:
                    if target_member == current_member:
                        messages.error(request, "Нельзя кикнуть самого себя!")
                    else:
                        target_member.delete()
                        messages.success(request, f"{target_member.minecraft_account.nickname} кикнут с ивента.")

                return redirect("event_page", slug=event.slug)

        if "action_leave" in request.POST:
            if current_member:
                current_member.delete()
                messages.success(request, "Ты вышел из ивента.")
            return redirect("event_page", slug=event.slug)

        elif "action_join" in request.POST:
            team_id = request.POST.get("action_join")
            team = event.teams.get(id=team_id)

            if not account_id:
                messages.error(request, "Необходимо выбрать Minecraft аккаунт для  участия!")
                return redirect("event_page", slug=event.slug)

            if team.max_players is None or team.members.count() < team.max_players:
                if current_member:
                    current_member.minecraft_account = minecraft_account
                    current_member.team = team
                    current_member.save()
                else:
                    EventMember.objects.create(
                        event=event,
                        profile=request.user.profile,
                        role="PLAYER",
                        minecraft_account=minecraft_account,
                        team=team,
                    )
                messages.success(request, f"Ты присоединился к команде {team.name}")
            else:
                messages.error(request, "Команда уже заполнена!")

            return redirect("event_page", slug=event.slug)

        elif "action_create" in request.POST:
            team_name = request.POST.get("new_team_name")
            team_color = request.POST.get("new_team_color")
            team_max = request.POST.get("new_team_max_players")

            if not account_id:
                messages.error(request, "Необходимо выбрать Minecraft аккаунт!")
                return redirect("event_page", slug=event.slug)

            if not team_name or not team_name.strip():
                messages.error(request, "Название команды не может быть пустым!")
                return redirect("event_page", slug=event.slug)

            new_team = Team.objects.create(
                event=event,
                name=team_name,
                color=team_color,
                max_players=team_max or None
            )

            if current_member:
                current_member.minecraft_account = minecraft_account
                current_member.team = new_team
                current_member.save()
            else:
                EventMember.objects.create(
                    event=event,
                    profile=request.user.profile,
                    role="PLAYER",
                    minecraft_account=minecraft_account,
                    team=new_team,
                )

            messages.success(request, f"Команда {new_team.name} создана, ты автоматически вступил в неё!")
            return redirect("event_page", slug=event.slug)

    return render(
        request,
        "events/event_page.html",
        {
            "event": event,
            "current_member": current_member,
            "can_edit": can_edit,
            "can_manage": can_manage,
            "roles": Roles.choices,
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

    if not instance.can_edit(request.user.profile):
        messages.error(request, "У тебя нет прав на редактирование этого ивента!")
        return redirect("event_page", slug=instance.slug)

    if request.method == "POST":
        event_form = EventForm(request.POST or None, instance=instance, profile=request.user.profile)
        team_formset = TeamFormSet(request.POST, instance=instance)

        if event_form.is_valid() and team_formset.is_valid():
            event = event_form.save()
            team_formset.save()

            messages.success(request, "Ивент успешно обновлен!")
            return redirect("event_page", slug=event.slug)

    else:
        event_form = EventForm(
            instance=instance,
            profile=request.user.profile,
        )
        team_formset = TeamFormSet(instance=instance)

    return render(
        request,
        "events/new_or_edit_event.html",
        {"event_form": event_form, "team_formset": team_formset}
    )