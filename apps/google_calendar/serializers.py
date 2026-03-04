from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    attendees_detail = serializers.SerializerMethodField(read_only=True)
    start = serializers.DateTimeField(source='start_time', read_only=True)
    end = serializers.DateTimeField(source='end_time', read_only=True)
    source = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['google_event_id', 'meet_link']

    def get_attendees_detail(self, obj):
        return [
            {'id': user.id, 'email': user.email, 'username': user.username}
            for user in obj.attendees.all()
        ]

    def get_source(self, obj):
        return 'local'