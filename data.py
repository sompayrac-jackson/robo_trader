import robin_stocks.robinhood as rh
import pandas as pd


def get_historicals(symbol, interval='day', span='3month'):
    data = rh.stocks.get_stock_historicals(symbol, interval=interval, span=span)
    if not data:
        return None
    df = pd.DataFrame(data)
    df['close_price'] = df['close_price'].astype(float)
    df['begins_at'] = pd.to_datetime(df['begins_at'])
    df = df.sort_values('begins_at').reset_index(drop=True)
    return df


def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_ma(prices, period=20):
    return prices.rolling(window=period).mean()
