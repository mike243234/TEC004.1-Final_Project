import os
import json
import time
from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
}

def text_or(node, default=""):
    return node.get_text(" ", strip=True) if node else default

def attr_or(node, attr, default=""):
    if node is None:
        return default
    value = node.get(attr)
    if value:
        return value.strip()
    return node.get_text(" ", strip=True) or default

class BaseJobScraper(ABC):
    site_name = "base"
    prefix = "base"
    max_pages = 3
    delay = 1.0

    def __init__(self, raw_dir=None, max_pages=None):
        self.raw_dir = raw_dir
        if max_pages is not None:
            self.max_pages = max_pages
            
        # Khởi tạo cấu hình Selenium thay cho requests.Session()
        chrome_options = Options()
        chrome_options.add_argument("--headless") # Chạy ngầm, không mở giao diện
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument(f"user-agent={HEADERS['User-Agent']}")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=chrome_options
        )

    @abstractmethod
    def list_url(self, page):
        pass

    @abstractmethod
    def parse(self, html):
        pass

    def fetch_live(self, page):
        url = self.list_url(page)
        try:
            self.driver.get(url)
            time.sleep(3) 
            return self.driver.page_source 
        except Exception as e:
            print(f"Lỗi Selenium khi tải trang {url}: {e}")
            return ""

    def fetch_saved(self, page):
        if not self.raw_dir:
            return ""
        path = os.path.join(self.raw_dir, "{}_page_{}.html".format(self.prefix, page))
        if not os.path.exists(path):
            return ""
        with open(path, encoding="utf-8-sig") as handle: 
            return handle.read()

    def safe_parse(self, html):
        if not html:
            return []
        try:
            return self.parse(html)
        except Exception as e:
            print(f"Lỗi parse dữ liệu: {e}")
            return []

    def scrape_page(self, page):
        html = ""
        try:
            html = self.fetch_live(page)
        except Exception:
            html = ""
        jobs = self.safe_parse(html)
        if not jobs:
            jobs = self.safe_parse(self.fetch_saved(page))
        return jobs

    def scrape(self):
        results = []
        for page in range(1, self.max_pages + 1):
            jobs = self.scrape_page(page)
            for job in jobs:
                job["source"] = self.site_name
                results.append(job)
            if self.delay:
                time.sleep(self.delay)
                
        self.driver.quit() 
        return results