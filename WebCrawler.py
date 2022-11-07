import itertools
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from urllib.parse import urljoin, urlparse
import os
from AtomicCounter import Counter
from WebScraper import scrape_page, scrape_links, scrape_info

sys.setrecursionlimit(10000)

'''

The Crawler crawls the UIC domain starting from the URL https://cs.uic.edu, 
multi-threaded crawle simultaneously 10 worker threads scrape the UIC domain

'''


# Challenges - multithreading webscraping, redirected sites, .shtml, aspx pages,
# RecursionError: maximum recursion depth exceeded while calling a Python object
class WebCrawler:

    def __init__(self, base_url):

        self.base_url = base_url
        self.root_url = '{}://{}'.format(urlparse(self.base_url).scheme, urlparse(self.base_url).netloc)
        self.pool = ThreadPoolExecutor(max_workers=10)
        self.domain = 'uic.edu'
        self.atomicCounter = Counter(0)
        self.invalid_extensions = [".pdf", ".jpg", ".jpeg", ".doc", ".docx", ".ppt", ".pptx", ".png", ".txt", ".exe",
                                   ".ps", ".psb", ".shtml", ".aspx", "mailto:", ".html", ".php", ".asp", ".htm",
                                   "?", ".thmx"]
        # All the scraped pages
        self.crawled_pages = set([])
        self.dictionary = {}
        self.cont = itertools.count()
        # A queue representing the urls fetched and yet to be scraped
        self.to_crawl = Queue()
        # self.parent_list = defaultdict(list)

        # Adding the base url to the queue
        self.to_crawl.put(self.base_url)

    def is_valid_extension(self, url):
        if any(ext in url for ext in self.invalid_extensions):
            return False
        return True

    def parse_links(self, html, parent_url):
        links = scrape_links(html)
        for link in links:
            url = link['href']
            url = url.strip()
            if (url.startswith('/') or self.domain in url) and ('.com' not in url):
                url = urljoin(parent_url, url)
                # self.parent_list[parent_url].append(url)
                if url not in self.crawled_pages and '@' not in url and self.is_valid_extension(url):
                    if not url.endswith("/"):
                        url = url + "/"
                    if "https" in url:
                        url = url.replace("https", "http")
                    self.to_crawl.put(url)

    def delete_invalid_url(self, reason, url):
        url = url.replace("https", "http")
        print(f'{reason} -> {url}')
        self.dictionary = {key: val for key, val in self.dictionary.items() if val != url}
        if url in self.crawled_pages:
            self.crawled_pages.remove(url)

    def post_scrape_callback(self, res):
        if res is not None:
            result = res.result()
            if result:
                if result[3] == 200:
                    self.parse_links(result[0], result[1])
                    scrape_info(result[0], result[2])

    def run_scraper(self, num_pages):
        while True:
            try:
                target_url = self.to_crawl.get(timeout=120)  # wait for 120 sec for a page to add a url to be parsed
                if "https" in target_url:
                    target_url = target_url.replace("https", "http")
                if target_url not in self.crawled_pages:
                    self.crawled_pages.add(target_url)
                    if len(self.crawled_pages) <= num_pages:
                        self.atomicCounter.increment()
                        self.dictionary[self.atomicCounter.value()] = target_url
                        job = self.pool.submit(scrape_page, target_url, self.atomicCounter.value())
                        job.add_done_callback(self.post_scrape_callback)
                    else:
                        break
            except Exception as e:
                print(f'Exception is \n{e}')
                continue

    def store_crawled_pages(self):
        list1 = []
        for filename in os.listdir('/Users/rishabhgoel/Documents/Fall22/IR/Web-Search-Engine/uic-docs-text'):
            list1.append(int(filename[:-4]))

        main_list = list(set(self.dictionary.keys()).difference(list1))
        print(f'Missing docs = {main_list}')

        for key in main_list:
            del self.dictionary[key]

        with open("mapping.txt", "w") as f:
            for num, url in self.dictionary.items():
                f.write(f'{num} {url}\n')


if __name__ == '__main__':
    s = WebCrawler("https://cs.uic.edu")
    s.run_scraper(5000)
    s.pool.shutdown()
    s.store_crawled_pages()
