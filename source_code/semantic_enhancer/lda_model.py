from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from .utils import preprocess_service_names

class LDAModel:
    """
    封装LDA模型相关操作，用于确定主题数和提取主题关键词。
    """
    def __init__(self, service_names: List[str]):
        self.processed_names = preprocess_service_names(service_names)
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.X = self.vectorizer.fit_transform(self.processed_names)

    def find_best_topic_num(self, min_topics=2, max_topics=10) -> int:
        """
        通过困惑度自动确定最佳主题数。
        """
        best_num = min_topics
        best_score = float('inf')
        for n in range(min_topics, max_topics + 1):
            lda = LatentDirichletAllocation(n_components=n, random_state=42)
            lda.fit(self.X)
            score = lda.perplexity(self.X)
            if score < best_score:
                best_score = score
                best_num = n
        return best_num

    def get_top_words(self, n_topics: int, n_top_words: int = 5) -> List[List[str]]:
        """
        获取每个主题的高频词。
        """
        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        lda.fit(self.X)
        feature_names = self.vectorizer.get_feature_names_out()
        topic_keywords = []
        for topic_idx, topic in enumerate(lda.components_):
            top_features = topic.argsort()[:-n_top_words - 1:-1]
            topic_keywords.append([feature_names[i] for i in top_features])
        return topic_keywords
