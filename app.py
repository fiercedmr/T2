import yfinance as yf
import requests
import os
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_data():
    nifty = yf.download("^NSEI", period="5d", interval="1d")
    vix = yf.download("^INDIAVIX", period="5d", interval="1d")
    us = yf.download("^GSPC", period="5d", interval="1d")
    asia = yf.download("^N225", period="5d", interval="1d")

    if len(nifty) < 2:
        return None

    today = nifty.iloc[-1]
    prev = nifty.iloc[-2]

    gap = ((today['Open'] - prev['Close']) / prev['Close']) * 100

    return {
        "price": today['Close'],
        "gap": gap,
        "vix": vix.iloc[-1]['Close'],
        "us_change": (us.iloc[-1]['Close'] - us.iloc[-2]['Close']) / us.iloc[-2]['Close'],
        "asia_change": (asia.iloc[-1]['Close'] - asia.iloc[-2]['Close']) / asia.iloc[-2]['Close']
    }

def generate_signal(data):
    # Global bias
    if data['us_change'] > 0 and data['asia_change'] > 0:
        bias = "BULLISH"
    elif data['us_change'] < 0 and data['asia_change'] < 0:
        bias = "BEARISH"
    else:
        return "NO TRADE", "Mixed Global"

    # VIX filter
    if not (13.5 < data['vix'] < 18.5):
        return "NO TRADE", "VIX Filter"

    gap = data['gap']

    if abs(gap) < 0.3:
        return "NO TRADE", "No Gap"

    # Small gap → continuation
    if 0.3 <= abs(gap) <= 0.7:
        if gap > 0 and bias == "BULLISH":
            return "BUY CALL", bias
        elif gap < 0 and bias == "BEARISH":
            return "BUY PUT", bias

    # Big gap → reversal
    if abs(gap) > 0.7:
        if gap > 0 and bias == "BEARISH":
            return "BUY PUT", bias
        elif gap < 0 and bias == "BULLISH":
            return "BUY CALL", bias

    return "NO TRADE", bias

def run():
    data = get_data()

    if not data:
        send_telegram("⚠️ Data error")
        return

    signal, reason = generate_signal(data)

    message = f"""
📊 NIFTY:
Price: {round(data['price'],2)}
Gap: {round(data['gap'],2)}%

📉 VIX: {round(data['vix'],2)}

🌍 Bias: {reason}

🚀 SIGNAL: {signal}
🎯 Target: 10-12%
🛑 SL: 18%
"""

    send_telegram(message)

send_telegram("🚀 SIGNAL BOT STARTED")

while True:
    try:
        run()
    except Exception as e:
        send_telegram(f"❌ Error: {str(e)}")

    time.sleep(300)
