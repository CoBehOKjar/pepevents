from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from events.models import Event, Team, EventMember
from users.models import Profile, MinecraftAccount


User = get_user_model()

# Helper funcs
def create_player(username):
    user = User.objects.create(username=username)
    profile = Profile.objects.filter(user=user).first()
    mc_acc = MinecraftAccount.objects.create(profile=profile, nickname=username)

    return profile, mc_acc

def create_member(event, team=None, role="PLAYER", username=None):
    username = username or f"player_{EventMember.objects.count()}"
    profile, mc_acc = create_player(username)
    return EventMember.objects.create(event=event, profile=profile, minecraft_account=mc_acc, team=team, role=role)


# Models Tests
class EventTests(TestCase):
    def test_slug_is_generated_from_name(self):
        event = Event.objects.create(
            name="Хайповый ивент"
        )
        self.assertEqual(event.slug, "khaipovyi-ivent")

    def test_slug_rejects_invalid_characters(self):
        invalid_slugs = ["ру с пробелом", "with space", "w!th@symb()l", "with/slash"]
        for slug in invalid_slugs:
            with self.subTest(slug=slug):
                event = Event(name="Test", slug=slug)
                with self.assertRaises(ValidationError):
                    event.full_clean()


class EventModelTests(TestCase):
    def setUp(self):
        self.event1 = Event.objects.create(
            name="Event1"
        )
        self.event2 = Event.objects.create(
            name="Event2"
        )
        self.event1Team = Team.objects.create(
            event=self.event1,
            name="Team1"
        )


    def test_join_to_team_from_other_event(self):
        with self.assertRaises(ValidationError):
            create_member(self.event2, team=self.event1Team)

    def test_organizer_role_cant_edit_event(self):
        member = create_member(event=self.event1, role="ORGANIZER")

        self.assertFalse(self.event1.can_edit(member.profile))
        self.assertTrue(self.event1.can_manage(member.profile))


class EventMemberTeamLimitTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            name="Event",
        )
        self.team = Team.objects.create(
            event=self.event,
            name="Team1",
            max_players=2
        )


    def test_cannot_join_team_over_limit(self):
        create_member(self.event, self.team)
        create_member(self.event, self.team)

        with self.assertRaises(ValidationError):
            create_member(self.event, self.team)

    def test_moving_member_to_full_team_still_raises(self):
        create_member(self.event, self.team)
        create_member(self.event, self.team)

        team2 = Team.objects.create(
            event=self.event,
            name="Team2",
            max_players=2
        )
        member = create_member(self.event, team2)

        with self.assertRaises(ValidationError):
            member.team = self.team
            member.save()


class EventMemberEventLimitTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            name="Event",
            max_players=2,
        )


    def test_join_to_full_event_where_organizer_without_team(self):
        create_member(self.event, role="ORGANIZER")
        create_member(self.event)

        create_member(self.event)
        self.assertTrue(self.event.members.count()==3)

    # In theory it shouldnt break, but let it be
    def test_join_to_full_event_with_organizer_without_team(self):
        create_member(self.event, role="ORGANIZER")
        create_member(self.event)
        create_member(self.event)

        with self.assertRaises(ValidationError):
            create_member(self.event)


class EventMemberEventStatusTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            name="Event",
        )



# View tests
class EventPageJoinTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.event = Event.objects.create(
            name="Event",
        )
        self.team = Team.objects.create(
            event=self.event,
            name="Team"
        )


    def test_cannot_join_when_event_ongoing_or_finished(self):
        for status in ("ONGOING", "FINISHED"):
            with self.subTest(status=status):
                profile, mc_acc = create_player(f"user_{status}")
                self.client.force_login(profile.user)
                self.event.status = status
                self.event.save()

                url = reverse("event_page", args=[self.event.slug])
                response = self.client.post(url,{
                    "action_join": self.team.id,
                    "minecraft_account": mc_acc.id,
                })
                self.assertFalse(EventMember.objects.filter(event=self.event, profile=profile).exists())

    def test_can_join_when_event_wip_recruitment_ready(self):
        for status in ("WIP", "RECRUITMENT", "READY"):
            with self.subTest(status=status):
                profile, mc_acc = create_player(f"user_{status}")
                self.client.force_login(profile.user)
                self.event.status = status
                self.event.save()

                url = reverse("event_page", args=[self.event.slug])
                response = self.client.post(url,{
                    "action_join": self.team.id,
                    "minecraft_account": mc_acc.id,
                })
                self.assertTrue(EventMember.objects.filter(event=self.event, profile=profile).exists())


class EventPageManageTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.event = Event.objects.create(
            name="Event",
        )
        self.team = Team.objects.create(
            event=self.event,
            name="Team"
        )

        self.creator = create_member(self.event, self.team, "CREATOR", "creator")
        self.player = create_member(self.event)

    def test_regular_player_cannot_kick_member(self):
        self.client.force_login(self.player.profile.user)

        url = reverse("event_page", args=[self.event.slug])
        response = self.client.post(url, {
            "member_id": self.creator.id,
            "action_kick": "",
        })

        self.assertTrue(EventMember.objects.filter(pk=self.creator.pk).exists())

    def test_creator_can_kick_player(self):
        self.client.force_login(self.creator.profile.user)

        url = reverse("event_page", args=[self.event.slug])
        response = self.client.post(url, {
            "member_id": self.player.id,
            "action_kick": "",
        })

        self.assertFalse(EventMember.objects.filter(pk=self.player.pk).exists())


    def test_creator_cannot_kick_self(self):
        self.client.force_login(self.creator.profile.user)

        url = reverse("event_page", args=[self.event.slug])
        response = self.client.post(url, {
            "member_id": self.creator.id,
            "action_kick": "",
        })

        messages_list = list(response.wsgi_request._messages)
        self.assertTrue(any("Нельзя кикнуть самого себя" in str(m) for m in messages_list))
        self.assertTrue(EventMember.objects.filter(pk=self.creator.pk).exists())