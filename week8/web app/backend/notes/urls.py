from django.urls import path
from rest_framework import status
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView

from notes.models import Note, Todo
from notes.views import NoteViewSet, TodoViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"todos", TodoViewSet, basename="todo")
router.register(r"notes", NoteViewSet, basename="note")


class CategoryListView(APIView):
    def get(self, request):
        todo_categories = (
            Todo.objects.exclude(category="").values_list("category", flat=True).distinct()
        )
        note_categories = (
            Note.objects.exclude(category="").values_list("category", flat=True).distinct()
        )
        all_categories = sorted(set(list(todo_categories) + list(note_categories)))
        return Response(all_categories)


class CategoryDeleteView(APIView):
    def delete(self, request):
        name = request.query_params.get("name", "")
        if not name:
            return Response({"detail": "缺少分类名称参数"}, status=status.HTTP_400_BAD_REQUEST)
        todo_count = Todo.objects.filter(category=name).update(category="")
        note_count = Note.objects.filter(category=name).update(category="")
        total = todo_count + note_count
        return Response({"deleted": name, "cleared": total})


urlpatterns = router.urls + [
    path("categories", CategoryListView.as_view(), name="categories"),
    path("categories/delete", CategoryDeleteView.as_view(), name="category-delete"),
]
