import yfinance as yf
import requests
import os
import time
import json
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

FILE = "results.json"
START_CAPITAL = 100

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

# 🔵 Strategy 1 (safe)
def strat1(data, capital):
    gap = (data['open'] - data['prev_close']) / data['prev_close'] * 100

    if abs(gap) < 0.5:
        return capital, "NO TRADE"

    direction = "PUT" if gap > 0 else "CALL"

    move = (data['close'] - data['open']) / data['open']
    if direction == "PUT":
        move = -move

    pnl = move * 3  # mild leverage

    capital += capital * pnl
    return capital, f"{direction} | {round(pnl*100,2)}%"

# 🟡 Strategy 2 (your adaptive)
def strat2(data, capital):
    gap = (data['open'] - data['prev_close']) / data['prev_close']

    direction1 = "CALL" if gap < 0 else "PUT"
    move = (data['close'] - data['open']) / data['open']

    trend = "CALL" if move > 0 else "PUT"

    def opt_move(direction):
        m = move
        if direction == "PUT":
            m = -m
        return m * 5

    # Step1
    if opt_move(direction1) > 0:
        capital += capital * 0.10 * 0.15
        return capital, f"{direction1} Step1 WIN"

    # Step2
    if opt_move(trend) > 0:
        capital += capital * 0.40 * 0.15
        return capital, f"{trend} Step2 WIN"

    # Step3
    if opt_move(trend) > 0:
        capital += capital * 1.0 * 0.15
        return capital, f"{trend} Step3 WIN"

    # loss
    capital *= 0.5
    return capital, f"{trend} LOSS"

def run():
    data = get_data()
    if not data:
        return

    results = load_results()

    cap1 = START_CAPITAL
    cap2 = START_CAPITAL

    # recompute capital
    for r in results:
        cap1 = r["cap1"]
        cap2 = r["cap2"]

    cap1, info1 = strat1(data, cap1)
    cap2, info2 = strat2(data, cap2)

    results.append({
        "date": data["date"],
        "cap1": cap1,
        "cap2": cap2
    })

    save_results(results)

    msg = f"""
📊 DAY {len(results)}

Open: {round(data['open'],2)}
Close: {round(data['close'],2)}

🔵 Strategy 1:
{info1}
💰 ₹{round(cap1,2)}

🟡 Strategy 2:
{info2}
💰 ₹{round(cap2,2)}
"""

    send_telegram(msg)

while True:
    run()
    time.sleep(86400)
