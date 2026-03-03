from django.urls import path
from .views import ProjectViewSet, TaskViewSet, TeamViewSet, RepositoryViewSet, EventViewSet

urlpatterns = [
    path("projects", ProjectViewSet.as_view(actions={"get": "list", "post": "create"}), name="projects"),
    path("tasks", TaskViewSet.as_view(actions={"get": "list", "post": "create"}), name="tasks"),
    path("teams", TeamViewSet.as_view(actions={"get": "list", "post": "create"}), name="teams"),
    path("repositories", RepositoryViewSet.as_view(actions={"get": "list", "post": "create"}), name="repositories"),
    path("events", EventViewSet.as_view(actions={"get": "list", "post": "create"}), name="events"),
    
]
