import numpy as np
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from .utils import preprocess_service_names

class TFIDFModel:
    """
    封装TF-IDF模型，用于文本向量化。
    """
    def __init__(self, max_features: int = 1000):
        self.vectorizer = TfidfVectorizer(max_features=max_features)

    def train(self, service_names: List[str]):
        """
        训练 TF-IDF 模型。
        """
        processed = preprocess_service_names(service_names)
        self.vectorizer.fit(processed)

    def classify(self, service_names: List[str]) -> np.ndarray:
        """
        使用 TF-IDF 模型对服务名进行向量化。
        """
        processed = preprocess_service_names(service_names)
        return self.vectorizer.transform(processed)
