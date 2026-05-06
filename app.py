from flask import Flask, render_template
from paper_trader import load_portfolio
from rsi_strategy import scan_watchlist as rsi_scan
from ma_strategy import scan_watchlist as ma_scan
from trader import merge_signals
from auth import login, logout

app = Flask(__name__)


@app.route('/')
def index():
    portfolio = load_portfolio()
    trades = list(reversed(portfolio.get('trades', [])))[:20]
    return render_template('index.html', portfolio=portfolio, trades=trades)


@app.route('/scan')
def scan():
    try:
        login()
        rsi_signals = rsi_scan()
        ma_signals = ma_scan()
        logout()
    except Exception as e:
        return render_template('signals.html', signals=[], error=str(e))

    merged = {s['symbol']: s for s in merge_signals(rsi_signals, ma_signals)}
    ma_by_symbol = {s['symbol']: s for s in ma_signals}

    rows = []
    for s in rsi_signals:
        sym = s['symbol']
        ma = ma_by_symbol.get(sym, {})
        rows.append({
            'symbol': sym,
            'price': s.get('price') or ma.get('price'),
            'rsi_action': s.get('action', 'hold'),
            'rsi_value': s.get('rsi'),
            'ma_action': ma.get('action', 'hold'),
            'combined': merged.get(sym, {}).get('action', 'hold'),
        })

    return render_template('signals.html', signals=rows)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
