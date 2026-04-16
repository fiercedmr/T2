import yfinance as yf
import requests
import os
import time
import json
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

FILE = "results.json"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def load_results():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_results(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

# ============================
# DATA (9:15 APPROX = DAY OPEN)
# ============================
def get_data():
    data = yf.Ticker("^NSEI").history(period="5d")

    if len(data) < 2:
        return None

    today = data.iloc[-1]
    prev = data.iloc[-2]

    return {
        "date": str(datetime.now().date()),
        "open": float(today['Open']),
        "close": float(today['Close']),
        "prev_close": float(prev['Close'])
    }

# ============================
# STRATEGY 1 (FILTERED)
# ============================
def s1(data):
    gap = (data['open'] - data['prev_close']) / data['prev_close'] * 100

    if abs(gap) < 0.5:
        return "NO TRADE"

    return "BUY PUT" if gap > 0 else "BUY CALL"

# ============================
# STRATEGY 2 (YOUR LOGIC)
# ============================
def s2(data):
    if data['open'] > data['prev_close']:
        return "BUY PUT"
    elif data['open'] < data['prev_close']:
        return "BUY CALL"
    return "NO TRADE"

# ============================
# RESULT EVALUATION
# ============================
def evaluate(signal, entry_price, next_close):
    if signal == "BUY CALL":
        return "WIN" if next_close > entry_price else "LOSS"
    if signal == "BUY PUT":
        return "WIN" if next_close < entry_price else "LOSS"
    return "NA"

# ============================
# MAIN
# ============================
def run():
    data = get_data()
    if not data:
        return

    results = load_results()

    # Evaluate previous day
    if results:
        last = results[-1]
        if "res1" not in last:
            last["res1"] = evaluate(last["s1"], last["open"], data["close"])
            last["res2"] = evaluate(last["s2"], last["open"], data["close"])

    # Generate today signals
    data["s1"] = s1(data)
    data["s2"] = s2(data)

    results.append(data)
    save_results(results)

    # Calculate stats
    s1_wins = sum(1 for r in results if r.get("res1") == "WIN")
    s1_total = sum(1 for r in results if r.get("res1") in ["WIN","LOSS"])

    s2_wins = sum(1 for r in results if r.get("res2") == "WIN")
    s2_total = sum(1 for r in results if r.get("res2") in ["WIN","LOSS"])

    s1_acc = (s1_wins / s1_total * 100) if s1_total else 0
    s2_acc = (s2_wins / s2_total * 100) if s2_total else 0

    gap = (data['open'] - data['prev_close']) / data['prev_close'] * 100

    msg = f"""
📊 DAY {len(results)}

Open: {round(data['open'],2)}
Prev Close: {round(data['prev_close'],2)}
Gap: {round(gap,2)}%

🔵 Strategy 1:
{data['s1']}

🟡 Strategy 2:
{data['s2']}

📈 PERFORMANCE:
S1 → {s1_wins}/{s1_total} ({round(s1_acc,1)}%)
S2 → {s2_wins}/{s2_total} ({round(s2_acc,1)}%)
"""

    send_telegram(msg)

# Run once per day
while True:
    run()
    time.sleep(86400)
