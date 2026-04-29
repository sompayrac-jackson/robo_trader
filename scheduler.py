import schedule
import time
from datetime import datetime
import pytz

from trader import run

MARKET_OPEN = 9   # 9:30 AM ET (simplified to hour)
MARKET_CLOSE = 16  # 4:00 PM ET
TIMEZONE = pytz.timezone('America/New_York')
RUN_INTERVAL_MINUTES = 30


def is_market_open():
    now = datetime.now(TIMEZONE)
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    return MARKET_OPEN <= now.hour < MARKET_CLOSE


def job():
    if not is_market_open():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Market closed, skipping.")
        return
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running bot...")
    try:
        run()
    except Exception as e:
        print(f"  [ERROR] {e}")


if __name__ == "__main__":
    print(f"Scheduler started — running every {RUN_INTERVAL_MINUTES} min during market hours.")
    schedule.every(RUN_INTERVAL_MINUTES).minutes.do(job)

    # Run immediately on start
    job()

    while True:
        schedule.run_pending()
        time.sleep(60)
