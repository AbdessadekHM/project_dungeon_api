from rest_framework import serializers #type:ignore
from .models import Project, Task, Team, Repository, Issue, Message



class ProjectSerializer(serializers.ModelSerializer):
    tasks_count = serializers.IntegerField(source='calculated_tasks_count', read_only=True)
    completed_tasks_count = serializers.IntegerField(source='calculated_completed_tasks_count', read_only=True)
    collaborators_count = serializers.IntegerField(source='calculated_collaborators_count', read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['owner']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "priority", "task_type", "project", "assignee", "deadline"]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        user = self.context['request'].user
        project = instance.project

        if user.role == 'admin' or project.owner == user:
            return super().update(instance, validated_data)

        status = validated_data.get('status', instance.status)
        instance.status = status
        instance.save(update_fields=['status'])
        return instance

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = '__all__'

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']

# EventSerializer moved to google_calendar app

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'project', 'sender', 'sender_username', 'content', 'created_at']
        read_only_fields = ['id', 'sender', 'sender_username', 'created_at']