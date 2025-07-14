from playwright.sync_api import sync_playwright
import requests
import os
import time
import glob
import json
import random
def download_transcript_and_audio(url, output_dir="output", title='A'):
    os.makedirs(output_dir, exist_ok=True)
    with sync_playwright() as p:
        browser =  browser = p.chromium.connect_over_cdp("http://localhost:9333")

        # page = browser.new_page()
        contexts = browser.contexts
        page = contexts[0].pages[0]  # 获取第一个 context 的第一个 page
        page.goto(url, timeout=60000)
        # page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")  # 等待初次加载完成
        # page.reload()
        # page.wait_for_load_state("networkidle")  # 再次确保加载完
        page.wait_for_selector('div[data-test-id="content-container"]', timeout=10000)

        # 提取 transcript 内容
        transcript_div = page.locator('div[data-test-id="content-container"].T2G6W')
        transcript_text = transcript_div.inner_text()
        with open(f"{output_dir}/{title}.txt", "w", encoding="utf-8") as f:
            f.write(transcript_text)
        print("✅ Transcript 已保存到 transcript.txt")

        # 查找 audio 链接
        # SeekingAlpha 的 transcript 页面通常会有音频 player 标签或链接
        # 判断是否存在 audio 元素
        # 1️⃣ 点击 play-button（如果有）
        # 等待按钮出现并点击
        # page.wait_for_selector('button[data-test-id="play-button"]', timeout=5000)
        # page.wait_for_selector('button[data-test-id="play-button"]', timeout=5000)
        # page.locator('button[data-test-id="play-button"]').first.click()
        # page.locator('button[data-test-id="play-button"]').nth(1).click()
        # buttons = page.locator('button[data-test-id="play-button"]')
        # for i in range(buttons.count()):
        #     btn = buttons.nth(i)
        #     if btn.is_visible():
        #         btn.click()
        #         break
        # time.sleep(2)

        # # 方法一：根据 aria-label 属性
        # download_button = page.query_selector('button[aria-label="download"]')
        # if download_button:
        #     download_button.click()
        #     print("✅ 下载按钮已点击")
        # else:
        #     print("❌ 没有找到下载按钮")

        # time.sleep(30)

        # # 方法一：根据 aria-label 属性 close-modal-button
        # download_button = page.query_selector('button[data-test-id="close-modal-button"]')
        # if download_button:
        #     download_button.click()
        #     print("✅ 关闭按钮已点击")
        # else:
        #     print("❌ 没有找到关闭按钮")


        browser.close()

import re

def sanitize_filename(title):
    # 替换掉文件名中不允许的字符
    return re.sub(r'[<>:"/\\|?*]', '_', title)

should_restart = False  # 全局变量，控制是否重新爬数据

def check_ticker_and_set_flag(ticker):
    global should_restart
    if ticker == 'SCI':
        should_restart = True
        print("✅ 检测到 ticker, 标记为重新开始抓取")

if __name__ == "__main__":
    file_list = glob.glob("/Users/qiqi1996amelia/Downloads/seekingalpha/1/*.json")
    loaded_list = glob.glob("/Users/qiqi1996amelia/Downloads/transcript/*.txt")
    for file in file_list:

        ticker = os.path.splitext(os.path.basename(file))[0].split("_")[-1]
        print(ticker)
        check_ticker_and_set_flag(ticker)
        if should_restart:
            # 假设文件名为 transcripts.json
            with open( file, 'r') as f:
                data = json.load(f)
            
            

            # 提取 link 和 title
            results = [(item['title'], item['link']) for item in data]

            # 输出结果
            for  title, link in results:
                safe_title = sanitize_filename(title)
                matched = any(safe_title in filename for filename in loaded_list)
                if not matched:
                    print(f"Title: {title}")
                    
                    clean_url = link.split('#')[0]
                    if 'Earnings' in title:
                        download_transcript_and_audio( clean_url, f'/Users/qiqi1996amelia/Downloads/transcript/{ticker}', safe_title)
                        delta_y = random.randint(10, 20)
                        time.sleep(delta_y)