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
        with self.assertRaises(ValidationError):
            Event.objects.create(
                name="Не очень хайповый ивент",
                slug="очень/c@-@l event_1o1!"
            ).full_clean()


class EventModelTests(TestCase):
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

        self.event1Team = Team.objects.create(
            event=self.event1,
            name="Team1"
        )

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