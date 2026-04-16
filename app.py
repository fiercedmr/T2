import yfinance as yf
import requests
import os
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

send_telegram("🚀 BOT RUNNING")

def run():
    try:
        nifty = yf.download("^NSEI", period="5d", interval="1d", progress=False)
        vix = yf.download("^INDIAVIX", period="5d", interval="1d", progress=False)

        if len(nifty) < 2:
            send_telegram("⚠️ Nifty data missing")
            return

        today = nifty.iloc[-1]
        prev = nifty.iloc[-2]

        gap = ((today['Open'] - prev['Close']) / prev['Close']) * 100

        send_telegram(f"NIFTY OK | Gap: {round(gap,2)}%")

    except Exception as e:
        send_telegram(f"❌ Error: {str(e)}")

while True:
    run()
    time.sleep(300)
