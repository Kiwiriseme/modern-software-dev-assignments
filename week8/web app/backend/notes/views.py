from django.contrib.auth import authenticate, login, logout
from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from notes.ai_service import (
    AINotConfiguredError,
    AIServiceError,
    EmptyContentError,
    summarize_note_todos,
)
from notes.models import AISettings, Note, Todo
from notes.serializers import (
    AISettingsSerializer,
    LoginSerializer,
    NoteSerializer,
    RegisterSerializer,
    TodoSerializer,
)


class BaseItemViewSet(viewsets.ModelViewSet):
    """共享过滤逻辑的基类 — 所有操作需要登录，数据按当前用户过滤"""

    permission_classes = [IsAuthenticated]

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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TodoViewSet(BaseItemViewSet):
    serializer_class = TodoSerializer

    def get_queryset(self):
        return self.filter_queryset_by_params(Todo.objects.filter(user=self.request.user))


class NoteViewSet(BaseItemViewSet):
    serializer_class = NoteSerializer

    def get_queryset(self):
        return self.filter_queryset_by_params(Note.objects.filter(user=self.request.user))

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
            error_str = str(e)
            if "401" in error_str or "Unauthorized" in error_str or "403" in error_str:
                return Response(
                    {"detail": "API 密钥无效，请检查设置"},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            if (
                "timeout" in error_str.lower()
                or "Timeout" in error_str
                or "timed out" in error_str.lower()
            ):
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


class AuthViewSet(viewsets.GenericViewSet):
    """Registration, login, logout, current-user, and CSRF token endpoints."""

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def get_serializer_class(self):
        if self.action == "login_view":
            return LoginSerializer
        return RegisterSerializer

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    @method_decorator(ensure_csrf_cookie)
    def csrf(self, request):
        """Set the CSRF cookie for the SPA."""
        return Response({"detail": "CSRF cookie set"})

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create AISettings for the new user
        AISettings.objects.create(user=user)

        login(request, user)
        return Response(
            {"id": user.id, "email": user.email},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def login_view(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {"detail": "邮箱或密码错误"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        return Response({"id": user.id, "email": user.email})

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout_view(self, request):
        logout(request)
        return Response({"detail": "已登出"})

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response({"id": request.user.id, "email": request.user.email})


class AISettingsViewSet(viewsets.ModelViewSet):
    """Per-user AI settings. GET returns current user's settings, PUT updates it."""

    serializer_class = AISettingsSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "head", "options"]

    def get_queryset(self):
        return AISettings.objects.filter(user=self.request.user)

    def get_object(self):
        obj, _ = AISettings.objects.get_or_create(user=self.request.user)
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
