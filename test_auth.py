from auth import login, logout
import robin_stocks.robinhood as rh
from data import get_historicals, calculate_rsi, calculate_ma

WATCHLIST = ['GLD', 'UCO', 'AGQ']


def test_auth():
    print("=== Auth Test ===")
    login()
    profile = rh.profiles.load_account_profile()
    portfolio = rh.profiles.load_portfolio_profile()
    print(f"  Account: {profile.get('account_number')}")
    print(f"  Buying power: ${float(portfolio.get('withdrawable_amount', 0)):.2f}")
    print("  Auth: PASSED\n")


def test_data():
    print("=== Data Test ===")
    for symbol in WATCHLIST:
        df = get_historicals(symbol)
        if df is None or df.empty:
            print(f"  {symbol}: FAILED — no data returned")
            continue

        closes = df['close_price']
        rsi = calculate_rsi(closes)
        ma = calculate_ma(closes)

        print(f"  {symbol}:")
        print(f"    Rows fetched:   {len(df)}")
        print(f"    Latest close:   ${closes.iloc[-1]:.2f}")
        print(f"    RSI (14):       {rsi.iloc[-1]:.2f}")
        print(f"    MA  (20-day):   ${ma.iloc[-1]:.2f}")
    print()


if __name__ == "__main__":
    test_auth()
    test_data()
    logout()
    print("All tests complete.")
