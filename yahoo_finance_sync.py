import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def extract_article_details(url, headers):
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Title extraction
        title = soup.find('h1', class_='cover-title yf-1o1tx8g')
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

def scrape_yahoo_finance_news(stock):
    # Use the news-specific URL
    url = f"https://finance.yahoo.com/quote/{stock}/news/"
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

    # Extract details for each article
    articles = []
    for article_url in article_urls[:10]:  # Limit to first 10 articles
        article_details = extract_article_details(article_url, headers)
        if article_details:
            articles.append(article_details)

    # Save to JSON file
    filename = f"{stock}_news_articles.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(articles)} articles to {filename}")
    json_string = json.dumps(articles)

    return json_string

# Run the scraper
if __name__ == "__main__":
    stock = "NVDA"
    articles = scrape_yahoo_finance_news(stock)
    '''
    # Optional: Print articles to console
    for article in articles:
        print("\n--- Article ---")
        print(f"Title: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Timestamp: {article['timestamp']}")
        print("Content Preview:", article['content'][:1] if article['content'] else "No content")
    '''


# test script
'''

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

url = "https://finance.yahoo.com/video/jensen-huang-sets-nvidia-apart-220744099.html"

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Actual URL: {response.url}")
    
    # Check content type
    content_type = response.headers.get('Content-Type', '')
    print(f"Content Type: {content_type}")
    
    # Try parsing with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try to find titles or main content
    titles = soup.find_all(['h1', 'h2', 'title'])
    print("\nFound Titles:")
    for title in titles:
        print(title.text.strip())
    bodys = soup.find_all('p', class_='yf-1pe5jgt')
    print("\nFound Body:")
    for body in bodys:
        print(body.text.strip())
    

except requests.exceptions.RequestException as e:
    print(f"Error fetching the page: {e}")
'''