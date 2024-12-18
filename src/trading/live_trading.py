# src/trading/live_trading.py

import time
import logging
from src.strategies.risk_management import RiskManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def run_live_trading(exchange, strategy, position_manager, symbol="KRW-BTC", interval=5):
    max_coin_holdings = 1.0  # 최대 보유 개수
    fixed_buy_amount = 5250  # 매수 시 항상 5250원 매수
    risk_manager = RiskManager(stop_loss_pct=0.05, take_profit_pct=0.10)  # 손절 5%, 익절 10%

    print("[DEBUG] run_live_trading 시작")

    while True:
        print("[DEBUG] 가격 조회 시작")
        try:
            current_price = exchange.get_current_price(symbol)
        except Exception as e:
            print(f"[ERROR] 가격 조회 실패: {e}")
            logger.error(f"Failed to get current price: {e}")
            time.sleep(interval)
            continue

        print(f"[DEBUG] 현재가: {current_price}")

        print("[DEBUG] 시그널 계산 시작")
        try:
            # simple_moving_average.py 수정된 코드에 맞추어 사용
            strategy.update_price(current_price)
            signal = strategy.compute_signals()
            print(f"[DEBUG] 시그널: {signal}")
        except Exception as e:
            print(f"[ERROR] 시그널 계산 실패: {e}")
            logger.error(f"Failed to calculate signal: {e}")
            time.sleep(interval)
            continue

        # RiskManager로 손절/익절 조건 확인
        exit_signal = risk_manager.check_exit_conditions(current_price)
        if exit_signal:
            print(f"[DEBUG] 리스크 관리 신호: {exit_signal}")
            # STOP_LOSS 또는 TAKE_PROFIT 신호는 결국 청산을 의미하므로 SELL로 처리
            if exit_signal in ["STOP_LOSS", "TAKE_PROFIT"]:
                signal = "SELL"

        if signal == "HOLD":
            print("[DEBUG] HOLD 상태 진입")
            logger.info(f"Current price: {current_price:.2f}, Signal: HOLD")
            logger.info(f"No action taken. cash={position_manager.cash_balance}, coin={position_manager.coin_balance}")

        elif signal == "BUY":
            print("[DEBUG] BUY 신호 발생")
            if position_manager.coin_balance >= max_coin_holdings:
                print("[DEBUG] 이미 최대 보유 개수 보유 중, 추가 매수 불가")
                logger.info("Already holding max coin. No additional buy allowed.")
            else:
                print("[DEBUG] 5250원 매수 로직 수행")
                buy_volume = fixed_buy_amount / current_price
                print(f"[DEBUG] 매수 수량: {buy_volume}")
                try:
                    order_result = exchange.place_order(symbol, "buy", price=fixed_buy_amount)
                except Exception as e:
                    print(f"[ERROR] 매수 주문 실패: {e}")
                    logger.error(f"Buy order failed: {e}")
                    time.sleep(interval)
                    continue

                print(f"[DEBUG] 주문 결과: {order_result}")

                executed_price = current_price
                executed_quantity = buy_volume

                print("[DEBUG] 포지션 반영 시도")
                if position_manager.execute_order("buy", executed_price, executed_quantity):
                    logger.info(f"Current price: {current_price:.2f}, Signal: BUY")
                    logger.info(f"Order executed: {order_result}")
                    logger.info(f"After order: cash={position_manager.cash_balance}, coin={position_manager.coin_balance}")
                    print("[DEBUG] 매수 성공")
                    risk_manager.set_entry_price(executed_price)
                else:
                    logger.info("Buy order failed. Not enough cash.")
                    print("[DEBUG] 매수 실패: 자금 부족")

        elif signal == "SELL":
            print("[DEBUG] SELL 신호 발생")
            sell_volume = min(position_manager.coin_balance, 0.001)
            print(f"[DEBUG] 매도 수량: {sell_volume}")
            if sell_volume <= 0:
                print("[DEBUG] 매도할 코인이 없음")
                logger.info("No coin to sell.")
            else:
                try:
                    order_result = exchange.place_order(symbol, "sell", volume=sell_volume)
                except Exception as e:
                    print(f"[ERROR] 매도 주문 실패: {e}")
                    logger.error(f"Sell order failed: {e}")
                    time.sleep(interval)
                    continue

                print(f"[DEBUG] 주문 결과: {order_result}")

                executed_price = current_price
                executed_quantity = sell_volume

                print("[DEBUG] 포지션 반영 시도")
                if position_manager.execute_order("sell", executed_price, executed_quantity):
                    logger.info(f"Current price: {current_price:.2f}, Signal: SELL")
                    logger.info(f"Order executed: {order_result}")
                    logger.info(f"After order: cash={position_manager.cash_balance}, coin={position_manager.coin_balance}")
                    print("[DEBUG] 매도 성공")
                    risk_manager.entry_price = None
                else:
                    logger.info("Sell order failed. Not enough coin.")
                    print("[DEBUG] 매도 실패: 코인 부족")

        print("[DEBUG] 다음 루프 전 대기")
        time.sleep(interval)

        # 잔고 동기화
        try:
            position_manager.update_balances()
            print("[DEBUG] 잔고 동기화 완료")
        except Exception as e:
            print(f"[ERROR] 잔고 동기화 실패: {e}")
            logger.error(f"Failed to update balances: {e}")
