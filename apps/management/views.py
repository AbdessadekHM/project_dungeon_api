from rest_framework import viewsets
from .models import Project, Task, Team, Repository
from .serializers import ProjectSerializer, TaskSerializer, TeamSerializer, RepositorySerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsProjectOwnerOrCollaborator
from django.db.models import Count
from django.db.models import Q

class BaseProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

class ProjectViewSet(BaseProjectViewSet):
    serializer_class = ProjectSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin can see all projects
        if user.role == "admin":
            return Project.objects.prefetch_related('tasks', 'collaborators', 'teams__collaborators').all()
            
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
    permission_classes = [IsAuthenticated, IsProjectOwnerOrCollaborator]

    
class TeamViewSet(BaseProjectViewSet):
    serializer_class = TeamSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin can see all teams
        if user.role == "admin":
            return Team.objects.all()

        return Team.objects.filter(
            Q(owner=user) | 
            Q(collaborators=user)
        ).distinct()
    
class RepositoryViewSet(BaseProjectViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrCollaborator]
    
# EventViewSet moved to google_calendar app

