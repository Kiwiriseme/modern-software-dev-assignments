from backend.app.services.extract import extract_action_items, extract_tags


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "Ship it!" in items


def test_extract_tags():
    assert extract_tags("hello #world and #foo bar") == ["#world", "#foo"]
    assert extract_tags("no tags here") == []


def test_extract_tags_with_punctuation():
    assert extract_tags("do #task1, #task2 and #task3!") == ["#task1", "#task2", "#task3"]
