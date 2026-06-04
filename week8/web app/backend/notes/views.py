from django.db import models
from rest_framework import viewsets

from notes.models import Note, Todo
from notes.serializers import NoteSerializer, TodoSerializer


class BaseItemViewSet(viewsets.ModelViewSet):
    """共享过滤逻辑的基类"""

    def filter_queryset_by_params(self, queryset):
        category = self.request.query_params.get("category", None)
        q = self.request.query_params.get("q", None)
        if category and category != "全部":
            queryset = queryset.filter(category=category)
        if q:
            queryset = queryset.filter(
                models.Q(title__icontains=q) | models.Q(content__icontains=q)
            )
        return queryset


class TodoViewSet(BaseItemViewSet):
    serializer_class = TodoSerializer

    def get_queryset(self):
        return self.filter_queryset_by_params(Todo.objects.all())


class NoteViewSet(BaseItemViewSet):
    serializer_class = NoteSerializer

    def get_queryset(self):
        return self.filter_queryset_by_params(Note.objects.all())
