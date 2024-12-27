import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
def extract_article_details(url: str, headers: str) -> list  :
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Title extraction
        title = soup.find('div', class_='cover-title yf-1at0uqp')
        title_text = title.text.strip() if title else "No title found"

        # Content extraction
        contents = soup.find_all('p', class_='yf-1pe5jgt')
        content_text = [content.text.strip() for content in contents if content.text.strip()]

        # Time extraction
        time_element = soup.find('time', class_='byline-attr-meta-time')
        article_time = time_element['datetime'] if time_element and time_element.has_attr('datetime') else None

        return {
            'title': title_text,
            'content': content_text,
            'url': url,
            'timestamp': article_time
        }
    except Exception as e:
        print(f"Error extracting details from {url}: {e}")
        return None

def scrape_yahoo_finance_news(stock: str) -> list:
    # Use the news-specific URL
    url = f"https://finance.yahoo.com/quote/{stock}/news/"

    # Optional
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Send request
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract article URLs
    links = soup.find_all('div', class_='yf-18q3fnf')
    article_urls = [
        link.find('a')['href'] 
        for link in links 
        if link.find('a') and link.find('a').has_attr('href') and link.find('a')['href'].startswith('https://finance.yahoo.com/')
    ]

    articles = []
    # Limit to first 10 articles
    for article_url in article_urls[:10]:
        article_details = extract_article_details(article_url, headers)
        if article_details:
            articles.append(article_details)

    # Save to JSON file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    os.makedirs(data_dir, exist_ok=True)
    filename = f"{stock}_news_articles.json"
    filepath = os.path.join(data_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(articles)} articles to {filename}")
    
    return articles  # Return the list directly

# Run the scraper
if __name__ == "__main__":
    stock = "NVDA"
    articles = scrape_yahoo_finance_news(stock)
