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

TASK_TYPE = (
    ("feature", "Feature"),
    ("bug", "Bug"),
    ("documentation", "Documentation"),
    ("other", "Other"),
)

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey("account.User", on_delete=models.CASCADE, related_name="owner")
    collaborators = models.ManyToManyField("account.User", related_name="collaborators", blank=True)
    repositories = models.ManyToManyField("management.Repository", related_name="repositories", blank=True)
    teams = models.ManyToManyField("management.Team", related_name="teams", blank=True)

    @property
    def calculated_tasks_count(self):
        return len(self.tasks.all())

    @property
    def calculated_collaborators_count(self):
        individual_ids = {user.id for user in self.collaborators.all()}
        team_member_ids = {user.id for team in self.teams.all() for user in team.collaborators.all()}
        return len(individual_ids.union(team_member_ids))

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=TASK_STATUS, default="todo")
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVEL, default="low")
    task_type = models.CharField(max_length=20, choices=TASK_TYPE, default="other")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assignee = models.ForeignKey("account.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    deadline = models.DateField()


class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    collaborators = models.ManyToManyField("account.User", related_name="members", blank=True)
    owner = models.ForeignKey("account.User", on_delete=models.CASCADE)
    projects = models.ManyToManyField(Project, related_name="projects", blank=True)

class Repository(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    link = models.URLField()

class Event(Task):
    start_date = models.DateField()
    end_date = models.DateField()