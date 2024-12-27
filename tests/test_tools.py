import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))  # Add src to PATH, adjust the path based on the file location
import unittest  
from tools import scrape_yahoo_finance_news  # Import from tools package


class TestScraper(unittest.TestCase):
    def test_scrape_yahoo_finance_news(self):
        articles = scrape_yahoo_finance_news("NVDA")
        self.assertIsInstance(articles, list)
        self.assertGreater(len(articles), 0)

if __name__ == "__main__":
    unittest.main()