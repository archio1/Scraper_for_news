import csv
import json
from newspaper import Config, Article
from newspaper.utils import BeautifulSoup


def extract_author(article):
    # Check for author information from various possible tags
    for tag in ['author', 'byline', 'dc.creator', 'byl']:
        if tag in article.meta_data:
            return article.meta_data[tag]

    # If author not found in meta_data, try to extract from JSON-LD
    soup = BeautifulSoup(article.html, 'html.parser')
    script_tag = soup.find("script", {"type": "application/ld+json"})
    if script_tag:
        try:
            json_data = json.loads(script_tag.contents[0])
            if 'author' in json_data:
                return json_data['author']['name']
        except json.JSONDecodeError:
            pass

    # If author not found, return None
    return None

def extract_article_info(url):
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    config.request_timeout = 10

    article = Article(url, config=config)
    article.download()
    article.parse()

    title = article.title
    publish_date = article.publish_date
    body = article.text
    authors = extract_author(article)


    return {
        'Title': title,
        'Date': publish_date,
        'Author': authors,
        'Body': body,
        'Link': url,
    }


tsn_urls = [
    'https://tsn.ua/tsikavinki/hlopchik-upiymav-ribu-z-idealnimi-lyudskimi-zubami-foto-2374234.html',
    # Add more URLs here
]


csv_filename = 'tsn_article.csv'
fieldnames = ['Title', 'Date', 'Author', 'Body', 'Link']

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for url in tsn_urls:
        article_info = extract_article_info(url)
        writer.writerow(article_info)