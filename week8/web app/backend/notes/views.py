from django.db import models
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from notes.ai_service import (
    AINotConfiguredError,
    AIServiceError,
    EmptyContentError,
    summarize_note_todos,
)
from notes.models import AISettings, Note, Todo
from notes.serializers import AISettingsSerializer, NoteSerializer, TodoSerializer


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

    @action(detail=True, methods=["post"], url_path="summarize-todos")
    def summarize_todos(self, request, pk=None):
        """Call AI to extract todo items from the note content."""
        note = self.get_object()
        try:
            todos, count = summarize_note_todos(note)
        except AINotConfiguredError:
            return Response(
                {"detail": "请先配置 API 设置"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except EmptyContentError:
            return Response(
                {"detail": "笔记内容为空"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except AIServiceError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            # Handle requests.exceptions.RequestException (network, timeout, auth errors)
            error_str = str(e)
            if "401" in error_str or "Unauthorized" in error_str or "403" in error_str:
                return Response(
                    {"detail": "API 密钥无效，请检查设置"},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            if "timeout" in error_str.lower() or "Timeout" in error_str:
                return Response(
                    {"detail": "AI 请求超时，请重试"},
                    status=status.HTTP_504_GATEWAY_TIMEOUT,
                )
            return Response(
                {"detail": f"AI API 请求失败: {error_str}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        serializer = TodoSerializer(todos, many=True)
        return Response({"todos": serializer.data, "count": count})


class AISettingsViewSet(viewsets.ModelViewSet):
    """CRUD for AI settings. Only supports get/update since it's a singleton."""

    serializer_class = AISettingsSerializer
    http_method_names = ["get", "put", "head", "options"]

    def get_queryset(self):
        # Return the singleton
        return AISettings.objects.filter(pk=AISettings.get_solo().pk)

    def get_object(self):
        return AISettings.get_solo()
