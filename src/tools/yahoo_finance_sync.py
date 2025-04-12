import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import re
def extract_article_details(url: str, headers: str) -> list  :
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Title extraction
        title_element = soup.find(class_=re.compile(r'cover-title yf-\w+'))
        title_text = title_element.get_text().strip() if title_element else "No title found"
        
        # Content extraction
        content_text = soup.find('div', class_='atoms-wrapper')
        paragraphs = []
        for p in content_text.find_all('p'):
            # 过滤掉空段落或特定内容的段落
            text = p.get_text().strip()
            if text and not text.startswith(('Read more:', 'Related:', 'Follow us on')):
                # 清理文本中的特殊字符和多余空格
                text = re.sub(r'[\xa0\u200b]+', ' ', text)
                text = re.sub(r'\s+', ' ', text)
                paragraphs.append(text)
        
        content_text = '\n\n'.join(paragraphs)

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
    print("Starting scrape_yahoo_finance_news function")
    url = f"https://finance.yahoo.com/quote/{stock}/news/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract article URLs with deduplication
    links = soup.select('div[class*="holder yf-"] a[href^="https://finance.yahoo.com/"]')
    seen_urls = set()
    unique_article_urls = []
    
    for a in links:
        url = a['href']
        # Normalize URL by removing query parameters and fragments
        clean_url = url.split('?')[0].split('#')[0]
        if clean_url not in seen_urls:
            seen_urls.add(clean_url)
            unique_article_urls.append(url)
    
    articles = []
    print(f"Found {len(unique_article_urls)} unique articles, processing first 10")
    
    for article_url in unique_article_urls[:10]:
        article_details = extract_article_details(article_url, headers)
        if article_details:
            articles.append(article_details)

    # Save to JSON file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    os.makedirs(data_dir, exist_ok=True)
    filename = f"{stock}_news_articles.json"
    
    with open(os.path.join(data_dir, filename), 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(articles)} unique articles to {filename}")
    return articles

# Run the scraper
if __name__ == "__main__":
    print("Running the script directly")
    stock = "NVDA"
    print(f"Scraping news for stock: {stock}")
    articles = scrape_yahoo_finance_news(stock)
