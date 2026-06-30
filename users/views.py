from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import MinecraftAccountForm

@login_required
def profile(request):
    profile_obj = request.user.profile
    accounts = profile_obj.minecraft_accounts.all()

    return render(
        request,
        "users/profile.html",
        {
            "profile": profile_obj,
            "accounts": accounts,
        },
    )

@login_required
def add_minecraft_account(request):
    if request.method == "POST":
        form = MinecraftAccountForm(request.POST)

        if form.is_valid():
            account = form.save(commit=False)

            account.profile = request.user.profile
            account.save()

            return redirect("me")

    else:
        form = MinecraftAccountForm()

    return render(
        request,
        "users/add_account.html",
        {"form": form},
    )

@login_required
def delete_account(request, pk):
    account = request.user.profile.minecraft_accounts.get(pk=pk)

    if request.method == "POST":
        account.delete()
        return redirect("me")

    return redirect("me")