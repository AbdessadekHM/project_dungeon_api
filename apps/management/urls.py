from django.urls import path
from .views import ProjectViewSet, TaskViewSet, TeamViewSet, RepositoryViewSet, IssueViewSet

urlpatterns = [
    path("projects/", ProjectViewSet.as_view(actions={"get": "list", "post": "create", "patch": "partial_update", "delete": "destroy"}), name="projects"),

    path("tasks/<int:pk>/", TaskViewSet.as_view(actions={"get": "retrieve", "patch": "partial_update", "delete": "destroy"}), name="tasks"),

    path("tasks/", TaskViewSet.as_view(actions={"get": "list", "post": "create", "patch": "partial_update", "delete": "destroy"}), name="tasks"),

    path("teams/<int:pk>/", TeamViewSet.as_view(actions={"get": "retrieve", "patch": "partial_update", "delete": "destroy"}), name="teams"),

    path("teams/", TeamViewSet.as_view(actions={"get": "list", "post": "create"}), name="teams"),

    path("repositories/", RepositoryViewSet.as_view(actions={"get": "list", "post": "create", "patch": "partial_update", "delete": "destroy"}), name="repositories"),
    
    path("issues/", IssueViewSet.as_view(actions={"get": "list", "post": "create", "patch": "partial_update", "delete": "destroy"}), name="issues"),
    path("issues/<int:pk>/", IssueViewSet.as_view(actions={"get": "retrieve", "patch": "partial_update", "delete": "destroy"}), name="issues-detail"),
]
