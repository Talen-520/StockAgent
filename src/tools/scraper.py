import requests
from bs4 import BeautifulSoup

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