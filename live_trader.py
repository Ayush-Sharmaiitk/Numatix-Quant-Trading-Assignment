import time
import pandas as pd
from binance.client import Client

from indicators import add_indicators_15m, add_indicators_1h
from strategy import MultiTimeframeStrategy

# ---------------- CONFIG ----------------
API_KEY = "Uyocz2D4FbMw1Jw4nguXFvtjE2BzChRgutWsOQmCOVJd65xR7Iw0d98S6ORCyfs5"
API_SECRET = "mAloxT3mFuvUaGn6HOtWuavGQvoeNdSK8T3ySoMFLiehYJFXQRUNBPUQHM6CwYQd"

SYMBOL = "BTCUSDT"
INTERVAL_15M = Client.KLINE_INTERVAL_15MINUTE
LOOKBACK_LIMIT = 200

# ---------------- CLIENT ----------------
client = Client(API_KEY, API_SECRET)
client.API_URL = "https://testnet.binance.vision/api"

# ---------------- STRATEGY ----------------
strategy = MultiTimeframeStrategy()

# ---------------- STATE ----------------
in_position = False
entry_price = None

# ---------------- CSV INIT ----------------
csv_file = "live_trades.csv"

if not pd.io.common.file_exists(csv_file):
    pd.DataFrame(
        columns=["timestamp", "symbol", "direction", "entry_price", "exit_price"]
    ).to_csv(csv_file, index=False)

# ---------------- HELPERS ----------------
def fetch_15m_data():
    klines = client.get_klines(
        symbol=SYMBOL,
        interval=INTERVAL_15M,
        limit=LOOKBACK_LIMIT
    )

    df = pd.DataFrame(klines, columns=[
        "OpenTime", "Open", "High", "Low", "Close", "Volume",
        "_", "_", "_", "_", "_", "_"
    ])

    df["Datetime"] = pd.to_datetime(df["OpenTime"], unit="ms", utc=True)
    df = df[["Datetime", "Open", "High", "Low", "Close", "Volume"]]

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col])

    df.set_index("Datetime", inplace=True)
    return df


# ---------------- MAIN LOOP ----------------
while True:
    try:
        df_15m = fetch_15m_data()
        df_15m = add_indicators_15m(df_15m)

        df_1h = df_15m.resample("1H").last().dropna()
        df_1h = add_indicators_1h(df_1h)

        signal = strategy.generate_signal(
            df_15m,
            df_1h,
            in_position
        )

        if signal == "BUY" and not in_position:
            order = client.create_order(
                symbol=SYMBOL,
                side="BUY",
                type="MARKET",
                quantity=0.001
            )

            entry_price = float(order["fills"][0]["price"])
            in_position = True

            print(f"BUY @ {entry_price}")

        elif signal == "SELL" and in_position:
            order = client.create_order(
                symbol=SYMBOL,
                side="SELL",
                type="MARKET",
                quantity=0.001
            )

            exit_price = float(order["fills"][0]["price"])
            in_position = False

            trade = {
                "timestamp": pd.Timestamp.utcnow(),
                "symbol": SYMBOL,
                "direction": "BUY",
                "entry_price": entry_price,
                "exit_price": exit_price
            }

            pd.DataFrame([trade]).to_csv(
                csv_file,
                mode="a",
                header=False,
                index=False
            )

            print(f"SELL @ {exit_price}")

        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
