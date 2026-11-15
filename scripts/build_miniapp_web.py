"""앱인토스 미니앱용 정적 웹 번들 생성 (miniapp/dist)
대시보드 템플릿을 HTML로 렌더링하고 static/을 복사, API는 배포된 서버(API_BASE)를 호출
실행: python scripts/build_miniapp_web.py  (miniapp에서 npm run build 하면 자동 실행)"""
import json
import os
import shutil

from jinja2 import Environment, FileSystemLoader

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'miniapp', 'dist')
# 미니앱은 HTTPS API만 호출 가능 (토스 앱에서 HTTP 차단)
API_BASE = os.environ.get('MINIAPP_API_BASE', 'https://stock-portfolio-delta.vercel.app')


def render_index():
    env = Environment(loader=FileSystemLoader(os.path.join(ROOT, 'templates')))
    env.globals['url_for'] = lambda endpoint, filename: f'./static/{filename}'  # 정적 파일만 상대 경로로
    html = env.get_template('index2.html').render()
    marker = '<script type="module"'
    assert html.count(marker) == 1, "main.js 스크립트 태그를 찾을 수 없어요"
    return html.replace(marker, f'<script>window.API_BASE = {json.dumps(API_BASE)};</script>\n  {marker}')


def main():
    assert API_BASE.startswith('https://'), "MINIAPP_API_BASE는 https 주소여야 해요"
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, 'static'), os.path.join(OUT, 'static'))
    with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(render_index())
    print(f"미니앱 웹 번들 생성 → {os.path.normpath(OUT)} (API: {API_BASE})")


if __name__ == '__main__':
    main()
