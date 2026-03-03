from django.db import models

# Create your models here.


TASK_STATUS = (
    ("todo", "Todo"),
    ("in_progress", "In Progress"),
    ("finished", "Finished"),
)
PRIORITY_LEVEL = (
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
)

EVENT_TYPE = (
    ("meeting", "Meeting"),
    ("issues", "Issues"),
    ("other", "Other"),
)


class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey("account.User", on_delete=models.CASCADE, related_name="owner")
    collaborators = models.ManyToManyField("account.User", related_name="collaborators")
    repositories = models.ManyToManyField("management.Repository", related_name="repositories")
    teams = models.ManyToManyField("management.Team", related_name="teams")
    

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=TASK_STATUS)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVEL)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    deadline = models.DateField()


class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    collaborators = models.ManyToManyField("account.User", related_name="collaborators")
    owner = models.ForeignKey("account.User", on_delete=models.CASCADE)
    projects = models.ManyToManyField(Project, related_name="projects")

class Repository(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="repositories")
    link = models.URLField()

class Event(Task):
    start_date = models.DateField()
    end_date = models.DateField()