import yfinance as yf
import requests
import os
import time

BOT_TOKEN = os.getenv("7884471454:AAGd3xW5kyZh0NRBrcFi5LBA5lQKecJ_Er8")
CHAT_ID = os.getenv("838128310")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{7884471454:AAGd3xW5kyZh0NRBrcFi5LBA5lQKecJ_Er8}/sendMessage"
    requests.post(url, data={"838128310": CHAT_ID, "text": msg})

def run():
    nifty = yf.download("^NSEI", period="5d", interval="1d")
    vix = yf.download("^INDIAVIX", period="5d", interval="1d")

    if len(nifty) < 2 or len(vix) < 1:
        send_telegram("⚠️ Not enough data")
        return

    today = nifty.iloc[-1]
    prev = nifty.iloc[-2]

    gap = ((today['Open'] - prev['Close']) / prev['Close']) * 100

    message = f"""
📊 NIFTY:
Price: {round(today['Close'], 2)}
Gap: {round(gap, 2)}%

📉 VIX:
{round(vix.iloc[-1]['Close'], 2)}
"""

    send_telegram(message)
    send_telegram("🚀 BOT STARTED")

while True:
    try:
        run()
    except Exception as e:
        send_telegram(f"❌ Error: {str(e)}")

    time.sleep(300)  # runs every 5 minutes
