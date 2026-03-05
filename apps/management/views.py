from rest_framework import viewsets
from .models import Project, Task, Team, Repository, Issue
from .serializers import ProjectSerializer, TaskSerializer, TeamSerializer, RepositorySerializer, IssueSerializer
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
    
class IssueViewSet(BaseProjectViewSet):
    item_model = Issue
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrCollaborator]

    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get('project')
        
        if user.role == "admin":
            queryset = Issue.objects.all()
        else:
            queryset = Issue.objects.filter(
                Q(project__owner=user) | 
                Q(project__collaborators=user) | 
                Q(project__teams__collaborators=user)
            ).distinct()
            
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# EventViewSet moved to google_calendar app
