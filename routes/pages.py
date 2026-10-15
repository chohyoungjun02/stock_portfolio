"""화면 렌더링 라우트"""
from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)


# 메인 대시보드 화면 렌더링
@pages_bp.route('/')
def index():
    return render_template('index2.html')
