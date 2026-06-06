from django.db import transaction
from django.urls import path
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView

from notes.models import Note, Todo
from notes.views import AISettingsViewSet, AuthViewSet, NoteViewSet, TodoViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"todos", TodoViewSet, basename="todo")
router.register(r"notes", NoteViewSet, basename="note")
router.register(r"ai-settings", AISettingsViewSet, basename="ai-settings")
router.register(r"auth", AuthViewSet, basename="auth")


class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        todo_categories = (
            Todo.objects.filter(user=request.user)
            .exclude(category="")
            .values_list("category", flat=True)
            .distinct()
        )
        note_categories = (
            Note.objects.filter(user=request.user)
            .exclude(category="")
            .values_list("category", flat=True)
            .distinct()
        )
        all_categories = sorted(set(list(todo_categories) + list(note_categories)))
        return Response(all_categories)


class CategoryDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request):
        name = request.query_params.get("name", "")
        if not name:
            return Response({"detail": "缺少分类名称参数"}, status=status.HTTP_400_BAD_REQUEST)
        todo_count = Todo.objects.filter(user=request.user, category=name).update(category="")
        note_count = Note.objects.filter(user=request.user, category=name).update(category="")
        total = todo_count + note_count
        return Response({"deleted": name, "cleared": total})


urlpatterns = router.urls + [
    path("categories", CategoryListView.as_view(), name="categories"),
    path("categories/delete", CategoryDeleteView.as_view(), name="category-delete"),
    # Override auth action URLs for clean paths
    path(
        "auth/register",
        AuthViewSet.as_view({"post": "register"}),
        name="auth-register",
    ),
    path(
        "auth/login",
        AuthViewSet.as_view({"post": "login_view"}),
        name="auth-login",
    ),
    path(
        "auth/logout",
        AuthViewSet.as_view({"post": "logout_view"}),
        name="auth-logout",
    ),
    path(
        "auth/me",
        AuthViewSet.as_view({"get": "me"}),
        name="auth-me",
    ),
]
