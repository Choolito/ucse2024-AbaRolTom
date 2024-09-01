from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(length=32)
        super().save(*args, **kwargs)