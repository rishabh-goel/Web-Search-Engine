import itertools
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from urllib.parse import urljoin, urlparse

from AtomicCounter import Counter
from WebScraper import scrape_page, scrape_links, scrape_info

'''

The Crawler crawls the UIC domain starting from the URL https://cs.uic.edu, 
multi-threaded crawle simultaneously 10 worker threads scrape the UIC domain

'''


# Challenges - multithreading webscraping, redirected sites, .shtml pages
class WebCrawler:

    def __init__(self, base_url):

        self.base_url = base_url
        self.root_url = '{}://{}'.format(urlparse(self.base_url).scheme, urlparse(self.base_url).netloc)
        self.pool = ThreadPoolExecutor(max_workers=10)
        self.domain = 'uic.edu'
        self.atomicCounter = Counter(0)
        self.invalid_extensions = ["pdf", "jpg", "jpeg", "doc", "docx", "ppt", "pptx", "png", "txt", "exe", "ps", "psb",
                                   "shtml", "aspx"]
        # All the scraped pages
        self.crawled_pages = set([])
        self.dictionary = {}
        self.cont = itertools.count()
        self.counter = 0
        # A queue representing the urls fetched and yet to be scraped
        self.to_crawl = Queue()

        # Adding the base url to the queue
        self.to_crawl.put(self.base_url)

    def is_valid_extension(self, url):
        if True in [ext in url for ext in self.invalid_extensions]:
            return False
        return True

    def parse_links(self, html):
        links = scrape_links(html)
        for link in links:
            url = link['href']
            if (url.startswith('/') or self.domain in url) and ('.com' not in url):  # run only in the uic.edu domain
                url = urljoin(self.root_url, url)
                if url not in self.crawled_pages and '@' not in url and self.is_valid_extension(url):
                    if not url.endswith("/"):
                        url = url + "/"  # appending / in the end to avoid duplicate runs
                    if "https" not in url:
                        url = url.replace("http", "https")
                    self.to_crawl.put(url)

    def post_scrape_callback(self, res):
        if res is not None:
            result = res.result()
            if result[0] and result[0].status_code == 200:
                self.parse_links(result[0].text)
                scrape_info(result[0].text, result[2])

    def run_scraper(self, num_pages):
        while True:
            try:
                target_url = self.to_crawl.get(timeout=120)  # wait for 120 sec for a page to add a url to be parsed
                if target_url not in self.crawled_pages:
                    self.crawled_pages.add(target_url)
                    if len(self.crawled_pages) <= num_pages:
                        self.atomicCounter.increment()
                        self.dictionary[self.atomicCounter.value()] = target_url
                        job = self.pool.submit(scrape_page, target_url, self.atomicCounter.value())
                        job.add_done_callback(self.post_scrape_callback)
                    elif len(self.crawled_pages) > num_pages:
                        break
            except Empty:
                return
            except Exception as e:
                print(e)
                continue

    def store_crawled_pages(self):
        with open("mapping.txt", "w+") as f:
            for num, url in self.dictionary.items():
                f.write(f'{num} {url}\n')


if __name__ == '__main__':
    s = WebCrawler("https://cs.uic.edu")
    s.run_scraper(4000)
    s.store_crawled_pages()
