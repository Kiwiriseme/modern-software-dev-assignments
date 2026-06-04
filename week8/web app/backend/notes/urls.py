from django.urls import path
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


urlpatterns = router.urls + [
    path("categories", CategoryListView.as_view(), name="categories"),
]
