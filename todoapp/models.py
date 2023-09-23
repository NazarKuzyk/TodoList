from django.db import models
from django.contrib.auth.models import User

PRIORITY_CHOICES = [
    ('High', 'High'),
    ('Medium', 'Medium'),
    ('Low', 'Low'),
]

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Completed', 'Completed'),
]

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Incomplete')
    created = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')


    def __str__(self):
        return self.title