import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경 변수 로드

CLIENT_ID = os.getenv("TOSS_CLIENT_ID")
CLIENT_SECRET = os.getenv("TOSS_CLIENT_SECRET")

# 메모리에 토큰과 만료 시각을 저장 (회원마다 키가 다르므로 client_id별로 보관)
_token_cache = {}  # client_id -> (token, expires_at)

def get_access_token(client_id=None, client_secret=None) -> str:
    # 인자가 없으면 .env 키 사용 (check.py, account.py 등 단독 실행용)
    client_id = client_id or CLIENT_ID
    client_secret = client_secret or CLIENT_SECRET

    if not client_id or not client_secret:
        print("[오류] CLIENT_ID 또는 CLIENT_SECRET이 설정되지 않았습니다. .env 파일을 확인하세요.")
        return None

    current_time = time.time()

    # 1. 이미 발급된 토큰이 있고, 만료까지 60초 이상 남아있다면 재사용
    cached_token, expires_at = _token_cache.get(client_id, (None, 0.0))
    if cached_token and current_time < (expires_at - 60):
        return cached_token

    # 2. 토큰이 없거나 만료 직전일 때만 토스 서버로 신규 발급 요청
    url = "https://openapi.tossinvest.com/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    print("\n[auth.py] 토큰 신규 발급/갱신 요청 중...")
    try:
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            
            # 토스에서 내려준 유효 기간(초 단위, 보통 86400초) 기준으로 만료 시점 계산
            expires_in = token_data.get("expires_in", 86400)
            _token_cache[client_id] = (token, current_time + expires_in)
            
            print(f"[auth.py] 토큰 발급 성공 (유효 기간: {expires_in}초)")
            return token
        else:
            print(f"\n[auth.py 실패] 오류 응답 ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        print(f"[auth.py 예외 발생]: {e}")
        return None

if __name__ == "__main__":
    t1 = get_access_token()
    if t1:
        print(f"첫 번째 호출 결과: {t1[:15]}...")
    
    t2 = get_access_token()
    if t2:
        print(f"두 번째 호출 결과 (캐시): {t2[:15]}...")