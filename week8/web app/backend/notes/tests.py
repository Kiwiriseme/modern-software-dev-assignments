from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from notes.ai_service import decrypt_api_key, encrypt_api_key
from notes.models import AISettings, Note, Todo
from notes.serializers import NoteSerializer, TodoSerializer


class TodoModelTest(TestCase):
    def test_create_todo_with_minimal_fields(self):
        todo = Todo.objects.create(title="Buy groceries")
        self.assertEqual(todo.title, "Buy groceries")
        self.assertEqual(todo.content, "")
        self.assertEqual(todo.category, "")
        self.assertFalse(todo.is_completed)
        self.assertIsNotNone(todo.created_at)
        self.assertIsNotNone(todo.updated_at)

    def test_create_todo_with_all_fields(self):
        todo = Todo.objects.create(
            title="Finish report",
            content="Need to include charts",
            category="工作",
            is_completed=True,
        )
        self.assertEqual(todo.content, "Need to include charts")
        self.assertEqual(todo.category, "工作")
        self.assertTrue(todo.is_completed)

    def test_todo_ordering(self):
        t1 = Todo.objects.create(title="First", category="工作")
        t2 = Todo.objects.create(title="Second", category="工作")
        todos = list(Todo.objects.order_by("created_at"))
        self.assertEqual(todos[0].title, t1.title)
        self.assertEqual(todos[1].title, t2.title)

    def test_title_max_length(self):
        todo = Todo.objects.create(title="a" * 200)
        self.assertEqual(len(todo.title), 200)
        too_long = Todo(title="a" * 201)
        with self.assertRaises(ValidationError):
            too_long.full_clean()

    def test_due_date_defaults_to_today(self):
        from datetime import date

        todo = Todo.objects.create(title="Task with default due date")
        self.assertEqual(todo.due_date, date.today())

    def test_due_date_can_be_set_explicitly(self):
        from datetime import date

        d = date(2026, 12, 25)
        todo = Todo.objects.create(title="Christmas task", due_date=d)
        self.assertEqual(todo.due_date, d)


class NoteModelTest(TestCase):
    def test_create_note(self):
        note = Note.objects.create(
            title="Meeting Notes",
            content="## Agenda\n- Item 1\n- Item 2",
            category="工作",
        )
        self.assertEqual(note.title, "Meeting Notes")
        self.assertEqual(note.category, "工作")
        self.assertFalse(note.content == "")

    def test_note_defaults(self):
        note = Note.objects.create(title="Quick Note")
        self.assertEqual(note.content, "")
        self.assertEqual(note.category, "")


class TodoSerializerTest(TestCase):
    def test_valid_todo(self):
        data = {"title": "Test Todo", "category": "工作"}
        serializer = TodoSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_empty_title_rejected(self):
        data = {"title": "", "category": "工作"}
        serializer = TodoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_whitespace_only_title_rejected(self):
        data = {"title": "   ", "category": "工作"}
        serializer = TodoSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_title_stripped_on_validation(self):
        data = {"title": "  Clean me  ", "category": "工作"}
        serializer = TodoSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["title"], "Clean me")

    def test_category_stripped(self):
        data = {"title": "Test", "category": " 工作 "}
        serializer = TodoSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["category"], "工作")

    def test_content_max_length(self):
        data = {"title": "Test", "content": "a" * 10001}
        serializer = TodoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_category_max_length(self):
        data = {"title": "Test", "category": "a" * 51}
        serializer = TodoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("category", serializer.errors)


class NoteSerializerTest(TestCase):
    def test_valid_note(self):
        data = {"title": "Meeting Notes", "content": "# Agenda", "category": "工作"}
        serializer = NoteSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_empty_title_rejected(self):
        data = {"title": "", "content": "Some content"}
        serializer = NoteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)


class TodoAPITest(APITestCase):
    def setUp(self):
        self.todo = Todo.objects.create(title="Test Todo", category="工作")

    def test_list_todos(self):
        response = self.client.get("/api/v1/todos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_todo(self):
        response = self.client.post(
            "/api/v1/todos",
            {
                "title": "New Todo",
                "category": "学习",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Todo.objects.count(), 2)

    def test_get_todo_detail(self):
        response = self.client.get(f"/api/v1/todos/{self.todo.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Todo")

    def test_update_todo(self):
        response = self.client.put(
            f"/api/v1/todos/{self.todo.id}",
            {
                "title": "Updated Todo",
                "category": "生活",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, "Updated Todo")
        self.assertEqual(self.todo.category, "生活")

    def test_patch_toggle_complete(self):
        response = self.client.patch(
            f"/api/v1/todos/{self.todo.id}",
            {
                "is_completed": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.is_completed)

    def test_delete_todo(self):
        response = self.client.delete(f"/api/v1/todos/{self.todo.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Todo.objects.count(), 0)

    def test_filter_by_category(self):
        Todo.objects.create(title="Study", category="学习")
        response = self.client.get("/api/v1/todos?category=学习")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_search_todos(self):
        Todo.objects.create(title="Buy milk", content="Grocery shopping")
        response = self.client.get("/api/v1/todos?q=milk")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_invalid_todo(self):
        response = self.client.post(
            "/api/v1/todos",
            {
                "title": "",
                "category": "工作",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pagination(self):
        for i in range(25):
            Todo.objects.create(title=f"Todo {i}", category="工作")
        response = self.client.get("/api/v1/todos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 20)
        self.assertEqual(response.data["count"], 26)
        self.assertIsNotNone(response.data["next"])

    def test_create_todo_with_due_date(self):
        response = self.client.post(
            "/api/v1/todos",
            {
                "title": "Scheduled Todo",
                "category": "工作",
                "due_date": "2026-12-25",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["due_date"], "2026-12-25")

    def test_create_todo_without_due_date_defaults_today(self):
        response = self.client.post(
            "/api/v1/todos",
            {
                "title": "No date todo",
                "category": "工作",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        from datetime import date

        self.assertEqual(response.data["due_date"], str(date.today()))


class NoteAPITest(APITestCase):
    def setUp(self):
        self.note = Note.objects.create(title="Meeting Notes", content="## Agenda", category="工作")

    def test_list_notes(self):
        response = self.client.get("/api/v1/notes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_note(self):
        response = self.client.post(
            "/api/v1/notes",
            {
                "title": "Ideas",
                "content": "Some ideas here",
                "category": "想法",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 2)

    def test_get_note_detail(self):
        response = self.client.get(f"/api/v1/notes/{self.note.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Meeting Notes")

    def test_update_note(self):
        response = self.client.put(
            f"/api/v1/notes/{self.note.id}",
            {
                "title": "Updated Notes",
                "content": "Updated content",
                "category": "学习",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Updated Notes")

    def test_delete_note(self):
        response = self.client.delete(f"/api/v1/notes/{self.note.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CategoryAPITest(APITestCase):
    def test_get_categories(self):
        Todo.objects.create(title="T1", category="工作")
        Todo.objects.create(title="T2", category="学习")
        Note.objects.create(title="N1", category="生活")
        response = self.client.get("/api/v1/categories")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {"工作", "学习", "生活"})

    def test_categories_deduplicated(self):
        Todo.objects.create(title="T1", category="工作")
        Note.objects.create(title="N1", category="工作")
        response = self.client.get("/api/v1/categories")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ["工作"])

    def test_empty_category_excluded(self):
        Todo.objects.create(title="T1", category="")
        response = self.client.get("/api/v1/categories")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class CategoryDeleteAPITest(APITestCase):
    def setUp(self):
        Todo.objects.create(title="Work Todo", category="工作")
        Todo.objects.create(title="Another Work Todo", category="工作")
        Note.objects.create(title="Work Note", category="工作")
        Todo.objects.create(title="Study Todo", category="学习")

    def test_delete_category_clears_items(self):
        response = self.client.delete("/api/v1/categories/delete?name=工作")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["deleted"], "工作")
        self.assertEqual(response.data["cleared"], 3)

    def test_deleted_category_items_now_have_empty_category(self):
        self.client.delete("/api/v1/categories/delete?name=工作")
        self.assertEqual(Todo.objects.filter(category="工作").count(), 0)
        self.assertEqual(Note.objects.filter(category="工作").count(), 0)
        self.assertEqual(Todo.objects.filter(category="").count(), 2)

    def test_delete_category_only_affects_target(self):
        self.client.delete("/api/v1/categories/delete?name=工作")
        self.assertEqual(Todo.objects.filter(category="学习").count(), 1)

    def test_delete_missing_name_returns_400(self):
        response = self.client.delete("/api/v1/categories/delete")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_nonexistent_category_succeeds_with_zero(self):
        response = self.client.delete("/api/v1/categories/delete?name=不存在")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cleared"], 0)


class AISettingsModelTest(TestCase):
    def test_get_solo_creates_default(self):
        self.assertEqual(AISettings.objects.count(), 0)
        s = AISettings.get_solo()
        self.assertEqual(s.model, "gpt-4o-mini")
        self.assertEqual(s.base_url, "https://api.openai.com/v1")
        self.assertEqual(s.api_key, "")
        self.assertFalse(s.is_configured())

    def test_get_solo_returns_existing(self):
        s1 = AISettings.get_solo()
        s2 = AISettings.get_solo()
        self.assertEqual(s1.pk, s2.pk)
        self.assertEqual(AISettings.objects.count(), 1)

    def test_is_configured_with_key(self):
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test-key")
        s.save()
        self.assertTrue(s.is_configured())


class AISettingsEncryptionTest(TestCase):
    def test_encrypt_decrypt_roundtrip(self):
        plaintext = "sk-test-api-key-12345"
        ciphertext = encrypt_api_key(plaintext)
        self.assertNotEqual(ciphertext, plaintext)
        self.assertNotIn("sk-test", ciphertext)
        decrypted = decrypt_api_key(ciphertext)
        self.assertEqual(decrypted, plaintext)

    def test_encrypt_empty_key(self):
        self.assertEqual(encrypt_api_key(""), "")

    def test_decrypt_empty_key(self):
        self.assertEqual(decrypt_api_key(""), "")


class AISettingsAPITest(APITestCase):
    def test_get_unconfigured_settings(self):
        response = self.client.get("/api/v1/ai-settings/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_configured"])
        self.assertEqual(response.data["api_key"], "")
        self.assertEqual(response.data["model"], "gpt-4o-mini")

    def test_put_settings_masks_key_in_response(self):
        response = self.client.put(
            "/api/v1/ai-settings/1",
            {
                "api_key": "sk-my-secret-key",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["api_key"], "***")

    def test_put_settings_encrypts_key_at_rest(self):
        self.client.put(
            "/api/v1/ai-settings/1",
            {
                "api_key": "sk-my-secret-key",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o",
            },
            format="json",
        )
        s = AISettings.get_solo()
        # The stored value should be encrypted, not the plaintext
        self.assertNotEqual(s.api_key, "sk-my-secret-key")
        self.assertTrue(len(s.api_key) > 0)
        # But it should decrypt back
        self.assertEqual(decrypt_api_key(s.api_key), "sk-my-secret-key")

    def test_put_star_preserves_existing_key(self):
        # First set a key
        self.client.put(
            "/api/v1/ai-settings/1",
            {
                "api_key": "sk-original-key",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o",
            },
            format="json",
        )
        # Then update with *** to preserve
        self.client.put(
            "/api/v1/ai-settings/1",
            {"api_key": "***", "base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
            format="json",
        )
        s = AISettings.get_solo()
        self.assertEqual(decrypt_api_key(s.api_key), "sk-original-key")
        self.assertEqual(s.model, "deepseek-chat")
        self.assertEqual(s.base_url, "https://api.deepseek.com/v1")


class AISummarizeAPITest(APITestCase):
    def setUp(self):
        self.note = Note.objects.create(
            title="Meeting Notes",
            content="需要完成项目报告\n需要回复客户邮件\n预约下周的会议室",
            category="工作",
        )

    def test_summarize_without_settings(self):
        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("请先配置", response.data["detail"])

    def test_summarize_empty_content(self):
        AISettings.get_solo()  # ensure exists
        note = Note.objects.create(title="Empty", content="", category="工作")
        # Configure AI settings
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test")
        s.save()
        response = self.client.post(f"/api/v1/notes/{note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("为空", response.data["detail"])

    @patch("notes.ai_service.requests.post")
    def test_summarize_success(self, mock_post):
        # Configure AI settings
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test")
        s.save()

        # Mock AI response
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '[{"title":"完成项目报告"},{"title":"回复客户邮件"},{"title":"预约会议室"}]'
                    }
                }
            ]
        }
        mock_post.return_value = mock_resp

        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["todos"]), 3)

        # Verify todos were created with correct category
        todos = Todo.objects.filter(category="工作")
        self.assertEqual(todos.count(), 3)
        titles = [t.title for t in todos]
        self.assertIn("完成项目报告", titles)
        self.assertIn("回复客户邮件", titles)
        self.assertIn("预约会议室", titles)

    @patch("notes.ai_service.requests.post")
    def test_summarize_no_todos_found(self, mock_post):
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test")
        s.save()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"choices": [{"message": {"content": "[]"}}]}
        mock_post.return_value = mock_resp

        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["todos"]), 0)

    @patch("notes.ai_service.requests.post")
    def test_summarize_ai_returns_401(self, mock_post):
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test")
        s.save()

        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.json.return_value = {"error": "Unauthorized"}
        mock_resp.raise_for_status.side_effect = Exception("401 Client Error: Unauthorized")
        mock_post.return_value = mock_resp

        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("密钥无效", response.data["detail"])

    @patch("notes.ai_service.requests.post")
    def test_summarize_ai_timeout(self, mock_post):
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test")
        s.save()

        import requests as requests_lib

        mock_post.side_effect = requests_lib.exceptions.Timeout("Connection timed out")

        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_504_GATEWAY_TIMEOUT)

    @patch("notes.ai_service.requests.post")
    def test_summarize_malformed_response(self, mock_post):
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test")
        s.save()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "这是一些随意的文本，没有JSON"}}]
        }
        mock_post.return_value = mock_resp

        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    @patch("notes.ai_service.requests.post")
    def test_summarize_with_code_fence_json(self, mock_post):
        s = AISettings.get_solo()
        s.api_key = encrypt_api_key("sk-test")
        s.save()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [
                {"message": {"content": '```json\n[{"title":"任务A"},{"title":"任务B"}]\n```'}}
            ]
        }
        mock_post.return_value = mock_resp

        response = self.client.post(f"/api/v1/notes/{self.note.id}/summarize-todos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
