from rest_framework import permissions
from django.db.models import Q
from .models import Project

class IsProjectOwnerOrCollaborator(permissions.BasePermission):
    """
    Custom permission for Tasks, Events, and Repositories.
    - Project Owners: Full CRUD
    - Project Collaborators/Team Members:
        - Repositories & Events: Read-only (GET, HEAD, OPTIONS)
        - Tasks: Read-only + PATCH allowed ONLY for 'status'
    - Admins: Ignored here (handled by viewset queryset or other logic if needed, but normally admins have full access)
    """

    def has_permission(self, request, view):
        # Allow authenticated users to perform list/create if they pass `has_object_permission` later.
        # But for creation, we need to verify they own the project they are trying to attach to.
        if request.user and request.user.role == 'admin':
            return True

        if request.method == 'POST':
            project_id = request.data.get('project')
            if not project_id:
                return False # Need a project to create a resource

            try:
                project = Project.objects.get(id=project_id)
                # Only owners can create resources
                return project.owner == request.user
            except Project.DoesNotExist:
                return False

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admins can do everything
        if request.user.role == 'admin':
            return True

        # Assuming obj is Task, Event, or Repository, it HAS to have a `project` attribute.
        project = obj.project
        user = request.user

        is_owner = project.owner == user
        
        # Check if user is a direct collaborator or via a team
        is_collaborator = project.collaborators.filter(id=user.id).exists() or \
                          project.teams.filter(collaborators=user).exists()

        if is_owner:
            return True

        if is_collaborator:
            # Read permissions are allowed for collaborators
            if request.method in permissions.SAFE_METHODS:
                return True
                
            # For Tasks, collaborators can only PATCH
            if hasattr(obj, 'status') and request.method == 'PATCH':
                return True
                
            return False

        return False