# src/strategies/risk_management.py

class RiskManager:
    """
    RiskManager는 손절(Stop-Loss)과 익절(Take-Profit) 조건을 관리하는 클래스입니다.
    """
    def __init__(self, stop_loss_pct=0.05, take_profit_pct=0.10):
        """
        손절과 익절 비율을 설정합니다.

        Args:
            stop_loss_pct (float): 손절 비율 (예: 0.05는 5% 손절)
            take_profit_pct (float): 익절 비율 (예: 0.10는 10% 익절)
        """
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.entry_price = None  # 포지션 진입 시 가격을 기록

    def set_entry_price(self, price):
        """
        포지션 진입 가격을 설정합니다.

        Args:
            price (float): 포지션 진입 가격
        """
        self.entry_price = price

    def check_exit_conditions(self, current_price):
        """
        현재 가격이 손절 또는 익절 조건을 충족하는지 확인합니다.

        Args:
            current_price (float): 현재 시장 가격

        Returns:
            str or None: "STOP_LOSS", "TAKE_PROFIT" 또는 None
        """
        if self.entry_price is None:
            return None

        # 손절 조건: 현재가가 진입가 대비 손실 비율 이상 하락
        if current_price <= self.entry_price * (1 - self.stop_loss_pct):
            return "STOP_LOSS"

        # 익절 조건: 현재가가 진입가 대비 이익 비율 이상 상승
        if current_price >= self.entry_price * (1 + self.take_profit_pct):
            return "TAKE_PROFIT"

        return None
