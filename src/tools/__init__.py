# myproject/src/tools/__init__.py
from .yahoo_finance_sync import *
from .market_watch_sync import scrape_market_watch_news
from .web_search import web_search
from .audio_to_text import speech_to_text
__all__ = [
    'scrape_yahoo_finance_news',
    'scrape_market_watch_news',
    'web_search'
    'speech_to_text'
]