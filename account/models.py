from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

USER_ROLES = [
    ("user", "User"),
    ("admin", "Admin"),
]

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    phone = models.CharField(max_length=150, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=150, default="user", choices=USER_ROLES)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "phone", "birth_date", "role"]
    
    def __str__(self):
        return self.email

    
