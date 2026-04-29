from data import get_historicals, calculate_rsi, calculate_ma

WATCHLIST = ['GLD', 'UCO', 'AGQ', 'XLE', 'XLF', 'XLB', 'XLV', 'XLK']

RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70


def get_signal(symbol):
    df = get_historicals(symbol)
    if df is None or len(df) < 20:
        return 'hold', None, None

    closes = df['close_price']
    rsi = calculate_rsi(closes)
    ma20 = calculate_ma(closes)

    current_price = closes.iloc[-1]
    current_rsi = rsi.iloc[-1]
    prev_rsi = rsi.iloc[-2]
    current_ma = ma20.iloc[-1]

    # Buy: RSI crosses up through 30 AND price is above 20-day MA
    if prev_rsi < RSI_OVERSOLD and current_rsi >= RSI_OVERSOLD and current_price > current_ma:
        return 'buy', current_price, current_rsi

    # Sell: RSI crosses above 70 OR price drops below 20-day MA
    if current_rsi > RSI_OVERBOUGHT or current_price < current_ma:
        return 'sell', current_price, current_rsi

    return 'hold', current_price, current_rsi


def scan_watchlist():
    signals = []
    for symbol in WATCHLIST:
        action, price, rsi = get_signal(symbol)
        price_str = f"${price:.2f}" if price else "N/A"
        rsi_str = f"{rsi:.2f}" if rsi else "N/A"
        print(f"  {symbol}: {action.upper()} | Price: {price_str} | RSI: {rsi_str}")
        signals.append({
            'symbol': symbol,
            'action': action,
            'price': price,
            'rsi': round(rsi, 2) if rsi else None,
        })
    return signals
