import json
import os
from datetime import datetime

PORTFOLIO_FILE = 'paper_portfolio.json'
STARTING_CASH = 10000.0
ALLOCATION = 0.25  # 25% of cash per trade


def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    return {
        'cash': STARTING_CASH,
        'positions': {},
        'trades': [],
    }


def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=2)


def execute_trade(symbol, action, price, portfolio):
    now = datetime.now().isoformat()

    if action == 'buy':
        amount = portfolio['cash'] * ALLOCATION
        shares = amount / price

        if portfolio['cash'] < amount:
            print(f"  [PAPER] Insufficient cash for {symbol}")
            return portfolio

        if symbol in portfolio['positions']:
            existing = portfolio['positions'][symbol]
            total_shares = existing['shares'] + shares
            avg_price = (
                (existing['shares'] * existing['avg_price']) + (shares * price)
            ) / total_shares
            portfolio['positions'][symbol] = {'shares': total_shares, 'avg_price': avg_price}
        else:
            portfolio['positions'][symbol] = {'shares': shares, 'avg_price': price}

        portfolio['cash'] -= amount
        portfolio['trades'].append({
            'time': now, 'symbol': symbol, 'action': 'buy',
            'shares': shares, 'price': price,
        })
        print(f"  [PAPER] BUY  {shares:.4f} sh {symbol} @ ${price:.2f} | Spent: ${amount:.2f}")

    elif action == 'sell':
        if symbol not in portfolio['positions']:
            print(f"  [PAPER] No position in {symbol} to sell")
            return portfolio

        position = portfolio['positions'][symbol]
        proceeds = position['shares'] * price
        pnl = proceeds - (position['shares'] * position['avg_price'])

        portfolio['cash'] += proceeds
        del portfolio['positions'][symbol]
        portfolio['trades'].append({
            'time': now, 'symbol': symbol, 'action': 'sell',
            'shares': position['shares'], 'price': price, 'pnl': pnl,
        })
        print(f"  [PAPER] SELL {position['shares']:.4f} sh {symbol} @ ${price:.2f} | P&L: ${pnl:+.2f}")

    save_portfolio(portfolio)
    return portfolio


def print_summary(portfolio, current_prices=None):
    print("\n--- Paper Portfolio ---")
    print(f"  Cash:  ${portfolio['cash']:.2f}")

    total_equity = portfolio['cash']
    for symbol, pos in portfolio['positions'].items():
        price = (current_prices or {}).get(symbol, pos['avg_price'])
        value = pos['shares'] * price
        pnl = value - (pos['shares'] * pos['avg_price'])
        total_equity += value
        print(f"  {symbol}: {pos['shares']:.4f} sh | Avg ${pos['avg_price']:.2f} | Value ${value:.2f} | P&L ${pnl:+.2f}")

    print(f"  Total: ${total_equity:.2f}")
    print("-----------------------\n")
