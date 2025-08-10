"""
This file is part of Abduallah Damash implementation
"""

import os
import time
import logging
import asyncio
import requests
import PyPDF2
from io import BytesIO
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import docx

# For Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# For Async Playwright
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

load_dotenv()  # Load env variables from .env if present

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# Ensure compatibility with Windows for Playwright subprocess management
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

class WebScraper:
    def __init__(self):
        self.visited_urls = set()
        # Read from an environment variable which backend to use
        self.scrape_backend = os.getenv("SCRAPE_BACKEND", "requests").lower()

    async def scrape_website(self, start_url):
        """
        Main entry point for scraping a URL. BFS-based approach:
        1) Gather sublinks in a queue (start with [start_url])
        2) For each link, parse content as HTML or PDF
        3) Skip images / non-text media

        If SCRAPE_BACKEND='selenium' or 'playwright', we delegate the BFS to the specialized method.
        Otherwise, we do BFS with the requests approach.
        """
        if self.scrape_backend == "selenium":
            logging.info(f"Scraping with Selenium for: {start_url}")
            loop = asyncio.get_event_loop()
            documents = []
            # Run the BFS in a thread executor, because Selenium is sync
            await loop.run_in_executor(None, self._bfs_selenium, start_url, documents)
            return documents

        elif self.scrape_backend == "playwright":
            logging.info(f"Scraping with Playwright for: {start_url}")
            return await self._bfs_playwright(start_url)

        else:
            # Default: requests-based BFS
            logging.info(f"Scraping with requests for: {start_url}")
            loop = asyncio.get_event_loop()
            documents = []
            # BFS in a thread, because requests is sync
            await loop.run_in_executor(None, self._bfs_requests, start_url, documents)
            return documents

    ##################################################
    # 1) Requests BFS
    ##################################################
    def _bfs_requests(self, start_url, documents):
        """
        BFS approach using the sync 'requests' library + BeautifulSoup.
        Skips images, parses PDF, gathers sublinks in a queue.
        """
        queue = [start_url]

        while queue:
            url = queue.pop(0)

            if url in self.visited_urls:
                continue

            self.visited_urls.add(url)
            logging.info(f"[Requests] Visiting: {url}")

            try:
                # HEAD to check content-type
                head_resp = requests.head(url, allow_redirects=True, timeout=10)
                ctype = head_resp.headers.get('Content-Type', '').lower()

                # PDF check
                if 'pdf' in ctype:
                    pdf_text = self._extract_pdf_content(url)
                    documents.append({"url": url, "content": pdf_text})
                    continue

                elif 'wordprocessingml.document' in ctype or 'msword' in ctype:
                    docx_text = self._extract_docx_content(url)
                    documents.append({"url": url, "content": docx_text})
                    continue

                # HTML check
                if 'text/html' in ctype:
                    # GET the HTML
                    headers = {
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/99.0.4844.84 Safari/537.36"
                        )
                    }
                    resp = requests.get(url, headers=headers, timeout=10)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "lxml")
                        text_content = self._extract_text(soup)
                        documents.append({"url": url, "content": text_content})

                        # Collect sublinks (BFS)
                        for link in soup.find_all("a", href=True):
                            sub_url = urljoin(url, link["href"])
                            if self._same_domain(start_url, sub_url) and sub_url.startswith(start_url):
                                if sub_url not in self.visited_urls:
                                    queue.append(sub_url)
                else:
                    # Non-text content
                    logging.info(f"[Requests] Skipped non-text content: {url}")

                time.sleep(0.5)  # mild rate limiting
            except Exception as e:
                logging.error(f"[Requests] Error visiting {url}: {e}", exc_info=True)

    ##################################################
    # 2) Selenium BFS
    ##################################################
    def _bfs_selenium(self, start_url, documents):
        """
        BFS approach using Selenium (sync).
        """
        queue = [start_url]

        while queue:
            url = queue.pop(0)
            if url in self.visited_urls:
                continue

            self.visited_urls.add(url)
            logging.info(f"[Selenium] Visiting: {url}")

            try:
                # HEAD request
                head_resp = requests.head(url, allow_redirects=True, timeout=10)
                ctype = head_resp.headers.get('Content-Type', '').lower()

                # PDF check
                if 'pdf' in ctype:
                    pdf_text = self._extract_pdf_content(url)
                    documents.append({"url": url, "content": pdf_text})
                    continue

                elif 'wordprocessingml.document' in ctype or 'msword' in ctype:
                    docx_text = self._extract_docx_content(url)
                    documents.append({"url": url, "content": docx_text})
                    continue

                # HTML check
                if 'text/html' in ctype:
                    # Use headless Chrome
                    chrome_options = Options()
                    chrome_options.add_argument("--headless")
                    chrome_options.add_argument("--disable-gpu")
                    chrome_options.add_argument("--no-sandbox")

                    driver = webdriver.Chrome(options=chrome_options)
                    driver.get(url)

                    # Wait for the <body> to appear
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "body"))
                        )
                    except Exception as e:
                        logging.warning(f"[Selenium] <body> not visible for {url}: {e}")

                    page_html = driver.page_source
                    driver.quit()

                    soup = BeautifulSoup(page_html, "lxml")
                    text_content = self._extract_text(soup)
                    documents.append({"url": url, "content": text_content})

                    # BFS sublinks
                    for link in soup.find_all("a", href=True):
                        sub_url = urljoin(url, link["href"])
                        if self._same_domain(start_url, sub_url) and sub_url.startswith(start_url):
                            if sub_url not in self.visited_urls:
                                queue.append(sub_url)
                else:
                    logging.info(f"[Selenium] Skipped non-text content: {url}")

                time.sleep(0.5)
            except Exception as e:
                logging.error(f"[Selenium] Error visiting {url}: {e}", exc_info=True)

    ##################################################
    # 3) Playwright BFS (Async)
    ##################################################
    async def _bfs_playwright(self, start_url):
        """
        BFS approach using async Playwright.
        """
        documents = []
        queue = [start_url]

        while queue:
            url = queue.pop(0)
            if url in self.visited_urls:
                continue

            self.visited_urls.add(url)
            logging.info(f"[Playwright] Visiting: {url}")

            try:
                # HEAD request to check content-type
                # (We can do an async HTTP request, but let's keep it simple with requests in a thread)
                loop = asyncio.get_event_loop()
                head_resp = await loop.run_in_executor(
                    None, lambda: requests.head(url, allow_redirects=True, timeout=10)
                )
                ctype = head_resp.headers.get('Content-Type', '').lower()

                # PDF check
                if 'pdf' in ctype:
                    pdf_text = await self._extract_pdf_content_async(url)
                    documents.append({"url": url, "content": pdf_text})
                    continue

                elif 'wordprocessingml.document' in ctype or 'msword' in ctype:
                    docx_text = self._extract_docx_content(url)
                    documents.append({"url": url, "content": docx_text})
                    continue

                # HTML check
                if 'text/html' in ctype:
                    # Launch Playwright
                    async with async_playwright() as pw:
                        browser = await pw.chromium.launch(headless=True)
                        context = await browser.new_context()
                        page = await context.new_page()

                        await page.goto(url, timeout=20000)

                        # Attempt to wait for <body> or main
                        try:
                            await page.wait_for_selector("body", timeout=10000)
                        except PlaywrightTimeoutError:
                            logging.warning(f"[Playwright] Timeout waiting for <body> on {url}")

                        # (Optional) infinite scroll or other advanced steps
                        await self._playwright_infinite_scroll_async(page)

                        page_html = await page.content()
                        await browser.close()

                    soup = BeautifulSoup(page_html, "lxml")
                    text_content = self._extract_text(soup)
                    documents.append({"url": url, "content": text_content})

                    # BFS sublinks
                    links = soup.find_all("a", href=True)
                    for link in links:
                        sub_url = urljoin(url, link["href"])
                        if self._same_domain(start_url, sub_url) and sub_url.startswith(start_url):
                            if sub_url not in self.visited_urls:
                                queue.append(sub_url)
                else:
                    logging.info(f"[Playwright] Skipped non-text content: {url}")

                await asyncio.sleep(0.5)
            except Exception as e:
                logging.error(f"[Playwright] Error visiting {url}: {e}", exc_info=True)

        return documents

    async def _playwright_infinite_scroll_async(self, page, pause_time=2, max_scroll=2):
        """
        Example infinite scroll with Playwright (async).
        We limit max_scroll to 2 by default to avoid infinite loops or big overhead.
        """
        logging.info("[Playwright] Starting infinite scrolling...")
        last_height = await page.evaluate("document.body.scrollHeight")
        scroll_count = 0

        while scroll_count < max_scroll:
            scroll_count += 1
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(pause_time * 1000)
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                logging.info("[Playwright] No new content after scrolling.")
                break
            last_height = new_height

        logging.info("[Playwright] Infinite scrolling complete.")

    ##################################################
    # Utility Functions
    ##################################################
    def _extract_pdf_content(self, url):
        """
        Download and parse PDF content using PyPDF2 (sync).
        """
        logging.info(f"Extracting PDF from {url}")
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            with BytesIO(resp.content) as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                text_parts = []
                for page in reader.pages:
                    text_parts.append(page.extract_text() or "")
                return "\n".join(text_parts)
        except Exception as e:
            logging.error(f"Failed to extract PDF from {url}: {e}", exc_info=True)
            return "[PDF extraction failed]"

    def _extract_docx_content(self, url):
        """
        Download and parse Docx content.
        """
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            with BytesIO(resp.content) as f:
                doc = docx.Document(f)
                full_text = []
                for para in doc.paragraphs:
                    full_text.append(para.text)
                return "\n".join(full_text)
        except Exception as e:
            logging.error(f"Failed to extract DOCX from {url}: {e}", exc_info=True)
            return "[DOCX extraction failed]"

    async def _extract_pdf_content_async(self, url):
        """
        Async version to parse PDF content with PyPDF2 (still sync internally).
        We just run it in an executor, so it doesn't block the event loop.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._extract_pdf_content(url))

    def _extract_text(self, soup):
        """
        Basic text extraction from HTML, removing scripts/styles.
        """
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        return soup.get_text(separator=" ", strip=True)

    def _same_domain(self, base_url, new_url):
        """
        Basic check if new_url is on the same domain as base_url.
        """
        try:
            base_domain = base_url.split("//", 1)[1].split("/", 1)[0]
            new_domain = new_url.split("//", 1)[1].split("/", 1)[0]
            return base_domain in new_domain
        except IndexError:
            return False
