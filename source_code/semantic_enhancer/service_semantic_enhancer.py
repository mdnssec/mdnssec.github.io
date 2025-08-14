import json
from typing import List, Dict, Any

from .llm_handler import LLMHandler
from .lda_model import LDAModel
from .tfidf_model import TFIDFModel

# ---------------- 主流程 ----------------

class ServiceSemanticEnhancer:
    """
    整合所有模块，执行完整的服务语义增强流程。
    """
    def __init__(self, llm_api_key: str, llm_base_url: str):
        self.llm_handler = LLMHandler(api_key=llm_api_key, base_url=llm_base_url)

    def enhance(
        self,
        service_names: List[str],
        lda_min_topics: int = 2,
        lda_max_topics: int = 10,
        tfidf_max_features: int = 1000,
        lda_top_words_num: int = 5
    ) -> Dict[str, Any]:
        """
        综合流程：LLM解释、LDA确定类别数及高频词、TF-IDF分类。
        """
        # 1. LLM 解释
        llm_cache = self.llm_handler.batch_describe(service_names)

        # 2. LDA 自动确定类别数和高频词
        lda_model = LDAModel(service_names)
        best_topic_num = lda_model.find_best_topic_num(lda_min_topics, lda_max_topics)
        lda_keywords = lda_model.get_top_words(best_topic_num, lda_top_words_num)

        # 3. TF-IDF 分类
        tfidf_model = TFIDFModel(max_features=tfidf_max_features)
        tfidf_model.train(service_names)
        vectors = tfidf_model.classify(service_names)

        # 4. 汇总结果
        results = []
        for name, vec in zip(service_names, vectors):
            results.append({
                "service_name": name,
                "tfidf_vector": vec.toarray().tolist()[0],
                "llm_description": llm_cache.get(name, "N/A")
            })

        return {
            "best_topic_num": best_topic_num,
            "lda_topic_keywords": lda_keywords,
            "services": results
        }

# ---------------- 示例用法 ----------------

if __name__ == "__main__":
    # 请替换为您的API密钥和基础URL
    API_KEY = ""
    BASE_URL = ""

    services_to_analyze = [
        "_http._tcp.local.",
        "_printer._tcp.local.",
        "_airplay._tcp.local.",
        "_ssh._tcp.local.",
        "_ftp._tcp.local."
    ]
    
    enhancer = ServiceSemanticEnhancer(llm_api_key=API_KEY, llm_base_url=BASE_URL)
    
    result = enhancer.enhance(
        services_to_analyze, 
        lda_min_topics=2, 
        lda_max_topics=5, 
        lda_top_words_num=3
    )
    
    print("\n--- Final Result ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))