from .yahoo_finance_sync import scrape_yahoo_finance_news
from .market_watch_sync import scrape_market_watch_news

__all__ = [
    'scrape_yahoo_finance_news',
    'scrape_market_watch_news',
]