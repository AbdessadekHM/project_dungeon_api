from django.db import models

# Create your models here.


class Event(Task):
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    google_event_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    meet_link = models.URLField(null=True, blank=True)
    attendees = models.ManyToManyField("account.User", related_name="event_attendees", blank=True)


class GoogleToken(models.Model):
    user = models.OneToOneField("account.User", on_delete=models.CASCADE, related_name="google_token")
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"GoogleToken for {self.user.email}"
