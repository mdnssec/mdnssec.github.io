import os
import csv
import re
import json
import time
from typing import Dict, List, Set

import easyocr
import pandas as pd
from geotext import GeoText
import nltk
from nltk.corpus import names
from openai import OpenAI

# --- 全局配置 ---
# 输入目录
SCREENSHOTS_DIR = os.path.join("output", "screenshots")
# 输出文件
OCR_RESULTS_CSV = os.path.join("output", "ocr_results.csv")
RULE_BASED_RESULTS_CSV = os.path.join("output", "privacy_analysis_rule_based.csv")
LLM_RESULTS_CSV = os.path.join("output", "privacy_analysis_llm.csv")
# 资源文件
NAME_CORPUS_PATH = 'English_Names_Corpus（2W）.txt' # 需确保此文件存在

# --- OpenAI API 配置 ---
client = OpenAI(
    base_url="https://uni-api.cstcloud.cn/v1",
    api_key="YOUR_API_KEY",  # 请替换为您的API Key
)

# --- 模块初始化 ---
def initialize_nltk_names():
    """下载并加载NLTK人名词典"""
    try:
        nltk.data.find('corpora/names')
    except nltk.downloader.DownloadError:
        print("首次运行，正在下载NLTK人名词典...")
        nltk.download('names')
    return set(name.lower() for name in names.words())

COMMON_NAMES = initialize_nltk_names()

# --- 1. OCR处理模块 ---
def perform_ocr_on_screenshots():
    """对截图目录中的所有图片执行OCR，并将结果保存到CSV"""
    print("\n--- 阶段1: 开始OCR处理 ---")
    if not os.path.exists(SCREENSHOTS_DIR):
        print(f"错误: 截图目录 '{SCREENSHOTS_DIR}' 不存在。")
        return

    reader = easyocr.Reader(['ch_sim', 'en'])
    ocr_data = []

    image_files = [f for f in os.listdir(SCREENSHOTS_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
    for filename in image_files:
        ip = os.path.splitext(filename)[0].replace('_', ':')
        file_path = os.path.join(SCREENSHOTS_DIR, filename)
        try:
            print(f"[*] 正在处理: {filename}")
            result = reader.readtext(file_path, detail=0, paragraph=True)
            ocr_text = ' '.join(result)
            ocr_data.append({'IP': ip, 'OCR_Text': ocr_text})
        except Exception as e:
            print(f"[!] OCR处理失败 {filename}: {e}")
    
    if ocr_data:
        pd.DataFrame(ocr_data).to_csv(OCR_RESULTS_CSV, index=False, encoding='utf-8')
        print(f"[+] OCR结果已保存到: {OCR_RESULTS_CSV}")
    else:
        print("未找到可处理的截图。")
    print("--- OCR处理完成 ---")


# --- 2. 基于规则的隐私分析模块 ---
def is_public_ip(ip: str) -> bool:
    """判断是否为公网IP地址"""
    private_ip_patterns = [
        re.compile(r"^10\..*"),
        re.compile(r"^172\.(1[6-9]|2[0-9]|3[0-1])\..*"),
        re.compile(r"^192\.168\..*")
    ]
    return not any(pat.match(ip) for pat in private_ip_patterns)

def analyze_privacy_rules():
    """使用正则表达式和词典进行隐私分析"""
    print("\n--- 阶段2: 开始基于规则的隐私分析 ---")
    if not os.path.exists(OCR_RESULTS_CSV):
        print(f"错误: OCR结果文件 '{OCR_RESULTS_CSV}' 不存在。请先运行OCR处理。")
        return

    # 定义正则表达式
    MAC_REGEX = re.compile(r'(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}')
    IP_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3})?[\s-]?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{4}\b')
    PRIVACY_CATEGORIES = ['Name', 'Location', 'MAC', 'PublicIP', 'Email', 'Phone']

    with open(OCR_RESULTS_CSV, 'r', encoding='utf-8') as infile, \
         open(RULE_BASED_RESULTS_CSV, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=['IP'] + PRIVACY_CATEGORIES)
        writer.writeheader()

        for row in reader:
            ip, ocr_content = row['IP'], row['OCR_Text']
            privacy = {cat: '' for cat in PRIVACY_CATEGORIES}

            # 人名、地名、MAC、IP、Email、电话识别
            words = re.findall(r'\b[a-zA-Z]{2,}\b', ocr_content)
            privacy['Name'] = ';'.join({word for word in words if word.lower() in COMMON_NAMES})
            
            places = GeoText(ocr_content)
            privacy['Location'] = ';'.join(set(places.cities + places.countries))
            
            privacy['MAC'] = ';'.join(set(MAC_REGEX.findall(ocr_content)))
            
            public_ips = {ip_addr for ip_addr in IP_REGEX.findall(ocr_content) if is_public_ip(ip_addr)}
            privacy['PublicIP'] = ';'.join(public_ips)
            
            privacy['Email'] = ';'.join(set(EMAIL_REGEX.findall(ocr_content)))
            privacy['Phone'] = ';'.join(set(PHONE_REGEX.findall(ocr_content)))

            writer.writerow({'IP': ip, **privacy})
    
    print(f"[+] 基于规则的分析结果已保存到: {RULE_BASED_RESULTS_CSV}")
    print("--- 基于规则的分析完成 ---")


# --- 3. 基于大模型的隐私分析模块 ---
PRIVACY_CATEGORIES_LLM = [
    "contains_names", "contains_locations", "contains_contacts",
    "contains_deviceid", "contains_medical", "contains_financial", "contains_ids"
]

def extract_json_from_response(response: str) -> Dict[str, bool]:
    """从API响应中安全地提取JSON数据"""
    try:
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            result = json.loads(json_match.group(0))
            return {k: bool(v) for k, v in result.items() if k in PRIVACY_CATEGORIES_LLM}
    except (json.JSONDecodeError, TypeError):
        print(f"无法解析响应中的JSON: {response}")
    return {category: False for category in PRIVACY_CATEGORIES_LLM}

def analyze_privacy_llm(ip: str, ocr_content: str) -> Dict[str, bool]:
    """使用大模型分析OCR内容中的隐私信息"""
    if not ocr_content or len(ocr_content.strip()) < 5:
        return {category: False for category in PRIVACY_CATEGORIES_LLM}

    prompt = f"""
    ### **隐私信息分析指令**
    **角色**：你是一名专业的数据安全分析师。
    **任务**：分析以下文本，检测所有隐私相关字段。
    **输出要求**：严格按JSON格式输出，仅包含以下预定义字段的布尔值（true/false）。
    **隐私检测类别**：
    - `contains_names`：人名
    - `contains_locations`：地理位置
    - `contains_contacts`：联系方式（电话/邮箱/社交账号）
    - `contains_deviceid`：设备标识符（IMEI/MAC地址/公网IP地址）
    - `contains_ids`：身份证、护照等ID
    - `contains_medical`：医疗信息
    - `contains_financial`：财务信息
    **分析规则**：
    1. 内网IP地址不视为隐私。
    2. 对模糊信息采用严格判定原则（如"张先生" -> `contains_names=true`）。

    **输入文本**：
    [IP]: {ip}
    [OCR]: {ocr_content}
    """
    try:
        completion = client.chat.completions.create(
            model="deepseek-r1:671b-64k",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        response = completion.choices[0].message.content
        return extract_json_from_response(response)
    except Exception as e:
        print(f"API调用出错 for IP {ip}: {e}")
        return {category: False for category in PRIVACY_CATEGORIES_LLM}

def analyze_privacy_with_llm():
    """使用大模型对OCR结果进行隐私分析"""
    print("\n--- 阶段3: 开始基于大模型的隐私分析 ---")
    if not os.path.exists(OCR_RESULTS_CSV):
        print(f"错误: OCR结果文件 '{OCR_RESULTS_CSV}' 不存在。请先运行OCR处理。")
        return

    with open(OCR_RESULTS_CSV, 'r', encoding='utf-8') as infile, \
         open(LLM_RESULTS_CSV, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=['IP'] + PRIVACY_CATEGORIES_LLM)
        writer.writeheader()

        for i, row in enumerate(reader):
            ip, ocr_content = row['IP'], row['OCR_Text']
            print(f"[*] 正在使用LLM分析 IP: {ip} ({i+1})")
            
            result = analyze_privacy_llm(ip, ocr_content)
            writer.writerow({'IP': ip, **result})
            
            detected = [cat for cat, found in result.items() if found]
            print(f" -> 检测到: {', '.join(detected) if detected else '无'}")

            # API速率控制
            if (i + 1) % 5 == 0:
                print("...等待20秒以控制速率...")
                time.sleep(20)
            else:
                time.sleep(3)
    
    print(f"[+] 基于LLM的分析结果已保存到: {LLM_RESULTS_CSV}")
    print("--- 基于大模型的分析完成 ---")


if __name__ == '__main__':
    # 完整流程
    # 1. 对截图进行OCR
    perform_ocr_on_screenshots()
    
    # 2. 使用规则进行隐私分析
    analyze_privacy_rules()
    
    # 3. 使用大模型进行隐私分析
    analyze_privacy_with_llm()
    
    print("\n所有分析任务已完成！")
