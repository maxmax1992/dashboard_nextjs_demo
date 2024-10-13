import asyncio
import websockets
import json
import pandas as pd
import numpy as np

BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"
WINDOW = 100
FEE_RATE = 0.001

price_history = []
position = None
entry_price = 0.0
pnl = 0.0

async def listen():
    async with websockets.connect(BINANCE_WS_URL) as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                price = float(data['p'])
                
                price_history.append(price)

                if len(price_history) > WINDOW:
                    price_history.pop(0)
                    predict_movement(price)

            except Exception as e:
                print(f"Error: {e}")


def predict_movement(current_price):
    global position, entry_price, pnl
    df = pd.Series(price_history)
    sma_short = df.rolling(window=3).mean().iloc[-1]
    sma_long = df.rolling(window=WINDOW).mean().iloc[-1]

    if np.isnan(sma_short) or np.isnan(sma_long):
        return

    if sma_short > sma_long:
        if position is None:
            # Mock buy order with fee
            potential_entry_price = current_price * (1 + FEE_RATE)
            if pnl - potential_entry_price >= -FEE_RATE * current_price:
                position = "long"
                entry_price = potential_entry_price
                print(f"Bought at {entry_price}")
    else:
        if position == "long":
            # Mock sell order with fee
            potential_sell_price = current_price * (1 - FEE_RATE)
            potential_pnl = pnl + (potential_sell_price - entry_price)
            if potential_pnl >= 0:
                pnl = potential_pnl
                print(f"Sold at {potential_sell_price}, PnL: {pnl}")
                position = None

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(listen())