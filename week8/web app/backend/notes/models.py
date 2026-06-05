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


class AISettings(models.Model):
    """Singleton model storing AI API configuration. Only one row should exist."""

    api_key = models.CharField(max_length=512, blank=True, default="")
    base_url = models.URLField(default="https://api.openai.com/v1")
    model = models.CharField(max_length=100, default="gpt-4o-mini")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI Settings"
        verbose_name_plural = "AI Settings"

    def __str__(self):
        return f"AISettings (model={self.model})"

    def is_configured(self):
        return bool(self.api_key)

    @classmethod
    def get_solo(cls):
        """Return the singleton AISettings instance, creating one if it doesn't exist."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
