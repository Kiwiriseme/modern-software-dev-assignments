from datetime import date

from django.db import models


class Todo(models.Model):
    CATEGORY_CHOICES = [
        ("工作", "工作"),
        ("学习", "学习"),
        ("生活", "生活"),
        ("想法", "想法"),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, default="")
    category = models.CharField(max_length=50, blank=True, default="")
    due_date = models.DateField(null=True, blank=True, default=date.today)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, default="")
    category = models.CharField(max_length=50, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
