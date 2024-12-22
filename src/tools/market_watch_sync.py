import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def extract_article_details(url, headers):
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Title extraction
        title = soup.find('h1', class_='article__headline css-14q97tr')
        title_text = title.text.strip() if title else "No title found"

        # Content extraction
        contents = soup.find_all('p')
        content_text = [content.text.strip() for content in contents if content.text.strip()]

        # Time extraction
        time_element = soup.find('time')
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

def scrape_market_watch_news(stock):
    # Use the news-specific URL
    url = f"https://www.marketwatch.com/investing/stock/{stock}?mod=search_symbol"

    # More comprehensive headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.marketwatch.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    # Send request with headers
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")

    # Check if request was successful
    if response.status_code != 200:
        print("Failed to retrieve the page. Response content:")
        print(response.text)
        return json.dumps([])

    soup = BeautifulSoup(response.text, 'html.parser')

    # More comprehensive URL extraction
    article_urls = []
    
    # Try multiple selectors
    selectors = [
        'h3.article__headline a.link',
        'div.article__headline a',
        'a.article__headline'
    ]

    for selector in selectors:
        links = soup.select(selector)
        urls = [
            link.get('href') 
            for link in links 
            if link.get('href') and 'marketwatch.com/story/' in link.get('href')
        ]
        article_urls.extend(urls)

    # Remove duplicates
    article_urls = list(dict.fromkeys(article_urls))

    print(f"Found {len(article_urls)} articles")
    print("Article URLs:", article_urls)

    # Extract details for each article  
    articles = []
    for article_url in article_urls[:10]:  # Limit to first 10 articles
        try:
            article_details = extract_article_details(article_url, headers)
            if article_details:
                articles.append(article_details)
        except Exception as e:
            print(f"Error extracting details for {article_url}: {e}")

    print(f"Saved {len(articles)} articles")
    json_string = json.dumps(articles)

    filename = f"{stock}_news_articles_marketWatch.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    return json_string

# Run the scraper
if __name__ == "__main__":
    stock = "NVDA"
    articles = market_watch_news(stock)
