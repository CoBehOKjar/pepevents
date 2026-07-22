from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from events.models import Event, Team, EventMember
from users.models import Profile, MinecraftAccount

User = get_user_model()

class EventTests(TestCase):
    def test_slug_is_generated_from_name(self):
        event = Event.objects.create(
            name="Хайповый ивент"
        )

        self.assertEqual(event.slug, "khaipovyi-ivent")

    def test_slug_can_contain_only_a_z_0_9_minus_dash(self):
        event = Event(name="Не очень хайповый ивент", slug="очень/c@-@l event_1o1!")
        with self.assertRaises(ValidationError):
            event.full_clean()


class EventModelTests(TestCase):
    def _create_member(self, i, event, team):
        user = User.objects.create(username=f"player{i}")
        profile = Profile.objects.filter(user=user).first()
        mc_acc = MinecraftAccount.objects.create(profile=profile, nickname=f"nick{i}")
        EventMember.objects.create(event=event, profile=profile, minecraft_account=mc_acc, team=team)


    def setUp(self):
        self.user = User.objects.create(username="Cobehok", password="123")
        self.profile = Profile.objects.filter(user=self.user).first()
        self.minecraft_account = MinecraftAccount.objects.create(
            profile=self.profile,
            nickname="CoBeHok"
        )

        self.event1 = Event.objects.create(
            name="Event1"
        )
        self.event2 = Event.objects.create(
            name="Event2"
        )

        self.event3 = Event.objects.create(
            name="Event3"
        )

        self.event1Team = Team.objects.create(
            event=self.event1,
            name="Team1"
        )

        self.event3Team = Team.objects.create(
            event=self.event3,
            name="Team1",
            max_players=2,
        )

        self.event3Team2 = Team.objects.create(
            event=self.event3,
            name="Team2",
            max_players=2,
        )

        for i in range(2):
            self._create_member(i, self.event3, self.event3Team)

    def test_join_to_team_from_other_event(self):
        with self.assertRaises(ValidationError):
            EventMember.objects.create(
                event=self.event2,
                profile=self.profile,
                minecraft_account=self.minecraft_account,
                team=self.event1Team
            )

    def test_organizer_role_cant_edit_event(self):
        member = EventMember.objects.create(
                event=self.event1,
                profile=self.profile,
                minecraft_account=self.minecraft_account,
                team=self.event1Team,
                role="ORGANIZER",
            )

        self.assertFalse(self.event1.can_edit(self.profile))
        self.assertTrue(self.event1.can_manage(self.profile))

    def test_cannot_join_team_over_limit(self):
        user3 = User.objects.create(username="player3")
        profile3 = Profile.objects.filter(user=user3).first()
        mc_acc3 = MinecraftAccount.objects.create(profile=profile3, nickname="nick3")

        with self.assertRaises(ValidationError):
            EventMember.objects.create(event=self.event3, profile=profile3, minecraft_account=mc_acc3, team=self.event3Team)

    def test_moving_full_member_to_another_full_team_still_raises(self):
        user4 = User.objects.create(username="player4")
        profile4 = Profile.objects.filter(user=user4).first()
        mc_acc4 = MinecraftAccount.objects.create(profile=profile4, nickname="nick4")
        member = EventMember.objects.create(event=self.event3, profile=profile4, minecraft_account=mc_acc4, team=self.event3Team2)

        with self.assertRaises(ValidationError):
            member.team = self.event3Team
            member.save()