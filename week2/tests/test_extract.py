import json
from unittest.mock import MagicMock, patch

from ..app.services.extract import extract_action_items, extract_action_items_llm


def _make_chat_response(items: list[str]) -> MagicMock:
    resp = MagicMock()
    resp.message.content = json.dumps({"items": items})
    return resp


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


class TestExtractActionItemsLLM:
    @patch("week2.app.services.extract.chat")
    def test_bullet_list_input(self, mock_chat):
        text = """Notes from meeting:
- Set up database
* implement API endpoint
1. Write unit tests
Some narrative sentence."""

        mock_chat.return_value = _make_chat_response(
            ["Set up database", "implement API endpoint", "Write unit tests"]
        )

        items = extract_action_items_llm(text)

        assert len(items) == 3
        assert "Set up database" in items
        assert "implement API endpoint" in items
        assert "Write unit tests" in items

        call_args = mock_chat.call_args.kwargs
        assert text in call_args["messages"][0]["content"]
        assert call_args["model"] == "mistral-nemo:12b"

    @patch("week2.app.services.extract.chat")
    def test_keyword_prefixed_lines(self, mock_chat):
        text = """TODO: Refactor database layer
action: Update API documentation
next: Write integration tests
Some random thought."""

        mock_chat.return_value = _make_chat_response(
            ["Refactor database layer", "Update API documentation", "Write integration tests"]
        )

        items = extract_action_items_llm(text)

        assert len(items) == 3
        assert "Refactor database layer" in items
        assert "Update API documentation" in items
        assert "Write integration tests" in items

        call_args = mock_chat.call_args.kwargs
        assert text in call_args["messages"][0]["content"]

    @patch("week2.app.services.extract.chat")
    def test_plain_paragraph_text(self, mock_chat):
        text = "We need to add error handling to the API. The database connection should be optimized for better performance. Also we should update the user documentation."

        mock_chat.return_value = _make_chat_response(
            [
                "Add error handling to the API",
                "Optimize database connection",
                "Update user documentation",
            ]
        )

        items = extract_action_items_llm(text)

        assert len(items) == 3
        assert "Add error handling to the API" in items
        assert "Optimize database connection" in items
        assert "Update user documentation" in items

    @patch("week2.app.services.extract.chat")
    def test_empty_input_returns_empty_list(self, mock_chat):
        mock_chat.return_value = _make_chat_response([])

        items = extract_action_items_llm("")

        assert items == []
        mock_chat.assert_called_once()

    @patch("week2.app.services.extract.chat")
    def test_whitespace_only_input(self, mock_chat):
        mock_chat.return_value = _make_chat_response([])

        items = extract_action_items_llm("   \n  \t  \n   ")

        assert items == []
        mock_chat.assert_called_once()

    @patch("week2.app.services.extract.chat")
    def test_deduplication_case_insensitive(self, mock_chat):
        text = "- Set up database\n- Set Up Database\n- SET UP DATABASE"

        mock_chat.return_value = _make_chat_response(
            ["Set up database", "Set Up Database", "SET UP DATABASE"]
        )

        items = extract_action_items_llm(text)

        assert len(items) == 1
        assert items == ["Set up database"]

    @patch("week2.app.services.extract.chat")
    def test_empty_items_filtered_from_response(self, mock_chat):
        mock_chat.return_value = _make_chat_response(["Set up database", "", "   ", "Write tests"])

        items = extract_action_items_llm("- Set up database\n- Write tests")

        assert len(items) == 2
        assert "Set up database" in items
        assert "Write tests" in items

    @patch("week2.app.services.extract.chat")
    def test_whitespace_trimming_on_items(self, mock_chat):
        mock_chat.return_value = _make_chat_response(
            ["  Set up database  ", "\tImplement API\t", "Write tests"]
        )

        items = extract_action_items_llm("- Set up database\n- Implement API\n- Write tests")

        assert items == ["Set up database", "Implement API", "Write tests"]

    @patch("week2.app.services.extract.chat")
    def test_llm_returns_no_action_items(self, mock_chat):
        text = "The weather is nice today. I had lunch with a friend."

        mock_chat.return_value = _make_chat_response([])

        items = extract_action_items_llm(text)

        assert items == []

    @patch("week2.app.services.extract.chat")
    def test_mixed_input_with_checkboxes_and_narrative(self, mock_chat):
        text = """Meeting Agenda:
- [ ] Review Q1 report
* Schedule follow-up meeting
The coffee was great today.
todo: Submit expense report
Random thought about the project."""

        mock_chat.return_value = _make_chat_response(
            ["Review Q1 report", "Schedule follow-up meeting", "Submit expense report"]
        )

        items = extract_action_items_llm(text)

        assert len(items) == 3
        assert "Review Q1 report" in items
        assert "Schedule follow-up meeting" in items
        assert "Submit expense report" in items

    @patch("week2.app.services.extract.chat")
    def test_chat_called_with_correct_model_and_format(self, mock_chat):
        mock_chat.return_value = _make_chat_response(["Test item"])

        from ..app.services.extract import ActionItems

        extract_action_items_llm("Test item")

        call_args = mock_chat.call_args.kwargs
        assert call_args["model"] == "mistral-nemo:12b"
        assert call_args["format"] == ActionItems.model_json_schema()

    @patch("week2.app.services.extract.chat")
    def test_multiline_bullet_list_with_various_prefixes(self, mock_chat):
        text = """- Buy groceries
* Clean the house
• Call the doctor
1. Finish the report
2. Submit the PR"""

        mock_chat.return_value = _make_chat_response(
            [
                "Buy groceries",
                "Clean the house",
                "Call the doctor",
                "Finish the report",
                "Submit the PR",
            ]
        )

        items = extract_action_items_llm(text)

        assert len(items) == 5
        assert "Buy groceries" in items
        assert "Clean the house" in items
        assert "Call the doctor" in items
        assert "Finish the report" in items
        assert "Submit the PR" in items
