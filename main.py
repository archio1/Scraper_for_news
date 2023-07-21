import json
import requests
import csv
from newspaper import Config, Article
from newspaper.utils import BeautifulSoup
from datetime import datetime

HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

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

    return None

def extract_category(article):
    # Check for category information from various possible tags
    for tag in ['category', 'news_keywords', 'og:section', 'article:section']:
        if tag in article.meta_data:
            return article.meta_data[tag]
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
    category = extract_category(article)

    return {
        'Title': title,
        'Date': publish_date,
        'Author': authors,
        'Body': body,
        'Link': url,
        'Category': category
    }

def get_article_urls(target_date):
    base_url = 'https://tsn.ua'
    article_urls = []

    response = requests.get(base_url, headers=HEADERS, allow_redirects=True, verify=True, timeout=30)
    soup = BeautifulSoup(response.content, 'html.parser')

    for article in soup.find_all('article'):
        date_elem = article.find('time')
        if date_elem:
            date_str = date_elem.get('datetime')
            article_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z').date()

            if article_date == target_date.date():
                link = article.find('a')['href']
                article_urls.append(link)

    return article_urls

def main():
    target_date_str = "2023-07-21"
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d")

    csv_filename = "article.csv"
    fieldnames = ["Title", "Date", "Author", "Body", "Link", "Category"]

    articles = get_article_urls(target_date)
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for url in articles:
            article_info = extract_article_info(url)
            if article_info:  # Add a check to make sure article_info is not None
                writer.writerow(article_info)

if __name__ == "__main__":
    main()