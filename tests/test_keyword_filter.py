from src.keyword_filter import filter_instances


def test_filter_instances_matches_keyword() -> None:
    instances = [{"text": "TODO: add consent check"}, {"text": "refactor logging"}]
    keywords = ["consent"]
    filtered = filter_instances(instances, keywords)
    assert len(filtered) == 1
