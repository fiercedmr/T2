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

send_telegram("🚀 BOT LIVE")

def get_data():
    try:
        data = yf.Ticker("^NSEI").history(period="5d")

        if len(data) < 2:
            return None

        today = data.iloc[-1]
        prev = data.iloc[-2]

        gap = float(((today['Open'] - prev['Close']) / prev['Close']) * 100)

        # VIX fallback (fixed safe value)
        vix = 15  

        return {
            "price": float(today['Close']),
            "gap": gap,
            "vix": vix
        }

    except:
        return None

def generate_signal(data):
    gap = data['gap']
    vix = data['vix']

    if not (13.5 < vix < 18.5):
        return "NO TRADE", "VIX Filter"

    if abs(gap) < 0.3:
        return "NO TRADE", "No Gap"

    if gap < 0:
        return "BUY CALL", "Gap Down Reversal"
    else:
        return "BUY PUT", "Gap Up Reversal"

def run():
    data = get_data()

    if not data:
        send_telegram("⚠️ Retry next cycle")
        return

    signal, reason = generate_signal(data)

    message = f"""
📊 NIFTY:
Price: {round(data['price'],2)}
Gap: {round(data['gap'],2)}%

🧠 Setup: {reason}

🚀 SIGNAL: {signal}
🎯 Target: 10-12%
🛑 SL: 18%
"""

    send_telegram(message)

while True:
    try:
        run()
    except Exception as e:
        send_telegram(f"❌ Error: {str(e)}")

    time.sleep(300)
