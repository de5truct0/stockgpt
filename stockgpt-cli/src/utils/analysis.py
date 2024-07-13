import pandas as pd
import numpy as np

def analyze_data(data: pd.DataFrame) -> dict:
    """Perform analysis on the stock data"""
    analysis = {}
    
    # Basic statistics
    analysis['avg_price'] = data['Close'].mean()
    analysis['price_change'] = data['Close'].iloc[-1] - data['Close'].iloc[0]
    analysis['price_change_pct'] = (analysis['price_change'] / data['Close'].iloc[0]) * 100
    analysis['avg_volume'] = data['Volume'].mean()
    
    # Trend identification
    analysis['trend'] = 'Upward' if analysis['price_change'] > 0 else 'Downward'
    
    # Significant price movements
    daily_returns = data['Close'].pct_change()
    analysis['max_daily_gain'] = daily_returns.max() * 100
    analysis['max_daily_loss'] = daily_returns.min() * 100
    
    # Technical indicators
    # MACD
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    analysis['macd'] = macd.iloc[-1]
    analysis['macd_signal'] = signal.iloc[-1]
    
    # RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    analysis['rsi'] = 100 - (100 / (1 + rs.iloc[-1]))
    
    # Bollinger Bands
    sma = data['Close'].rolling(window=20).mean()
    std = data['Close'].rolling(window=20).std()
    analysis['bb_upper'] = sma + (std * 2)
    analysis['bb_middle'] = sma
    analysis['bb_lower'] = sma - (std * 2)
    
    # Stochastic Oscillator
    low_14 = data['Low'].rolling(window=14).min()
    high_14 = data['High'].rolling(window=14).max()
    k = 100 * ((data['Close'] - low_14) / (high_14 - low_14))
    analysis['stoch_k'] = k.iloc[-1]
    analysis['stoch_d'] = k.rolling(window=3).mean().iloc[-1]
    
    return analysis