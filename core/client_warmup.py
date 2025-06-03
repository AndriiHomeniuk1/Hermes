import threading
import time

def keep_connection_alive(client) -> None:
    """Maintains an active connection with the Binance API."""
    while True:
        try:
            client.get_server_time()  # Sends periodic requests to keep the session active
            time.sleep(25)
        except Exception as e:
            print(f"Connection maintenance error: {e}")
            time.sleep(60)  # On failure, waits 60 seconds before retrying

def start_warmup(client) -> None:
    """Initiates a background thread to keep the Binance API connection alive."""
    if client:
        thread = threading.Thread(target=keep_connection_alive, args=(client,), daemon=True)
        thread.start() # Launches the background process
    else:
        print("Binance client is not initialized, connection maintenance not started!")
