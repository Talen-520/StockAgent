
import sys
import os
import unittest  

from src.tools import scrape_yahoo_finance_news  


class TestScraper(unittest.TestCase):
    def test_scrape_yahoo_finance_news(self):
        articles = scrape_yahoo_finance_news("NVDA")
        self.assertIsInstance(articles, list)
        self.assertGreater(len(articles), 0)

if __name__ == "__main__":
    unittest.main()