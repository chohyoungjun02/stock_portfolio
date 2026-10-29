"""회원가입 · 로그인 · 로그아웃 · 토스 계좌 연동"""
import re
import secrets

from flask import Blueprint, abort, current_app, redirect, render_template, request, session, url_for

from auth import get_access_token
from services import users

auth_bp = Blueprint('auth', __name__)

USERNAME_RE = re.compile(r'^[A-Za-z0-9_]{3,30}$')


# 폼 위조(CSRF) 방지: 세션 토큰을 폼에 넣고 POST마다 확인
def csrf_token():
    if '_csrf' not in session:
        session['_csrf'] = secrets.token_urlsafe(32)
    return session['_csrf']


@auth_bp.app_context_processor
def inject_csrf():
    return {"csrf_token": csrf_token}


@auth_bp.before_request
def check_csrf_and_availability():
    if not current_app.config['AUTH_ENABLED']:
        return render_template('auth_disabled.html'), 403
    if request.method == 'POST':
        sent, expected = request.form.get('_csrf', ''), session.get('_csrf', '')
        # 세션이 없으면 둘 다 빈 문자열이라 일치해 버리므로 빈 토큰은 항상 거부
        if not expected or not secrets.compare_digest(sent, expected):
            abort(400)


def _login(user_id, username):
    session.clear()  # 로그인 전 세션 재사용 방지
    session['user_id'] = user_id
    session['username'] = username


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    username = request.form.get('username', '').strip()
    if request.method == 'POST':
        password = request.form.get('password', '')
        if not USERNAME_RE.match(username):
            error = "아이디는 영문·숫자·밑줄 3~30자로 입력해 주세요."
        elif len(password) < 8:
            error = "비밀번호는 8자 이상이어야 해요."
        elif password != request.form.get('password_confirm', ''):
            error = "비밀번호가 서로 달라요."
        else:
            user_id = users.create_user(username, password)
            if user_id is None:
                error = "이미 사용 중인 아이디예요."
            else:
                _login(user_id, username)
                return redirect(url_for('auth.link_account'))
    return render_template('auth.html', mode='signup', error=error, username=username)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    username = request.form.get('username', '').strip()
    if request.method == 'POST':
        user_id = users.verify_user(username, request.form.get('password', ''))
        if user_id is None:
            error = "아이디 또는 비밀번호가 맞지 않아요."
        else:
            _login(user_id, username)
            return redirect(url_for('pages.index'))
    return render_template('auth.html', mode='login', error=error, username=username)


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('pages.index'))


@auth_bp.route('/account', methods=['GET', 'POST'])
def link_account():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    error = None

    if request.method == 'POST':
        if request.form.get('action') == 'unlink':
            users.delete_toss_keys(user_id)
            return redirect(url_for('auth.link_account'))

        client_id = request.form.get('client_id', '').strip()
        client_secret = request.form.get('client_secret', '').strip()
        account_no = request.form.get('account_no', '').strip() or '1'
        if not client_id or not client_secret:
            error = "Client ID와 Client Secret을 모두 입력해 주세요."
        elif not get_access_token(client_id, client_secret):
            # 저장 전에 실제로 토큰이 발급되는지 확인
            error = "토스 인증에 실패했어요. 키가 맞는지 확인해 주세요."
        else:
            users.save_toss_keys(user_id, client_id, client_secret, account_no)
            return redirect(url_for('pages.index'))

    linked = users.get_toss_keys(user_id)
    return render_template('link_account.html', error=error,
                           linked_account=linked['account_no'] if linked else None)
