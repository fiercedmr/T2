import yfinance as yf
import requests
import os
import time

# ============================
# TELEGRAM CONFIG (Railway Variables)
# ============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# ============================
# START MESSAGE
# ============================
send_telegram("🚀 SIGNAL BOT LIVE")

# ============================
# GET DATA (ROBUST VERSION)
# ============================
def get_data():
    try:
        # Retry mechanism
        for _ in range(3):
            nifty = yf.download("^NSEI", period="5d", interval="1d", progress=False)
            vix = yf.download("^INDIAVIX", period="5d", interval="1d", progress=False)

            if len(nifty) >= 2 and len(vix) >= 1:
                break
            time.sleep(2)

        if len(nifty) < 2 or len(vix) < 1:
            return None

        today = nifty.iloc[-1]
        prev = nifty.iloc[-2]

        gap = float(((today['Open'] - prev['Close']) / prev['Close']) * 100)

        # Try global data (optional)
        try:
            us = yf.download("^GSPC", period="5d", interval="1d", progress=False)
            asia = yf.download("^N225", period="5d", interval="1d", progress=False)

            if len(us) >= 2 and len(asia) >= 2:
                us_change = float((us.iloc[-1]['Close'] - us.iloc[-2]['Close']) / us.iloc[-2]['Close'])
                asia_change = float((asia.iloc[-1]['Close'] - asia.iloc[-2]['Close']) / asia.iloc[-2]['Close'])
            else:
                us_change = 0
                asia_change = 0
        except:
            us_change = 0
            asia_change = 0

        return {
            "price": float(today['Close']),
            "gap": gap,
            "vix": float(vix.iloc[-1]['Close']),
            "us_change": us_change,
            "asia_change": asia_change
        }

    except:
        return None

# ============================
# SIGNAL LOGIC
# ============================
def generate_signal(data):
    # Global bias (stable)
    if data['us_change'] >= 0 and data['asia_change'] >= 0:
        bias = "BULLISH"
    elif data['us_change'] < 0 and data['asia_change'] < 0:
        bias = "BEARISH"
    else:
        return "NO TRADE", "Mixed Global"

    # VIX filter
    if not (13.5 < data['vix'] < 18.5):
        return "NO TRADE", "VIX Out of Range"

    gap = data['gap']

    if abs(gap) < 0.3:
        return "NO TRADE", "No Clear Gap"

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

# ============================
# MAIN EXECUTION
# ============================
def run():
    data = get_data()

    if not data:
        send_telegram("⚠️ Data issue (retrying...)")
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

# ============================
# LOOP (RUNS EVERY 5 MIN)
# ============================
while True:
    try:
        run()
    except Exception as e:
        send_telegram(f"❌ Error: {str(e)}")

    time.sleep(300)
