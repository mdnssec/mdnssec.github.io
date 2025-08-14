import asyncio
import csv
import os
from playwright.async_api import async_playwright, Error as PlaywrightError

# --- 配置参数 ---
# 输入文件，包含IP地址列表
IP_LIST_FILE = "ip_list.csv"
# 输出目录
OUTPUT_DIR = "output"
# 截图保存的子目录
SCREENSHOTS_DIR = os.path.join(OUTPUT_DIR, "screenshots")
# 成功截图的IP日志
SUCCESS_LOG = os.path.join(OUTPUT_DIR, "successful_ips.txt")
# 并发任务数
MAX_CONCURRENCY = 10
# 页面加载超时时间（毫秒）
PAGE_TIMEOUT = 8000

def setup_directories():
    """创建输出目录"""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def load_ips(csv_file: str) -> list[str]:
    """从CSV文件中加载IP地址列表"""
    if not os.path.exists(csv_file):
        print(f"错误: IP列表文件 '{csv_file}' 未找到。")
        return []
    with open(csv_file, newline='', encoding='utf-8') as f:
        # 过滤空行
        return [row[0].strip() for row in csv.reader(f) if row and row[0].strip()]

async def capture_ip(ip: str, semaphore: asyncio.Semaphore):
    """
    使用Playwright捕获单个IP地址的网页截图。
    会依次尝试 http 和 https 协议。
    """
    async with semaphore:
        browser = None
        context = None
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(ignore_https_errors=True)
                page = await context.new_page()

                for scheme in ["http://", "https://"]:
                    url = f"{scheme}{ip}"
                    try:
                        print(f"[*] 正在尝试: {url}")
                        await page.goto(url, timeout=PAGE_TIMEOUT)
                        
                        # 使用IP地址创建有效的文件名
                        safe_ip = ip.replace(':', '_').replace('/', '_')
                        screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{safe_ip}.png")
                        
                        await page.screenshot(path=screenshot_path)
                        print(f"[+] 截图成功: {screenshot_path}")
                        
                        # 异步写入成功日志
                        async with asyncio.Lock():
                            with open(SUCCESS_LOG, "a", encoding='utf-8') as log:
                                log.write(f"{url}\n")
                        return  # 成功后即返回

                    except Exception as e:
                        error_message = str(e).splitlines()[0]
                        print(f"[-] 访问失败 {url}: {e.__class__.__name__}: {error_message}")

        except PlaywrightError as e:
            print(f"[!] Playwright初始化错误 for {ip}: {str(e)}")
        finally:
            if context:
                await context.close()
            if browser:
                await browser.close()

async def main():
    """主函数，设置并运行并发截图任务"""
    setup_directories()
    ip_list = load_ips(IP_LIST_FILE)
    if not ip_list:
        print("IP列表为空，程序退出。")
        return

    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = [capture_ip(ip, semaphore) for ip in ip_list]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("--- 开始网页截图 ---")
    asyncio.run(main())
    print("--- 截图任务完成 ---")
