import robin_stocks.robinhood as rh
from dotenv import load_dotenv
import os

load_dotenv()


def login():
    username = os.getenv("RH_USERNAME")
    password = os.getenv("RH_PASSWORD")

    if not username or not password:
        raise ValueError("RH_USERNAME and RH_PASSWORD must be set in your .env file")

    login_response = rh.login(
        username,
        password,
        expiresIn=86400,
        scope='internal',
        # by_sms=True,
        store_session=True
    )

    return login_response


def logout():
    rh.logout()


if __name__ == "__main__":
    response = login()
    print("Logged in:", response)
