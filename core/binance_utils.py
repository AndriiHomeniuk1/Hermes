def is_valid_symbol(binance_client, symbol:str) -> bool:
    """Checks if the entered trading pair exists via the Binance API client.
    Retrieves the exchange information using `get_exchange_info()`
    and checks whether the specified symbol is in the list of available trading pairs.

    Args:
        binance_client (object): Binance API client instance.
        symbol (str): Trading pair symbol to check.

    Returns:
        bool: True if the symbol exists, False otherwise.
    """
    try:
        exchange_info = binance_client.get_exchange_info()
        symbols = {s["symbol"] for s in exchange_info["symbols"]}
        return symbol in symbols
    except Exception as e:
        print(f"Error checking pair via Binance API.: {e}")
        return False


def get_quantity_precision(client, symbol: str) -> int | None:
    """Gets the precision for the amount of coin."""

    symbol_info = client.futures_exchange_info()
    for s in symbol_info['symbols']:
        if s['symbol'] == symbol:
            return s['quantityPrecision']
    return None


def get_price_precision(client, symbol: str) -> int | None:
    """Gets the precision (number of decimal places) for the coin price.
    Fetches the trading pair information from Binance Futures API and determines the number of
    decimal places allowed for the price by checking the 'PRICE_FILTER' tick size.
    """

    try:
        symbol_info = client.futures_exchange_info()
        for s in symbol_info['symbols']:
            if s['symbol'] == symbol:
                for f in s['filters']:
                    if f['filterType'] == 'PRICE_FILTER':
                        tick_size = f['tickSize']
                        return len(tick_size.rstrip('0').split('.')[-1])
        return None
    except Exception as e:
        print(f"Error while fetching price precision: {e}")
        return None
