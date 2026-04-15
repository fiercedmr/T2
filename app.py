import yfinance as yf
import requests

BOT_TOKEN = "7884471454:AAGACFUOkmhE4AN9sV3yRCtU5kypufQSqYk"
CHAT_ID = "838128310"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def run():
    nifty = yf.download("^NSEI", period="2d", interval="1d")
    vix = yf.download("^INDIAVIX", period="2d", interval="1d")

    today = nifty.iloc[-1]
    prev = nifty.iloc[-2]

    gap = ((today['Open'] - prev['Close']) / prev['Close']) * 100

    msg = f"""
📊 NIFTY:
Price: {round(today['Close'],2)}
Gap: {round(gap,2)}%

📉 VIX: {round(vix.iloc[-1]['Close'],2)}
"""

    send_telegram(msg)

run()
