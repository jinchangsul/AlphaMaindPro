# src/trading/position_manager.py

class PositionManager:
    def __init__(self, exchange, base_currency="KRW", asset="BTC"):
        self.exchange = exchange
        self.base_currency = base_currency
        self.asset = asset
        self.cash_balance = 0.0   # 원화(기준 통화) 잔고
        self.coin_balance = 0.0   # 코인 잔고
        self.update_balances()

    def update_balances(self):
        # 거래소로부터 실제 잔고를 조회
        self.cash_balance = self.exchange.get_balance(self.base_currency)
        self.coin_balance = self.exchange.get_balance(self.asset)

    def execute_order(self, side: str, price: float, quantity: float) -> bool:
        """
        주문 체결 후 잔고를 반영하는 메서드.
        
        Args:
            side (str): "buy" 또는 "sell"
            price (float): 체결 가격
            quantity (float): 체결 수량

        Returns:
            bool: 잔고 조정 성공 시 True, 실패 시 False
        """
        if side == "buy":
            cost = price * quantity
            if self.cash_balance < cost:
                # 자금 부족
                return False
            # 매수 체결 반영
            self.cash_balance -= cost
            self.coin_balance += quantity
            return True
        elif side == "sell":
            if self.coin_balance < quantity:
                # 코인 부족
                return False
            # 매도 체결 반영
            revenue = price * quantity
            self.coin_balance -= quantity
            self.cash_balance += revenue
            return True
        else:
            # 알 수 없는 주문 유형
            return False

    def buy(self, price):
        # 예시 코드 (현재 사용하지 않거나 필요 시 참조)
        amount_to_spend = self.cash_balance * 0.1  # 자금의 10%만 매수 예시
        if amount_to_spend < 5000:
            print("[DEBUG] Not enough base currency to buy.")
            return None
        market_pair = f"{self.base_currency}-{self.asset}"
        order_resp = self.exchange.place_order(market_pair, side='buy', price=amount_to_spend)
        self.update_balances()
        return order_resp

    def sell(self):
        # 예시 코드 (현재 사용하지 않거나 필요 시 참조)
        if self.coin_balance <= 0:
            print("[DEBUG] No asset to sell.")
            return None
        market_pair = f"{self.base_currency}-{self.asset}"
        order_resp = self.exchange.place_order(market_pair, side='sell', volume=self.coin_balance)
        self.update_balances()
        return order_resp
