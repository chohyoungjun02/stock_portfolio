"""회원가입 → 계좌 연동 → 보유 종목 → 로그아웃 흐름 테스트
(토스 서버 호출은 가짜 함수로 대체, 임시 DB 사용: python tests/test_auth_flow.py)"""
import os
import re
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import routes.auth  # noqa: E402
import routes.portfolio  # noqa: E402
from app import app  # noqa: E402
from services.users import init_db  # noqa: E402

# 가짜 토스: secret이 'good-secret'일 때만 토큰 발급
routes.auth.get_access_token = lambda cid, secret: 'tok' if secret == 'good-secret' else None
calls = []
def fake_holdings(cid, secret, account_no):
    calls.append((cid, secret, account_no))
    return {"data": {"holdings": [{"name": "QLD", "symbol": "QLD", "quantity": 2,
                                   "averagePrice": 100, "currentPrice": 110}]}}
routes.portfolio.get_my_holdings = fake_holdings

db_path = os.path.join(tempfile.mkdtemp(), 'test.db')
app.config.update(DB_PATH=db_path, AUTH_ENABLED=True)
with app.app_context():
    init_db()

c = app.test_client()


def csrf(url):
    return re.search(r'name="_csrf" value="([^"]+)"', c.get(url).get_data(as_text=True)).group(1)


# 로그인 전: 보유 종목 요청은 로그인 안내
r = c.get('/api/holdings')
assert r.status_code == 401 and r.get_json()['action'] == 'login'

# CSRF 토큰 없는 POST는 거부
assert c.post('/signup', data={'username': 'alice', 'password': 'pw123456', 'password_confirm': 'pw123456'}).status_code == 400

# 입력 검증
t = csrf('/signup')
assert '8자 이상' in c.post('/signup', data={'_csrf': t, 'username': 'alice', 'password': 'short',
                                             'password_confirm': 'short'}).get_data(as_text=True)

# 회원가입 성공 → 계좌 연동 화면으로 이동
r = c.post('/signup', data={'_csrf': t, 'username': 'alice', 'password': 'pw123456', 'password_confirm': 'pw123456'})
assert r.status_code == 302 and r.headers['Location'].endswith('/account')

# 연동 전: 연동 안내
r = c.get('/api/holdings')
assert r.status_code == 400 and r.get_json()['action'] == 'link'

# 틀린 키는 저장 안 됨
t = csrf('/account')
r = c.post('/account', data={'_csrf': t, 'client_id': 'cid', 'client_secret': 'wrong', 'account_no': '1'})
assert '인증에 실패' in r.get_data(as_text=True)

# 맞는 키 연동 → 보유 종목 조회 시 그 키 사용
r = c.post('/account', data={'_csrf': t, 'client_id': 'cid', 'client_secret': 'good-secret', 'account_no': '2'})
assert r.status_code == 302
j = c.get('/api/holdings').get_json()
assert j['status'] == 'success' and j['holdings'][0]['pnl_rate'] == 10.0, j
assert calls[-1] == ('cid', 'good-secret', '2')

# DB에는 키가 평문으로 저장되지 않음
row = sqlite3.connect(db_path).execute("SELECT toss_client_id_enc, toss_client_secret_enc, password_hash FROM users").fetchone()
assert 'good-secret' not in row[1] and row[0] != 'cid' and 'pw123456' not in row[2]

# 중복 아이디 거부
c2 = app.test_client()
t2 = re.search(r'name="_csrf" value="([^"]+)"', c2.get('/signup').get_data(as_text=True)).group(1)
assert '이미 사용 중' in c2.post('/signup', data={'_csrf': t2, 'username': 'alice', 'password': 'pw123456',
                                                  'password_confirm': 'pw123456'}).get_data(as_text=True)

# 다른 회원은 alice의 보유 종목을 볼 수 없음
r = c2.post('/signup', data={'_csrf': t2, 'username': 'bob', 'password': 'pw123456', 'password_confirm': 'pw123456'})
assert c2.get('/api/holdings').get_json()['action'] == 'link'

# 로그아웃 후 다시 로그인 안내, 틀린 비밀번호 거부, 맞으면 로그인
t = csrf('/account')
c.post('/logout', data={'_csrf': t})
assert c.get('/api/holdings').status_code == 401
t = csrf('/login')
assert '맞지 않아요' in c.post('/login', data={'_csrf': t, 'username': 'alice', 'password': 'nope'}).get_data(as_text=True)
assert c.post('/login', data={'_csrf': t, 'username': 'alice', 'password': 'pw123456'}).status_code == 302
assert c.get('/api/holdings').get_json()['status'] == 'success'

# 연동 해제
t = csrf('/account')
c.post('/account', data={'_csrf': t, 'action': 'unlink'})
assert c.get('/api/holdings').get_json()['action'] == 'link'

print("auth flow tests OK")
