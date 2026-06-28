from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import Profile


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        data = sociallogin.account.extra_data

        avatar = ""

        if data.get("avatar"):
            avatar = (
                f"https://cdn.discordapp.com/avatars/"
                f"{data['id']}/{data['avatar']}.png"
            )

        Profile.objects.update_or_create(
            user=user,
            defaults={
                "discord_id": data["id"],
                "username": data["username"],
                "global_name": data.get("global_name") or "",
                "avatar": avatar,
            },
        )

        return user