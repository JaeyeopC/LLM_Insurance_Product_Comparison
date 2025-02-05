import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote
from langchain.schema import Document
from langchain_community.document_transformers import Html2TextTransformer
from typing import Dict

def crawl_company_websites(companies, max_pages=200):
    crawl_results = {}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }

    for company in companies:
        company_name = company['name'].lower().replace(' ', '_')
        start_url = company['url']
        visited_urls = set()
        to_visit = [start_url]
        pages_crawled = 0

        try:
            while to_visit and pages_crawled < max_pages:
                url = to_visit.pop(0)
                if url in visited_urls:
                    continue

                response = requests.get(url, headers=headers)
                response.raise_for_status()

                page_filename = generate_filename_from_url(url)
                filename = os.path.join(company_name, page_filename)

                crawl_results[filename] = response.text

                soup = BeautifulSoup(response.content, 'html.parser')
                visited_urls.add(url)
                pages_crawled += 1

                for link in soup.find_all('a', href=True):
                    full_url = urljoin(url, link['href'])
                    if is_internal_link(start_url, full_url) and full_url not in visited_urls:
                        to_visit.append(full_url)

        except Exception as e:
            print(f"Error crawling {company['name']}: {e}")

    return crawl_results

def is_internal_link(base_url, test_url):
    base_domain = urlparse(base_url).netloc
    test_domain = urlparse(test_url).netloc
    return base_domain == test_domain

def generate_filename_from_url(url):
    parsed_url = urlparse(url)
    path = parsed_url.path if parsed_url.path else "home"
    path = path.strip("/").replace("/", "_")
    query = parsed_url.query
    if query:
        path += "_" + quote(query, safe="")
    filename = f"{path}.html"
    return filename


