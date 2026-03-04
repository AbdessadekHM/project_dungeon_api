from django.urls import path
from .views import (
    EventViewSet,
    GoogleAuthURLView,
    GoogleAuthCallbackView,
    GoogleConnectionStatusView,
    GoogleCalendarSyncView,
    GoogleCalendarCreateEventView,
)

urlpatterns = [
    # Event local management
    path("events/", EventViewSet.as_view(actions={"get": "list", "post": "create", "patch": "partial_update", "delete": "destroy"}), name="google-events"),
    path("events/<int:pk>/", EventViewSet.as_view(actions={"get": "retrieve", "patch": "partial_update", "delete": "destroy"}), name="google-events-detail"),

    # Google Calendar integration
    path("auth-url/", GoogleAuthURLView.as_view(), name="google-auth-url"),
    path("callback/", GoogleAuthCallbackView.as_view(), name="google-callback"),
    path("status/", GoogleConnectionStatusView.as_view(), name="google-status"),
    path("sync/", GoogleCalendarSyncView.as_view(), name="google-calendar-sync"),
    path("create/", GoogleCalendarCreateEventView.as_view(), name="google-calendar-create"),
]