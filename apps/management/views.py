from rest_framework import viewsets
from .models import Project, Task, Team, Repository, Event
from .serializers import ProjectSerializer, TaskSerializer, TeamSerializer, RepositorySerializer, EventSerializer
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class BaseProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

class ProjectViewSet(BaseProjectViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class TaskViewSet(BaseProjectViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    
class TeamViewSet(BaseProjectViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    
class RepositoryViewSet(BaseProjectViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
    
class EventViewSet(BaseProjectViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
