from django.contrib import admin
from .models import Project, Task, Team, Repository, Issue

# Register your models here.

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Team)
admin.site.register(Repository)
admin.site.register(Issue)