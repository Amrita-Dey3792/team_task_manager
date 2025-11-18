from django.db import models
from django.conf import settings
import uuid

# Create your models here.

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_companies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name