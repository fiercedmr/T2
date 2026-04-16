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
# ROBUST DATA FETCH (NO FAIL)
# ============================
def get_data():
    for _ in range(5):  # retry 5 times
        try:
            nifty = yf.download("^NSEI", period="5d", interval="1d", progress=False, threads=False)
            vix = yf.download("^INDIAVIX", period="5d", interval="1d", progress=False, threads=False)

            if len(nifty) >= 2 and len(vix) >= 1:
                today = nifty.iloc[-1]
                prev = nifty.iloc[-2]

                gap = float(((today['Open'] - prev['Close']) / prev['Close']) * 100)

                return {
                    "price": float(today['Close']),
                    "gap": gap,
                    "vix": float(vix.iloc[-1]['Close'])
                }

        except:
            pass

        time.sleep(2)

    return None

# ============================
# SIMPLE & RELIABLE STRATEGY
# ============================
def generate_signal(data):
    gap = data['gap']
    vix = data['vix']

    # VIX filter
    if not (13.5 < vix < 18.5):
        return "NO TRADE", "VIX Out of Range"

    # No clear gap
    if abs(gap) < 0.3:
        return "NO TRADE", "No Clear Gap"

    # Core logic (robust)
    if gap < 0:
        return "BUY CALL", "Gap Down Reversal"
    elif gap > 0:
        return "BUY PUT", "Gap Up Reversal"

    return "NO TRADE", "No Setup"

# ============================
# MAIN EXECUTION
# ============================
def run():
    data = get_data()

    if not data:
        send_telegram("⚠️ Data fetch failed")
        return

    signal, reason = generate_signal(data)

    message = f"""
📊 NIFTY:
Price: {round(data['price'],2)}
Gap: {round(data['gap'],2)}%

📉 VIX: {round(data['vix'],2)}

🧠 Setup: {reason}

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
