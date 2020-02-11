import argparse
import itertools
import logging
import time
import requests
import datetime
import os
from selenium import webdriver


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
    url_template = "https://google.com/webhp?#num={num_per_page}" \
                   "&start={page}&q={query}"
    url = url_template.format(num_per_page=num_per_page,
                              page=page,
                              query=query)
    logger.info(f"Fetching {page * num_per_page} results at {url}")
    browser.get(url)


def parse_search_results_page(browser, query, num_pages, num_per_page):
    pages = range(num_pages)
    num_per_page = num_per_page
    all_results = []
    for page in pages:
        load_page(browser, query, page, num_per_page)
        urls = scrape_urls(browser)
        all_results.extend(urls)
        time.sleep(0.1)

    return all_results


def save_file(content, filepath):
    with open(filepath) as f:
        f.write(content)


def download_and_save_pages(browser, urls, output_dir):
    for i, url in enumerate(urls, start=1):
        browser.get(url)
        content = browser.page_source
        timestamp = int(datetime.datetime.now().timestamp())
        filepath = os.path.join(output_dir, f"{i}_{timestamp}.html")
        save_file(content, filepath)


if __name__ == "__main__":
    args = parse_args()

    if not args.num_pages > 0:
        raise ValueError("'num_pages' expected to be positive")

    if not args.num_per_page > 0:
        raise ValueError("'num_per_page ecpected to be positive")

    if not args.query:
        raise ValueError("'query' should be non empty string")

    if args.executable_path and not os.path.isfile(args.executable_path):
        raise ValueError(
            f"'{args.executable_path}' not found or does not exist"
        )

    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    else:
        logger.warn(f"'{args.output_dir}' already exists")

    browser = start_browser(executable_path=args.executable_path)
    urls = parse_search_results_page(browser,
                                     args.query,
                                     args.num_pages,
                                     args.num_per_page)

    output_dir = args.output_dir
    download_and_save_pages(browser, urls, output_dir)
