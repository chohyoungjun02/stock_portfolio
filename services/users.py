"""회원 저장소 (SQLite) + 토스 API 키 암호화 저장"""
import base64
import hashlib
import sqlite3

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    toss_client_id_enc TEXT,
    toss_client_secret_enc TEXT,
    account_no TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""


def _db():
    conn = sqlite3.connect(current_app.config['DB_PATH'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _db() as conn:
        conn.execute(SCHEMA)


def _fernet():
    # 앱 SECRET_KEY에서 암호화 키를 만들어, 키 파일 하나만 지키면 되도록 함
    digest = hashlib.sha256(current_app.config['SECRET_KEY'].encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def _encrypt(text):
    return _fernet().encrypt(text.encode()).decode()


def _decrypt(token):
    try:
        return _fernet().decrypt(token.encode()).decode()
    except InvalidToken:
        return None  # SECRET_KEY가 바뀌면 복호화 불가 → 다시 연동 필요


def create_user(username, password):
    """성공 시 user id, 아이디 중복이면 None"""
    try:
        with _db() as conn:
            cur = conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                               (username, generate_password_hash(password)))
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


def verify_user(username, password):
    """아이디·비밀번호가 맞으면 user id, 아니면 None"""
    with _db() as conn:
        row = conn.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()
    if row and check_password_hash(row['password_hash'], password):
        return row['id']
    return None


def save_toss_keys(user_id, client_id, client_secret, account_no):
    with _db() as conn:
        conn.execute("UPDATE users SET toss_client_id_enc = ?, toss_client_secret_enc = ?, account_no = ? WHERE id = ?",
                     (_encrypt(client_id), _encrypt(client_secret), account_no, user_id))


def delete_toss_keys(user_id):
    with _db() as conn:
        conn.execute("UPDATE users SET toss_client_id_enc = NULL, toss_client_secret_enc = NULL, account_no = NULL "
                     "WHERE id = ?", (user_id,))


def get_toss_keys(user_id):
    """연동된 키 dict, 연동 전이거나 복호화 실패면 None"""
    with _db() as conn:
        row = conn.execute("SELECT toss_client_id_enc, toss_client_secret_enc, account_no FROM users WHERE id = ?",
                           (user_id,)).fetchone()
    if not row or not row['toss_client_secret_enc']:
        return None
    client_id, client_secret = _decrypt(row['toss_client_id_enc']), _decrypt(row['toss_client_secret_enc'])
    if not client_id or not client_secret:
        return None
    return {"client_id": client_id, "client_secret": client_secret, "account_no": row['account_no']}
