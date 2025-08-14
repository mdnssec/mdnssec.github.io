import re
from typing import List

def preprocess_service_names(service_names: List[str]) -> List[str]:
    """
    对服务名进行预处理（如分词、小写、去除特殊字符等）
    """
    processed = []
    for name in service_names:
        # 仅保留字母和数字，转小写
        clean = re.sub(r'[^a-zA-Z0-9 ]', ' ', name).lower()
        processed.append(clean)
    return processed
