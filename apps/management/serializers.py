from rest_framework import serializers
from .models import Project, Task, Team, Repository, Event



class ProjectSerializer(serializers.ModelSerializer):
    tasks_count = serializers.IntegerField(source='calculated_tasks_count', read_only=True)
    collaborators_count = serializers.IntegerField(source='calculated_collaborators_count', read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['owner']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'