import os
from dotenv import load_dotenv
from config.config_paths import ENV_PATH
from binance.client import Client



class BinanceClient:
    def __init__(self):
        """Initialize Binance client and attempt connection."""
        self.api_key = None
        self.api_secret = None
        self.client = None
        self.is_connected = False

        self.load_keys()

        if self.api_key and self.api_secret:
            self.is_connected = self.try_connect()

    def load_keys(self) -> None:
        """Load API keys from `.env` file."""
        load_dotenv(dotenv_path=ENV_PATH)
        self.api_key = os.getenv("API_KEY") or None
        self.api_secret = os.getenv("API_SECRET") or None

    def save_keys(self, api_key, api_secret) -> None:
        """Save new API keys and update Binance client."""
        with open(ENV_PATH, "w") as env_file:
            env_file.write(f"API_KEY={api_key}\n")
            env_file.write(f"API_SECRET={api_secret}\n")

        # Update stored keys
        self.api_key = api_key
        self.api_secret = api_secret

        # Attempt reconnection with new keys
        self.is_connected = self.try_connect()

    def try_connect(self) -> bool:
        """Validate API keys and establish Binance connection."""
        try:
            self.client = Client(self.api_key, self.api_secret)
            self.client.get_account()
            print("Connection to Binance successful!")
            return True
        except Exception as e:
            self.client = None
            print(f"Connection error: {e}")
            return False
