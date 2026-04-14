from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('delayed', 'Delayed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    voice_transcript = models.TextField(blank=True)
    parser_confidence = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    original_due_date = models.DateTimeField(null=True, blank=True)
    delay_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.due_date and self.status == 'pending':
            return timezone.now() > self.due_date
        return False

    @property
    def completed_on_time(self):
        if self.status == 'completed' and self.completed_at and self.due_date:
            return self.completed_at <= self.due_date
        return None

    def mark_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def mark_cancelled(self):
        self.status = 'cancelled'
        self.save()

    def delay(self, days=1):
        if self.due_date:
            if not self.original_due_date:
                self.original_due_date = self.due_date
            self.due_date = self.due_date + timezone.timedelta(days=days)
            self.delay_count += 1
            self.status = 'delayed'
            self.save() 