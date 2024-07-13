import yfinance as yf
import pandas as pd
from pandas_datareader import data as pdr
import requests
from bs4 import BeautifulSoup

def fetch_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch stock data using yfinance"""
    try:
        yf.pdr_override()
        data = pdr.get_data_yahoo(symbol, start=start_date, end=end_date)
        if data.empty:
            raise ValueError(f"No data available for {symbol} in the specified date range.")
        return data
    except Exception as e:
        raise ValueError(f"Error fetching data for {symbol}: {str(e)}")

def fetch_news(symbol: str, limit: int = 5) -> list:
    """Fetch recent news for the given stock symbol"""
    try:
        # Using yfinance to get news
        ticker = yf.Ticker(symbol)
        news = ticker.news[:limit]
        news_items = [{'title': item['title'], 'link': item['link']} for item in news]
        
        # Web scraping additional news with BeautifulSoup
        url = f"https://finance.yahoo.com/quote/{symbol}/news"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Parsing news articles
        articles = soup.find_all('h3', class_='Mb(5px)')
        for article in articles[:limit]:
            title = article.get_text()
            link = "https://finance.yahoo.com" + article.find('a')['href']
            news_items.append({'title': title, 'link': link})
        
        return news_items
    except Exception as e:
        print(f"Warning: Unable to fetch news for {symbol}: {str(e)}", file=sys.stderr)
        return []
