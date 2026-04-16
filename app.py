import yfinance as yf
import requests
import os
import time

# ============================
# GET FROM RAILWAY VARIABLES
# ============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        response = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
        print(response.text)
    except Exception as e:
        print("Telegram Error:", e)

# ============================
# START MESSAGE (CONFIRM BOT WORKING)
# ============================
send_telegram("🚀 BOT STARTED")

def run():
    try:
        nifty = yf.download("^NSEI", period="5d", interval="1d")
        vix = yf.download("^INDIAVIX", period="5d", interval="1d")

        # Safety check
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

    except Exception as e:
        send_telegram(f"❌ Run Error: {str(e)}")

# ============================
# CONTINUOUS LOOP (IMPORTANT)
# ============================
while True:
    run()
    time.sleep(300)  # runs every 5 minutes
