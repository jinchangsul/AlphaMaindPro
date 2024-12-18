# mock_exchange_api.py
import time

class MockPositionManager:
    """
    MockPositionManager는 가상의 계좌 상태(현금, 코인 보유량)를 관리하는 클래스입니다.
    execute_order() 메서드를 통해 매수/매도 체결 결과를 반영할 수 있습니다.
    """
    def __init__(self):
        self.cash_balance = 1000000  # 초기 자금 (예: 1,000,000원)
        self.coin_balance = 0.0      # 초기 코인 보유량(0개)

    def execute_order(self, side: str, price: float, volume: float) -> bool:
        """
        주문 체결 결과를 포지션(현금, 코인 잔고)에 반영합니다.

        Args:
            side (str): "buy" 또는 "sell"
            price (float): 체결 가격
            volume (float): 체결된 코인 수량

        Returns:
            bool: 주문 결과 반영 성공 여부
        """
        if side == "buy":
            cost = price * volume
            if self.cash_balance >= cost:
                self.cash_balance -= cost
                self.coin_balance += volume
                return True
            else:
                print("[MockPositionManager] Not enough cash to buy")
                return False
        else:  # "sell"
            if self.coin_balance >= volume:
                self.coin_balance -= volume
                self.cash_balance += price * volume
                return True
            else:
                print("[MockPositionManager] Not enough coin to sell")
                return False

class MockExchangeAPI:
    """
    MockExchangeAPI는 가상의 시세 변동 및 주문 체결 응답을 제공하는 클래스입니다.
    실제 거래소 API 없이 트레이딩 로직 테스트를 위해 사용할 수 있습니다.
    """
    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.current_price = 20000.0  # 초기 가상 가격
        self.price_trend = 10         # 가격 변동 폭 (매 루프마다 가격 변경)

    def get_current_price(self, symbol: str) -> float:
        """
        현재 가상 가격을 반환합니다.
        가격이 일정 범위를 초과하면 상승/하강 방향을 반전하여 반복적인 변동을 유도합니다.

        Args:
            symbol (str): 예: "BTC/USDT"

        Returns:
            float: 현재 가상 가격
        """
        self.current_price += self.price_trend
        if self.current_price > 21000:
            self.price_trend = -10
        elif self.current_price < 19000:
            self.price_trend = 10
        return self.current_price

    def place_order(self, symbol: str, side: str, quantity: float) -> dict:
        """
        가상의 주문 체결 결과를 반환합니다.
        이 예제에서는 항상 주문이 성공한다고 가정합니다.

        Args:
            symbol (str): 예: "BTC/USDT"
            side (str): "buy" 또는 "sell"
            quantity (float): 주문 수량

        Returns:
            dict: 주문 체결 결과 정보 (체결가격, 수량, 타임스탬프, 상태 등)
        """
        timestamp = int(time.time() * 1000)
        return {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price_executed": self.current_price,
            "timestamp": timestamp,
            "status": "filled"
        }

if __name__ == "__main__":
    # 단독 실행 시 테스트 코드
    position_manager = MockPositionManager()
    api = MockExchangeAPI(api_key="dummy_key", api_secret="dummy_secret")

    symbol = "BTC/USDT"
    price = api.get_current_price(symbol)
    volume = 0.001

    # 매수 주문 시뮬레이션
    order_result = api.place_order(symbol, "buy", volume)
    if position_manager.execute_order("buy", order_result["price_executed"], volume):
        print("[INFO] After buy:",
              "cash=", position_manager.cash_balance,
              "coin=", position_manager.coin_balance)
    else:
        print("[INFO] Buy order failed.")
