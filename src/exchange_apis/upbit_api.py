# src/exchange_apis/upbit_api.py

import os
import uuid
import jwt
import hashlib
import requests
from urllib.parse import urlencode

class UpbitAPI:
    def __init__(self, access_key=None, secret_key=None):
        self.access_key = access_key or os.getenv("UPBIT_API_KEY")
        self.secret_key = secret_key or os.getenv("UPBIT_SECRET_KEY")
        self.base_url = "https://api.upbit.com/v1"
        
        if not self.access_key or not self.secret_key:
            raise ValueError("UPBIT_API_KEY와 UPBIT_SECRET_KEY 설정 필요")

    def _make_headers(self, query=None):
        # 디버그: query 파라미터 상태 확인
        print(f"[DEBUG] _make_headers - Query: {query}")
        
        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
        }

        if query is not None:
            q_string = urlencode(query)
            # 디버그: query 문자열 변환 확인
            print(f"[DEBUG] _make_headers - Encoded Query String: {q_string}")
            
            m = hashlib.sha512()
            m.update(q_string.encode('utf-8'))
            query_hash = m.hexdigest()
            payload['query_hash'] = query_hash
            payload['query_hash_alg'] = 'SHA512'
            # 디버그: query_hash 생성 확인
            print(f"[DEBUG] _make_headers - Query Hash: {query_hash}")

        jwt_token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        headers = {
            "Accept": "application/json",
            "Authorization": f'Bearer {jwt_token}'
        }
        # 디버그: 생성된 헤더 확인
        print(f"[DEBUG] _make_headers - Headers: {headers}")
        return headers

    def get_current_price(self, market_pair: str) -> float:
        url = f"{self.base_url}/ticker?markets={market_pair}"
        print(f"[DEBUG] Fetching current price from URL: {url}")  
        resp = requests.get(url)
        print(f"[DEBUG] API Response Status Code: {resp.status_code}")  
        print(f"[DEBUG] API Response Body: {resp.text}")  
        resp.raise_for_status()
        data = resp.json()
        trade_price = float(data[0]['trade_price'])
        print(f"[DEBUG] Parsed Trade Price: {trade_price}")  
        print(f"[DEBUG] 현재가: {trade_price}")  
        return trade_price

    def get_balance(self, asset: str) -> float:
        url = f"{self.base_url}/accounts"
        headers = self._make_headers()
        print(f"[DEBUG] get_balance - Requesting balance for {asset}")
        resp = requests.get(url, headers=headers)
        print(f"[DEBUG] get_balance - Status Code: {resp.status_code}")
        print(f"[DEBUG] get_balance - Response Body: {resp.text}")
        resp.raise_for_status()
        data = resp.json()
        for d in data:
            if d['currency'].upper() == asset.upper():
                balance = float(d['balance'])
                print(f"[DEBUG] get_balance - Found balance: {balance}")
                return balance
        print("[DEBUG] get_balance - No balance found, returning 0.0")
        return 0.0

    def place_order(self, market_pair: str, side: str, volume: float = None, price: float = None):
        """
        실제 Upbit 주문을 발행합니다.

        Args:
            market_pair (str): 예: "KRW-BTC"
            side (str): "buy" 또는 "sell" -> Upbit에서는 "bid"(매수), "ask"(매도)로 변환 필요
            volume (float): 매도 시 코인 수량
            price (float): 매수 시 원화 금액

        Returns:
            dict: 주문 결과 응답
        """
        
        # 디버그: side 값 확인 및 변환
        print(f"[DEBUG] place_order - Original side: {side}")
        if side == 'buy':
            side = 'bid'
        elif side == 'sell':
            side = 'ask'
        print(f"[DEBUG] place_order - Converted side: {side}")

        url = f"{self.base_url}/orders"
        query = {"market": market_pair, "side": side}
        if side == 'bid':  # 매수
            # 시장가 매수 시 ord_type='price'로 설정하고, price에 매수할 원화 금액을 지정
            if price is None:
                raise ValueError("매수 시 price 필요")
            query["ord_type"] = "price"
            query["price"] = str(price)
        else:
            # 매도 시 volume 필수
            if volume is None:
                raise ValueError("매도 시 volume 필요")
            query["ord_type"] = "market"
            query["volume"] = str(volume)

        print(f"[DEBUG] place_order - Final query: {query}")
        headers = self._make_headers(query)
        resp = requests.post(url, headers=headers, params=query)
        print(f"[DEBUG] place_order - Status Code: {resp.status_code}")
        print(f"[DEBUG] place_order - Response Body: {resp.text}")
        resp.raise_for_status()
        return resp.json()
