from django.contrib import admin
from .models import Event, GoogleToken

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'start_date', 'end_date', 'google_event_id')
    search_fields = ('title', 'description', 'google_event_id')
    list_filter = ('project', 'start_date')

@admin.register(GoogleToken)
class GoogleTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__email',)
