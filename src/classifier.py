from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


@dataclass
class BaselineClassifier:
    pipeline: Pipeline

    @classmethod
    def build(cls) -> "BaselineClassifier":
        pipeline = Pipeline(
            steps=[
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
                ("svm", LinearSVC()),
            ]
        )
        return cls(pipeline=pipeline)

    def train(self, texts: Iterable[str], labels: Iterable[int]) -> None:
        self.pipeline.fit(list(texts), list(labels))

    def predict(self, texts: Iterable[str]) -> list[int]:
        return list(self.pipeline.predict(list(texts)))

    def evaluate(self, texts: Iterable[str], labels: Iterable[int]) -> str:
        predictions = self.predict(texts)
        return classification_report(list(labels), predictions)


def load_codebert_classifier(model_path: str):
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    from transformers import TextClassificationPipeline

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    return TextClassificationPipeline(model=model, tokenizer=tokenizer, return_all_scores=False)


def codebert_predict(pipeline, texts: Iterable[str]) -> list[dict]:
    return [pipeline(text) for text in texts]
