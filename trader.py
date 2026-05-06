from auth import login, logout
from rsi_strategy import scan_watchlist as rsi_scan
from ma_strategy import scan_watchlist as ma_scan
from paper_trader import load_portfolio, execute_trade, print_summary


def merge_signals(rsi_signals, ma_signals):
    by_symbol = {s['symbol']: s for s in rsi_signals}
    for ma in ma_signals:
        symbol = ma['symbol']
        rsi = by_symbol.get(symbol, {})
        rsi_action = rsi.get('action', 'hold')
        ma_action = ma['action']
        price = ma['price'] or rsi.get('price')

        if 'sell' in (rsi_action, ma_action):
            action = 'sell'
        elif 'buy' in (rsi_action, ma_action):
            action = 'buy'
        else:
            action = 'hold'

        by_symbol[symbol] = {'symbol': symbol, 'action': action, 'price': price}
    return list(by_symbol.values())


def run():
    print("Logging in...")
    login()

    print("\n[RSI Strategy]")
    rsi_signals = rsi_scan()

    print("\n[MA Crossover Strategy]")
    ma_signals = ma_scan()

    signals = merge_signals(rsi_signals, ma_signals)

    portfolio = load_portfolio()
    current_prices = {}

    print("\nExecuting trades...")
    for signal in signals:
        symbol = signal['symbol']
        action = signal['action']
        price = signal['price']

        if price:
            current_prices[symbol] = price

        if action in ('buy', 'sell'):
            execute_trade(symbol, action, price, portfolio)

    print_summary(portfolio, current_prices)
    logout()


if __name__ == "__main__":
    run()
