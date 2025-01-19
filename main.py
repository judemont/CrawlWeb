import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from database import Database
import socket
from utils import Utils
import random
import time
import threading

MAX_THEADS = 7
ENTRY_SITE = "https://news.ycombinator.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

def crawl(url: str, first = False):
    db = Database("data.db")

    headers = {
        "User-Agent": USER_AGENT
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        # print(e)
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
    description = soup.find("meta", attrs={"name": "keywords"})
    content = soup.get_text()[:200]

    contents = [(title, 10), (h1, 9), (description, 8), (content, 3)]
    contents = [c for c in contents if c[0] is not None]

    for content, score in contents:
        db.new_contents(site_id, content, score)

    print(f"{normalized_url}")
    

    for a in soup.find_all("a"):
        a_url = a.get("href")

        if a_url is None:
            continue

        if not a_url.startswith("http"):
            a_url = urljoin(url, a_url)

        if threading.active_count() < MAX_THEADS:
            time.sleep(random.randint(1, 3)/2)
            threading.Thread(target=crawl, args=(a_url,)).start()
        else:
            crawl(a_url)


if __name__ == "__main__":
    sites = Database("data.db").get_sites()
    if len(sites) == 0:
        crawl(ENTRY_SITE)
    else:
        crawl(sites[-1][1], first=True)