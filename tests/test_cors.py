"""앱인토스 미니앱 출처만 CORS 허용하는지 테스트 (네트워크 없이 실행: python tests/test_cors.py)"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app  # noqa: E402

app.config['TESTING'] = True
client = app.test_client()


def acao(path, origin):
    return client.get(path, headers={"Origin": origin}).headers.get('Access-Control-Allow-Origin')


# /api/news는 키가 없어도 응답(503)하므로 네트워크 없이 헤더만 확인 가능
os.environ.pop('NAVER_CLIENT_ID', None)
for origin in ['https://stockchartstudy.apps.tossmini.com', 'https://stockchartstudy.private-apps.tossmini.com',
               'https://abc.web.tossmini.com', 'https://abc.private-web.tossmini.com']:
    assert acao('/api/news', origin) == origin, origin

for origin in ['https://evil.com', 'http://stockchartstudy.apps.tossmini.com',
               'https://stockchartstudy.apps.tossmini.com.evil.com', 'https://tossmini.com']:
    assert acao('/api/news', origin) is None, origin

assert acao('/login', 'https://stockchartstudy.apps.tossmini.com') is None  # API 외 경로는 허용 안 함
print("cors tests OK")
