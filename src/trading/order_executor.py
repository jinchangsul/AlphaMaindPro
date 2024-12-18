def execute_order(api, symbol: str, side: str, quantity: float) -> dict:
    return api.place_order(symbol, side, quantity)
