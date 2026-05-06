import os
import math
import json
import functools
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from paper_trader import load_portfolio
from rsi_strategy import scan_watchlist as rsi_scan
from ma_strategy import scan_watchlist as ma_scan
from trader import merge_signals
from auth import login as rh_login, logout as rh_logout
from data import get_historicals, calculate_rsi, calculate_ma
from config import WATCHLIST
from rsi_strategy import RSI_OVERSOLD, RSI_OVERBOUGHT

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


def clean(series):
    return [None if math.isnan(v) else round(float(v), 4) for v in series]


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


@app.route('/watchlist')
@login_required
def watchlist():
    rows = []
    error = None
    try:
        rh_login()
        for symbol in WATCHLIST:
            df = get_historicals(symbol)
            if df is None or len(df) < 51:
                continue
            closes = df['close_price']
            price = round(float(closes.iloc[-1]), 2)
            rsi_series = calculate_rsi(closes)
            ma20_series = calculate_ma(closes, 20)
            ma50_series = calculate_ma(closes, 50)

            rsi = round(float(rsi_series.iloc[-1]), 1)
            ma20 = round(float(ma20_series.iloc[-1]), 2)
            ma50 = round(float(ma50_series.iloc[-1]), 2)
            prev_ma20 = float(ma20_series.iloc[-2])
            prev_ma50 = float(ma50_series.iloc[-2])

            rsi_action = 'buy' if rsi <= RSI_OVERSOLD else ('sell' if rsi > RSI_OVERBOUGHT else 'hold')

            if prev_ma20 <= prev_ma50 and ma20 > ma50:
                ma_action = 'buy'
            elif prev_ma20 >= prev_ma50 and ma20 < ma50:
                ma_action = 'sell'
            else:
                ma_action = 'hold'

            rows.append({
                'symbol': symbol,
                'price': price,
                'rsi': rsi,
                'ma20': ma20,
                'ma50': ma50,
                'rsi_action': rsi_action,
                'ma_action': ma_action,
            })
        rh_logout()
    except Exception as e:
        error = str(e)

    return render_template('watchlist.html', rows=rows, error=error)


VALID_SPANS = {'month', '3month', 'year'}

@app.route('/chart/')
@app.route('/chart/<symbol>')
@login_required
def chart(symbol='GLD'):
    symbol = symbol.upper()
    span = request.args.get('span', '3month')
    if span not in VALID_SPANS:
        span = '3month'

    chart_data = None
    error = None
    try:
        rh_login()
        df = get_historicals(symbol, span=span)
        rh_logout()

        if df is not None and len(df) >= 20:
            closes = df['close_price']
            has_ma50 = len(df) >= 51
            chart_data = json.dumps({
                'labels': df['begins_at'].dt.strftime('%b %d').tolist(),
                'prices': clean(closes),
                'ma20': clean(calculate_ma(closes, 20)),
                'ma50': clean(calculate_ma(closes, 50)) if has_ma50 else None,
                'rsi': clean(calculate_rsi(closes)),
            })
        else:
            error = f'Not enough data for {symbol}.'
    except Exception as e:
        error = str(e)

    return render_template('chart.html', symbol=symbol, watchlist=WATCHLIST,
                           chart_data=chart_data, error=error, span=span,
                           rsi_oversold=RSI_OVERSOLD, rsi_overbought=RSI_OVERBOUGHT)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
