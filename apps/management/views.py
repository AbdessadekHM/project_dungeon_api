from rest_framework import viewsets
from .models import Project, Task, Team, Repository, Event
from .serializers import ProjectSerializer, TaskSerializer, TeamSerializer, RepositorySerializer, EventSerializer
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class BaseProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

from django.db.models import Count

from django.db.models import Q

class ProjectViewSet(BaseProjectViewSet):
    serializer_class = ProjectSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Project.objects.prefetch_related(
            'tasks', 'collaborators', 'teams__collaborators'
        ).filter(
            Q(owner=user) | 
            Q(collaborators=user) | 
            Q(teams__collaborators=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskViewSet(BaseProjectViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    
class TeamViewSet(BaseProjectViewSet):
    serializer_class = TeamSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Team.objects.filter(
            Q(owner=user) | 
            Q(collaborators=user)
        ).distinct()
    
class RepositoryViewSet(BaseProjectViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
    
class EventViewSet(BaseProjectViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
