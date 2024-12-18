# src/strategies/simple_moving_average.py
# 익절/손절 관련 부분 제거 후 포지션 관리 로직 단순화
import numpy as np
from collections import deque

class SimpleMovingAverageStrategy:
    def __init__(self, short_window=5, long_window=20):
        self.short_window = short_window
        self.long_window = long_window
        self.prices = deque(maxlen=self.long_window)
        self.position = None  # "LONG" or None
        self.entry_price = None

    def update_price(self, current_price: float):
        self.prices.append(current_price)

    def compute_signals(self):
        if len(self.prices) < self.long_window:
            return "HOLD"

        prices_array = np.array(self.prices)
        short_sma = prices_array[-self.short_window:].mean()
        long_sma = prices_array.mean()

        if self.position is None:
            # 매수 조건: 5일 SMA가 20일 SMA 상향 돌파 시 BUY
            if short_sma > long_sma:
                return "BUY"
            else:
                return "HOLD"
        else:
            # 포지션 잡힌 상태에서는 전략 차원에서 별도 청산 신호 없음.
            # 청산은 RiskManager를 통해 처리하므로 여기서는 HOLD만 반환.
            return "HOLD"

    def on_buy(self, price):
        self.position = "LONG"
        self.entry_price = price

    def on_sell(self):
        self.position = None
        self.entry_price = None
