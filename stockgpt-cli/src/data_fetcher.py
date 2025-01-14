import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import sys
from datetime import datetime, timedelta
import json

def fetch_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch comprehensive stock data using yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Fetch historical data
        data = ticker.history(start=start_date, end=end_date, interval="1d")
        if data.empty:
            raise ValueError(f"No data available for {symbol}")

        # Add company info
        info = ticker.info
        data['market_cap'] = info.get('marketCap', 0)
        data['sector'] = info.get('sector', 'Unknown')
        data['industry'] = info.get('industry', 'Unknown')
        
        # Add technical indicators
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['EMA_12'] = data['Close'].ewm(span=12).mean()
        data['EMA_26'] = data['Close'].ewm(span=26).mean()
        
        # Add volatility metrics
        data['Daily_Return'] = data['Close'].pct_change()
        data['Volatility'] = data['Daily_Return'].rolling(window=20).std() * (252 ** 0.5)  # Annualized
        
        # Add trading metrics
        data['Value_Traded'] = data['Close'] * data['Volume']
        data['Avg_Value_Traded'] = data['Value_Traded'].rolling(window=5).mean()
        
        return data

    except Exception as e:
        raise ValueError(f"Error fetching data for {symbol}: {str(e)}")

def fetch_news(symbol: str, limit: int = 5) -> list:
    """Fetch news from multiple sources and combine them"""
    news_items = []
    
    try:
        # 1. Yahoo Finance API
        news_items.extend(fetch_yahoo_news(symbol, limit))
        
        # 2. Alpha Vantage News (if you have API key)
        # news_items.extend(fetch_alpha_vantage_news(symbol, limit))
        
        # 3. Finviz News Scraping
        news_items.extend(fetch_finviz_news(symbol, limit))
        
        # Remove duplicates and limit items
        seen = set()
        unique_news = []
        for item in news_items:
            if item['title'] not in seen:
                seen.add(item['title'])
                unique_news.append(item)
        
        return unique_news[:limit]
        
    except Exception as e:
        print(f"Warning: Unable to fetch news for {symbol}: {str(e)}", file=sys.stderr)
        return [{'title': 'Error fetching news', 'link': '#'}]

def fetch_yahoo_news(symbol: str, limit: int) -> list:
    """Fetch news from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news[:limit]
        
        news_items = []
        for item in news:
            news_item = {
                'title': item.get('title', 'No title available'),
                'link': item.get('link', '#'),
                'publisher': 'Yahoo Finance',
                'published_date': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                'summary': item.get('summary', '')
            }
            news_items.append(news_item)
        return news_items
    except:
        return []

def fetch_finviz_news(symbol: str, limit: int) -> list:
    """Fetch news from Finviz"""
    try:
        url = f'https://finviz.com/quote.ashx?t={symbol}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_table = soup.find(id='news-table')
        
        news_items = []
        if news_table:
            rows = news_table.findAll('tr')
            for row in rows[:limit]:
                title = row.a.text
                link = row.a['href']
                date_data = row.td.text.strip().split(' ')
                
                news_items.append({
                    'title': title,
                    'link': link,
                    'publisher': 'Finviz',
                    'published_date': ' '.join(date_data),
                    'summary': ''
                })
        return news_items
    except:
        return []

def fetch_alpha_vantage_news(symbol: str, limit: int) -> list:
    """Fetch news from Alpha Vantage (requires API key)"""
    try:
        # You'll need to add your Alpha Vantage API key
        API_KEY = 'YOUR_ALPHA_VANTAGE_API_KEY'
        url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={API_KEY}'
        
        response = requests.get(url)
        data = response.json()
        
        news_items = []
        if 'feed' in data:
            for item in data['feed'][:limit]:
                news_items.append({
                    'title': item.get('title', 'No title available'),
                    'link': item.get('url', '#'),
                    'publisher': item.get('source', 'Alpha Vantage'),
                    'published_date': item.get('time_published', ''),
                    'summary': item.get('summary', '')
                })
        return news_items
    except:
        return []

def get_market_context() -> dict:
    """Get broader market context"""
    try:
        indices = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'NASDAQ'
        }
        
        context = {}
        for symbol, name in indices.items():
            index = yf.Ticker(symbol)
            info = index.info
            context[name] = {
                'change_percent': info.get('regularMarketChangePercent', 0),
                'price': info.get('regularMarketPrice', 0)
            }
            
        return context
    except Exception as e:
        print(f"Warning: Unable to fetch market context: {str(e)}", file=sys.stderr)
        return {}
