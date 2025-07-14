from playwright.sync_api import sync_playwright
import time
import json
import threading
import random


stop_signal = False  # 用于中断滚动线程

def listen_for_enter():
    global stop_signal
    input("📨 按 Enter 停止自动滑动并开始提取内容...")
    stop_signal = True

def scroll_page(page):
    prev_height = 0
    same_count = 0
    max_same = 5  # 连续 5 次滑动高度未变化，认定到底

    while True:
        # 随机滚轮滑动：模拟人行为
        delta_y = random.randint(500, 3000)
        page.mouse.wheel(0, delta_y)
        time.sleep(random.uniform(1.2, 2.5))

        # 检查当前页面可视高度，计算滚动位置
        curr_height = page.evaluate("() => window.innerHeight + window.scrollY")

        # 持续到底的判断
        if curr_height == prev_height:
            same_count += 1
            if same_count >= max_same:
                print("🛑 可能已到底，停止滚动。")
                break
        else:
            same_count = 0
            prev_height = curr_height
def connect_to_existing_chrome_and_scrape(target_url, ticker_name):
    with sync_playwright() as p:
        # 连接到已开启远程调试端口的 Chrome
        browser = p.chromium.connect_over_cdp("http://localhost:9333")

        # # 获取所有已有页面
        context = browser.contexts[0]
        pages = context.pages
        

        # 找到当前正在浏览 SeekingAlpha 的页面（可按标题或 URL 匹配）
        for page in pages:
            if "seekingalpha.com" in page.url:
                # print(f"✅ 找到目标页面: {page.url}")

                break
        else:
            raise ValueError("❌ 没有找到包含 seekingalpha.com 的页面，请先用 Chrome 打开该页面")
        page.goto(target_url, timeout=60000)
        print("🚀 开始自动滚动页面加载内容...")


        # 启动滚动线程
        scroll_page(page)


        articles = page.query_selector_all('article[data-test-id="post-list-item"]')
        print(f"📄 共找到 {len(articles)} 篇文章")

        results = []
        for article in articles:
            title_elem = article.query_selector('a[data-test-id="post-list-item-title"]')
            date_elem = article.query_selector('span[data-test-id="post-list-date"]')
            symbol_elems = article.query_selector_all('a[data-test-id="post-list-ticker"]')

            title = title_elem.inner_text().strip() if title_elem else None
            link = title_elem.get_attribute('href') if title_elem else None
            date = date_elem.inner_text().strip() if date_elem else None
            symbols = [s.inner_text().strip() for s in symbol_elems]

            results.append({
                "title": title,
                "link": f"https://seekingalpha.com{link}" if link else None,
                "date": date,
                "symbols": symbols,
            })

        print(json.dumps(results[:3], indent=2))
        with open(f"/Users/qiqi1996amelia/Downloads/seekingalpha_articles_{ticker_name}.json", "w") as f:
            json.dump(results, f, indent=2)

        print("✅ 数据保存完成")

if __name__ == "__main__":
    ticker_list = [
       'NTGR', 'NEU', 'NWL', 'NKE', 'NDSN', 'NWPX', 'NCLH', 'NOV', 'NRG',
       'NUS', 'NUE', 'OI', 'OXY', 'OII', 'ODC', 'OIS', 'ODFL', 'OSBC',
       'OLN', 'ZEUS', 'OMC', 'OTEX', 'KAR', 'ORN', 'OSK', 'OSIS', 'OMI'
       ]
    for ticker in ticker_list:
     
        url = f'https://seekingalpha.com/author/sa-transcripts/analysis?ticker={ticker}'
        connect_to_existing_chrome_and_scrape(url, ticker)
