from data import get_historicals, calculate_ma
from config import WATCHLIST

MA_SHORT = 20
MA_LONG = 50


def get_signal(symbol):
    df = get_historicals(symbol)
    if df is None or len(df) < MA_LONG + 1:
        return 'hold', None, None

    closes = df['close_price']
    ma_short = calculate_ma(closes, MA_SHORT)
    ma_long = calculate_ma(closes, MA_LONG)

    current_price = closes.iloc[-1]
    prev_short, curr_short = ma_short.iloc[-2], ma_short.iloc[-1]
    prev_long, curr_long = ma_long.iloc[-2], ma_long.iloc[-1]

    # Golden cross: short MA crosses above long MA
    if prev_short <= prev_long and curr_short > curr_long:
        return 'buy', current_price, curr_short

    # Death cross: short MA crosses below long MA
    if prev_short >= prev_long and curr_short < curr_long:
        return 'sell', current_price, curr_short

    return 'hold', current_price, curr_short


def scan_watchlist():
    signals = []
    for symbol in WATCHLIST:
        action, price, ma = get_signal(symbol)
        price_str = f"${price:.2f}" if price else "N/A"
        ma_str = f"{ma:.2f}" if ma else "N/A"
        print(f"  {symbol}: {action.upper()} | Price: {price_str} | MA20: {ma_str}")
        signals.append({
            'symbol': symbol,
            'action': action,
            'price': price,
        })
    return signals
