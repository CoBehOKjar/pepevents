from django.urls import path
from . import views

urlpatterns = [
    path("me/", views.profile, name="me"),
    path("me/add-account/", views.add_minecraft_account, name="add_account"),
    path("me/delete-account/<int:pk>/", views.delete_account, name="delete_account"),
]