from django.urls import path
from . import views

urlpatterns = [
    path("", views.event_list, name="events"),
    path("new/", views.new_event, name="new"),
    path("<slug:slug>/", views.event_page, name="event_page"),
]