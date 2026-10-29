import requests
from auth import get_access_token

BASE_URL = "https://openapi.tossinvest.com"
ACCOUNT_NO = "1"  # 본인의 계좌 ID/번호

def get_my_holdings(client_id=None, client_secret=None, account_no=ACCOUNT_NO):
    # 인자가 없으면 .env 키 사용, 로그인 회원은 각자 연동한 키 사용
    token = get_access_token(client_id, client_secret)
    if not token:
        print("[holdings.py] 토큰 발급 실패")
        return []

    url = f"{BASE_URL}/api/v1/holdings"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Tossinvest-Account": str(account_no),
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()  # 정상 데이터 반환
        else:
            print(f"[holdings.py 조회 실패] {response.status_code}: {response.text}")
            return []
    except Exception as e:
        print(f"[holdings.py 예외]: {e}")
        return []

if __name__ == "__main__":
    print(get_my_holdings())