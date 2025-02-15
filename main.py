import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from database import Database
import socket
from utils import Utils
import random
import time
from concurrent.futures import ThreadPoolExecutor

MAX_THREADS = 20
ENTRY_SITE = "https://news.ycombinator.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

def crawl(url: str, first=False):
    db = Database("data.db")

    headers = {
        "User-Agent": USER_AGENT
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return
    
    soup = BeautifulSoup(response.text, "html.parser")

    normalized_url = Utils.normalize_url(url)

    sites = db.get_sites(url=normalized_url)
    if len(sites) > 0 and not first:
        return

    db.new_site(normalized_url, int(time.time()), 0)
    site_id = db.get_sites(url=normalized_url)[0][0]

    title = soup.title.string
    h1 = soup.h1.string if soup.h1 is not None else None
    description = soup.find("meta", attrs={"name": "description"})
    description = description["content"] if description else None
    keywords = soup.find("meta", attrs={"name": "keywords"})
    keywords = keywords["content"] if keywords else None
    content = soup.get_text()[:1000]

    contents = [(title, 10), (h1, 9), (description, 8), (keywords, 7), (content, 3)]
    contents = [c for c in contents if c[0] is not None]

    for content, score in contents:
        db.new_contents(site_id, content, score)

    print(f"{normalized_url}")

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for a in soup.find_all("a"):
            a_url = a.get("href")

            if a_url is None:
                continue

            if not a_url.startswith("http"):
                a_url = urljoin(url, a_url)

            futures.append(executor.submit(crawl, a_url))

        for future in futures:
            future.result()

if __name__ == "__main__":
    sites = Database("data.db").get_sites()
    if len(sites) == 0:
        crawl(ENTRY_SITE)
    else:
        crawl(sites[-1][1], first=True)