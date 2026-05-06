from src.classifier import BaselineClassifier


def test_baseline_classifier_train_predict() -> None:
    model = BaselineClassifier.build()
    texts = ["privacy consent", "update docs"]
    labels = [1, 0]
    model.train(texts, labels)
    preds = model.predict(["consent needed"])
    assert len(preds) == 1
