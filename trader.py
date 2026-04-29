from auth import login, logout
from strategy import scan_watchlist
from paper_trader import load_portfolio, execute_trade, print_summary


def run():
    print("Logging in...")
    login()

    print("\nScanning watchlist...")
    signals = scan_watchlist()

    portfolio = load_portfolio()
    current_prices = {}

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
