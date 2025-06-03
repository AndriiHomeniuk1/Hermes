import time
from binance.enums import ORDER_TYPE_MARKET, TIME_IN_FORCE_GTC
from decimal import Decimal, ROUND_DOWN, getcontext

#  IMPORTANT: Using simple functions instead of a class
#  Reason: Performance testing showed that calling class methods is ~7% slower than calling regular functions.
#  If maximum speed for order execution is required, using simple functions is preferable.
#  If code structure becomes more important in the future, switching to a class is possible, but at the cost of some performance.




def calculate_quantity_from_price(
    amount_usd: float,
    price: float,
    precision: int | None,
    use_decimal: bool = False
) -> float | None:
    """
    Calculates the number of coins
    based on a given USD amount and precision.
    """

    if price <= 0:
        print("Invalid price.")
        return None

    raw_quantity = amount_usd / price

    # Apply precision if specified
    if precision is not None:
        if use_decimal:
            getcontext().prec = 20  # Enable high-precision arithmetic
            quantity = Decimal(str(raw_quantity)).quantize(
                Decimal(f'1e-{precision}'), rounding=ROUND_DOWN
            )
            quantity = float(quantity)
        else:
            quantity = round(raw_quantity, precision)
    else:
        quantity = raw_quantity

    # Ensure the quantity is valid
    if quantity <= 0:
        print("Error: Quantity cannot be zero or negative.")
        return None

    return quantity


def get_executed_price(client, symbol: str, order_id: int) -> float | None:
    """
    Get the latest order status
    and return its average execution price if filled
    """
    order_status = client.futures_get_order(symbol=symbol, orderId=order_id)

    if order_status['status'] == 'FILLED':
        return float(order_status['avgPrice'])
    else:
        return None


def market_order(client, symbol: str, side: str, quantity: float | int):
    """Places a market order and waits for its execution."""
    # Attempt to create a market order
    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,  # "BUY" or "SELL"
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )

    except Exception as e:
        print(f"Error placing order: {e}")
        return None, None

    # Retrieve order ID for tracking
    order_id = order['orderId']

    # Wait for the order to be fully executed
    executed_price = None
    start_time = time.time()
    timeout = 60  # seconds

    while executed_price is None and time.time() - start_time < timeout:
        executed_price = get_executed_price(
            client=client,
            symbol=symbol,
            order_id=order_id
        )

        # Retry if not yet filled
        if executed_price is None:
            time.sleep(0.01)

    # Cancel the order and close any filled portions to ensure a clean exit
    if executed_price is None:
        rescue_order_after_timeout(
            client=client,
            symbol=symbol,
            order_id=order_id
        )
        return None, order_id

    return executed_price, order_id


def stop_loss_order(
        client,
        symbol: str,
        side: str,
        executed_price: float,
        st_percentage: float,
        quantity: float,
        price_precision: int
) -> None:
    """Places a stop-loss order based on the executed price."""

    # Calculate stop-loss price based on the executed price and percentage
    stop_loss_percentage = st_percentage / 100
    stop_price = (
        executed_price * (1 - stop_loss_percentage)
        if side == "BUY"
        else executed_price * (1 + stop_loss_percentage)
    )

    try:
        # Place stop-loss order
        client.futures_create_order(
            symbol=symbol,
            side="SELL" if side == "BUY" else "BUY",
            type="STOP_MARKET",
            stopPrice=round(stop_price, price_precision),
            quantity=quantity,
            timeInForce=TIME_IN_FORCE_GTC,
            reduceOnly=True
        )

    except Exception:
        pass


def take_profit_order(
        client,
        symbol: str,
        side: str,
        executed_price: float,
        tp_percentage: float,
        quantity: float,
        price_precision: int
) -> None:
    """Places a take-profit order based on the executed price."""

    # Calculate take_profit price based on the executed price and percentage
    take_profit_percentage = tp_percentage / 100
    take_profit_price = (
        executed_price * (1 + take_profit_percentage)
        if side == "BUY"
        else executed_price * (1 - take_profit_percentage)
    )

    try:
        # Create a limit order to take profit
        client.futures_create_order(
            symbol=symbol,
            side="SELL" if side == "BUY" else "BUY",
            type="LIMIT",
            price=round(take_profit_price, price_precision),
            quantity=quantity,
            timeInForce=TIME_IN_FORCE_GTC,
            reduceOnly=True
        )

    except Exception:
        pass


def place_market_order(
        client,
        symbol: str,
        side: str,
        amount_usd: int | float,
        precision: int | None,
        price_precision: int,
        st_percentage: float,
        tp_percentage: float,
        price: float,
        use_decimal: bool
) -> int | None:
    """Places a market order and sets stop-loss and take-profit levels."""

    quantity = calculate_quantity_from_price(
        amount_usd=amount_usd,
        price=price,
        precision=precision,
        use_decimal=use_decimal
    )

    if quantity is None:
        return None

    executed_price, order_id = market_order(client, symbol, side, quantity)

    if executed_price is None:
        return None

    stop_loss_order(
        client=client,
        symbol=symbol,
        side=side,
        executed_price=executed_price,
        st_percentage=st_percentage,
        quantity=quantity,
        price_precision=price_precision
    )

    take_profit_order(
        client=client,
        symbol=symbol,
        side=side,
        executed_price=executed_price,
        tp_percentage=tp_percentage,
        quantity=quantity,
        price_precision=price_precision
    )

    return order_id


def close_position_by_order_id(client, symbol: str, order_id: int) -> None:
    """Closes position by placing a market order in the reverse direction."""

    try:
        order_info = client.futures_get_order(symbol=symbol, orderId=order_id)
        side = order_info['side']
        quantity = float(order_info['executedQty'])

        if quantity == 0:
            print("Order has not been executed or quantity is zero")
            return

        # Determine the closing order side (opposite direction)
        close_side = "SELL" if side == "BUY" else "BUY"
        client.futures_create_order(
            symbol=symbol,
            side=close_side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity,
            reduceOnly=True
        )
        print(f"Position for order {order_id} closed ({close_side})")

    except Exception as e:
        print(f"Error closing position: {e}")


def rescue_order_after_timeout(client, symbol: str, order_id: int) -> None:
    """
    Attempts to cancel the remaining part of an unfilled order
    and close the executed portion.
    """

    # Try canceling the order if it hasn’t been fully executed within the timeout
    try:
        client.futures_cancel_order(symbol=symbol, orderId=order_id)
        print("Remaining order canceled.")
    except Exception as e:
        print(
            f"Unable to cancel the order"
            f"(it may already be filled or canceled): {e}"
        )

    # Close the position based on the successfully executed quantity
    close_position_by_order_id(
        client=client,
        symbol=symbol,
        order_id=order_id
    )
