import pandas as pd
import numpy as np
from typing import Dict, Any

def analyze_data(data: pd.DataFrame) -> dict:
    """Perform enhanced analysis on the stock data"""
    analysis = {}
    
    # Calculate daily returns
    daily_returns = data['Close'].pct_change() * 100
    
    # Calculate volatility (20-day annualized)
    analysis['volatility'] = float(daily_returns.std() * np.sqrt(252))  # Annualized volatility
    
    # Basic statistics
    analysis['avg_price'] = float(data['Close'].mean())
    analysis['price_change'] = float(data['Close'].iloc[-1] - data['Close'].iloc[0])
    analysis['price_change_pct'] = float(((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100)
    analysis['avg_volume'] = float(data['Volume'].mean())
    analysis['max_daily_gain'] = float(daily_returns.max())
    analysis['max_daily_loss'] = float(daily_returns.min())
    
    # Determine trend
    analysis['trend'] = 'Upward' if analysis['price_change'] > 0 else 'Downward'
    
    # Calculate MACD
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    analysis['macd'] = float(macd.iloc[-1])
    analysis['macd_signal'] = float(signal.iloc[-1])
    
    # Calculate RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    analysis['rsi'] = float(100 - (100 / (1 + rs.iloc[-1])))
    
    # Calculate Stochastic Oscillator
    low_14 = data['Low'].rolling(window=14).min()
    high_14 = data['High'].rolling(window=14).max()
    k = 100 * ((data['Close'] - low_14) / (high_14 - low_14))
    analysis['stoch_k'] = float(k.iloc[-1])
    analysis['stoch_d'] = float(k.rolling(window=3).mean().iloc[-1])
    
    # Calculate Bollinger Bands
    sma20 = data['Close'].rolling(window=20).mean()
    std20 = data['Close'].rolling(window=20).std()
    analysis['bb_upper'] = float((sma20 + (std20 * 2)).iloc[-1])
    analysis['bb_middle'] = float(sma20.iloc[-1])
    analysis['bb_lower'] = float((sma20 - (std20 * 2)).iloc[-1])
    
    # Add company info if available
    for key in ['sector', 'industry', 'market_cap', 'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26', 'Volatility', 'Avg_Value_Traded']:
        if key in data.columns:
            analysis[key] = float(data[key].iloc[-1]) if isinstance(data[key].iloc[-1], (np.integer, np.floating)) else data[key].iloc[-1]
    
    return analysis

def _determine_trend(data: pd.DataFrame) -> str:
    """Determine the trend direction and strength"""
    close_prices = data['Close']
    sma20 = close_prices.rolling(window=20).mean()
    sma50 = close_prices.rolling(window=50).mean()
    
    current_price = close_prices.iloc[-1]
    
    if current_price > sma20.iloc[-1] and sma20.iloc[-1] > sma50.iloc[-1]:
        return "Strong Upward"
    elif current_price > sma20.iloc[-1]:
        return "Moderate Upward"
    elif current_price < sma20.iloc[-1] and sma20.iloc[-1] < sma50.iloc[-1]:
        return "Strong Downward"
    elif current_price < sma20.iloc[-1]:
        return "Moderate Downward"
    else:
        return "Sideways"

def _calculate_trend_strength(data: pd.DataFrame) -> float:
    """Calculate trend strength using ADX indicator"""
    high = data['High']
    low = data['Low']
    close = data['Close']
    
    # Calculate +DM and -DM
    plus_dm = high.diff()
    minus_dm = low.diff()
    
    # Calculate TR (True Range)
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Calculate ATR
    atr = tr.rolling(window=14).mean()
    
    # Calculate +DI and -DI
    plus_di = (plus_dm.rolling(window=14).mean() / atr) * 100
    minus_di = (minus_dm.rolling(window=14).mean() / atr) * 100
    
    # Calculate ADX
    dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100
    adx = dx.rolling(window=14).mean()
    
    return adx.iloc[-1]

def _calculate_atr(data: pd.DataFrame) -> float:
    """Calculate Average True Range"""
    high = data['High']
    low = data['Low']
    close = data['Close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    return tr.rolling(window=14).mean().iloc[-1]

def _calculate_support_resistance(data: pd.DataFrame) -> tuple:
    """Calculate support and resistance levels"""
    prices = data['Close']
    resistance = prices.rolling(window=20).max().iloc[-1]
    support = prices.rolling(window=20).min().iloc[-1]
    return support, resistance

def _calculate_technical_indicators(data: pd.DataFrame) -> Dict[str, Any]:
    """Calculate technical indicators (original implementation)"""
    indicators = {}
    
    # Original technical indicators code here...
    # (Keep the existing technical indicator calculations)
    
    return indicators

