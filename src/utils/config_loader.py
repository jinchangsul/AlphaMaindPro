# src/utils/config_loader.py

import logging
import os
import yaml

def get_logger(name: str):
    """
    로거 설정 함수.

    Args:
        name (str): 로거 이름

    Returns:
        logging.Logger: 설정된 로거 객체
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 콘솔 핸들러
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # 기존 핸들러가 없는 경우에만 추가
    if not logger.handlers:
        logger.addHandler(ch)
    return logger

def load_secrets():
    """
    secrets.yaml 파일을 로드하여 딕셔너리 형태로 반환합니다.

    Returns:
        dict: secrets.yaml의 내용
    """
    secrets_path = os.path.join("config", "secrets.yaml")
    with open(secrets_path, "r", encoding="utf-8") as f:
        secrets = yaml.safe_load(f)
    return secrets
