from src.collector import compact_text


def test_compact_text() -> None:
    text = "hello\nworld"
    assert compact_text(text) == "hello world"
