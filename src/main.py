# src/main.py

from src.exchange_apis.upbit_api import UpbitAPI
from src.strategies.simple_moving_average import SimpleMovingAverageStrategy
from src.trading.live_trading import run_live_trading
from src.utils.config_loader import load_secrets
from src.trading.position_manager import PositionManager  # 실제 잔고 반영

if __name__ == "__main__":
    print("Starting run_live_trading...")

    # secrets.yaml에서 API 키 로딩
    secrets = load_secrets()
    upbit_key = secrets['upbit']['api_key']
    upbit_secret = secrets['upbit']['api_secret']

    # UpbitAPI 인스턴스 생성 (실매수 API)
    exchange = UpbitAPI(access_key=upbit_key, secret_key=upbit_secret)

    # PositionManager 인스턴스 생성 (실제 잔고 반영)
    position_manager = PositionManager(exchange, base_currency="KRW", asset="BTC")

    # SMA 전략 인스턴스 생성
    # short_window=5, long_window=20 사용, 익절/손절은 RiskManager에서 처리하므로 전략은 BUY/HOLD만 판단
    strategy = SimpleMovingAverageStrategy(short_window=5, long_window=20)

    # Upbit 마켓 페어
    trading_pair = "KRW-BTC"

    # 라이브 트레이딩 실행
    run_live_trading(exchange, strategy, position_manager, symbol=trading_pair, interval=5)

    print("After run_live_trading...")
