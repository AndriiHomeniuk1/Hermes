import asyncio
import json
import websockets
import websockets.asyncio.client


async def listen_price(symbol, price_value, event) -> None:
    """
    Connects to Binance WebSocket trade stream for the given symbol
    and continuously listens for real-time price updates.

    On receiving each new trade message:
    - Parses the price from the JSON message.
    - Updates the shared multiprocessing.Value with the latest price.
    - Sets the multiprocessing.Event to notify other processes of the update.

    Args:
        symbol (str): Trading pair symbol, e.g. 'btcusdt'.
        price_value (multiprocessing.Value): Shared memory double to store current price.
        event (multiprocessing.Event): Event to signal a new price update.

    This coroutine runs indefinitely until an exception occurs or connection closes.
    """

    url = f"wss://fstream.binance.com/ws/{symbol.lower()}@trade"
    try:
        async with websockets.connect(url) as ws:
            async for message in ws:
                data = json.loads(message)
                price = float(data['p'])
                price_value.value = price
                event.set()
                #print("⚡ event.set() work!")  # for debug

                # Uncomment below to display price updates in the console
                #print(f"Price updated: {price}")
    except Exception as e:
        print(f"WebSocket error: {e}")

def run_listener(symbol, price_value, event) -> None:
    """
    Entry point to start the asyncio event loop and run the WebSocket listener.

    This function is intended to be called in a separate process to isolate
    the async WebSocket logic and allow continuous price streaming without blocking.
    """

    asyncio.run(listen_price(symbol, price_value, event))
