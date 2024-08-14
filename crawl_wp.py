from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import argparse

parser = \
    argparse.ArgumentParser(epilog='Command : python3 crawl_wp.py -l "http://test01.local/"'
                            )
parser.add_argument('-l',
                    help='Add link with parameter as "http://test01.local/"',
                    required=True)
args = parser.parse_args()
url = args.l
crawl = {url}
visited = set()

while crawl:
    url = crawl.pop()
    resp = requests.get(url)

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, "html.parser")
        links = [a.get("href") for a in soup.find_all("a", href=True)]
        links = [urljoin(url, link) if link.startswith("#") else link for link in links]
        crawl_url = [link for link in links if link.startswith(f"{url}")]
        crawl.update({link for link in crawl_url if link not in visited})
        visited.add(url)
    else:
        print(f"Failed Links: {url}")

print("Exported Links:")
for url in visited:
    print(url)
    