import os
import functools
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from paper_trader import load_portfolio
from rsi_strategy import scan_watchlist as rsi_scan
from ma_strategy import scan_watchlist as ma_scan
from trader import merge_signals
from auth import login as rh_login, logout as rh_logout

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return wrapper


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == os.getenv('DASHBOARD_PASSWORD'):
            session['authenticated'] = True
            return redirect(url_for('index'))
        error = 'Incorrect password.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout_page():
    session.clear()
    return redirect(url_for('login_page'))


@app.route('/')
@login_required
def index():
    portfolio = load_portfolio()
    trades = list(reversed(portfolio.get('trades', [])))[:20]
    return render_template('index.html', portfolio=portfolio, trades=trades)


@app.route('/scan')
@login_required
def scan():
    try:
        rh_login()
        rsi_signals = rsi_scan()
        ma_signals = ma_scan()
        rh_logout()
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
