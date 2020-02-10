import argparse
import itertools
import logging
import time
import requests

from selenium import webdriver

# TODO: 
#   1. Finish first version of script
#   2. Rewrite on Scrapy
#   3. Add unit tests


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable-path",
                        required=False,
                        default=None,
                        help="Path to Firefox driver executable")
    parser.add_argument("--output-dir", 
                        required=True, 
                        help="Directory where to save pages")
    parser.add_argument("--query",
                        required=True,
                        help="Search query")
    parser.add_argument("--num-per-page", 
                        type=int,
                        default=100, 
                        help="Number of pages with results")
    parser.add_argument("--num-pages", 
                        type=int,
                        default=1, 
                        help="Number of results per page")
    args = parser.parse_args()
    return args


def start_browser(options=None, executable_path=None):
    kwargs = {
        "options": options,
        "executable_path": executable_path or "geckodriver"
    }
    browser = webdriver.Firefox(**kwargs)
    return browser


def scrape_urls(browser):
    links = browser.find_elements_by_xpath("//h3[@class='r']/a[@href]")
    
    urls = []
    for link in links:
        url = link.get_attribute("href")
        urls.append(url)

    return urls


def load_page(browser, query, page, num_per_page):
    url_template = "https://google.com/webh?#num={num_per_page}" \
                   "&start={page}&q={query}"
    url = url_template.format(num_per_page=num_per_page, 
                              page=page, 
                              query=query)
    logger.info(f"Fetching {page * num_per_page} results at {url}")
    browser.get(url)


def parse_results_page(num_pages, num_per_page):
    browser = start_browser()

    pages = range(num_pages)
    num_per_page = num_per_page

    all_results = []
    for page in pages:
        load_page(browser, args.query, page, num_per_page)
        urls = scrape_urls(browser)
        for url in urls:
            # Download 
            # result = browser.get()
            all_results.append()
        all_results.extend(urls)
        time.sleep(0.1)

    return all_results


# def download_page(url, headers=None):
#     try: 
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#     except:
#         logger.error(f"Failed to download page: {url}")

#     content = None
#     if response:
#         content = response.content
    
#     return content.encode("utf-8") if content else None 


if __name__ == "__main__":
    args = parse_args()

    if args.num_pages > 0:
        raise ValueError("'num_pages' expected to be positive")
    
    if args.num_per_page > 0:
        raise ValueError("'num_per_page ecpected to be positive")

    if not args.query:
        raise ValueError("'query' should be non empty string")

    urls = parse_urls(args.num_pages, args.num_per_page)
    contents = []
    for url in urls:
        content = download_page(url, headers)

