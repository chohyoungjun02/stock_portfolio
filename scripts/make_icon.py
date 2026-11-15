"""앱 아이콘 생성 (600x600 PNG): 토스 블루 배경 + 상승 캔들 + 추세선
실행: python scripts/make_icon.py  (Pillow 필요: pip install pillow)"""
import os

from PIL import Image, ImageDraw

SIZE, S = 600, 4  # 4배로 그린 뒤 줄여서 가장자리를 부드럽게
OUT = os.path.join(os.path.dirname(__file__), '..', 'miniapp', 'assets', 'icon-600.png')


def main():
    n = SIZE * S
    img = Image.new('RGB', (n, n))
    d = ImageDraw.Draw(img)
    # 위→아래 세로 그라데이션 (#4593fc → #1b64da)
    top, bottom = (0x45, 0x93, 0xfc), (0x1b, 0x64, 0xda)
    for y in range(n):
        t = y / (n - 1)
        d.line([(0, y), (n, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))

    p = lambda v: v * S  # 600 기준 좌표 → 실제 좌표
    # 캔들 4개: (x 중심, 시가, 종가, 고가, 저가), 600 기준 y는 아래로 증가
    candles = [(155, 345, 300, 280, 370), (245, 315, 245, 225, 335),
               (335, 275, 305, 255, 325), (425, 245, 155, 130, 265)]
    for x, o, c, hi, lo in candles:
        up = c < o
        color = (255, 255, 255) if up else (190, 215, 255)
        d.rounded_rectangle([p(x - 4), p(hi), p(x + 4), p(lo)], radius=p(4), fill=color)  # 꼬리
        d.rounded_rectangle([p(x - 30), p(min(o, c)), p(x + 30), p(max(o, c))], radius=p(10), fill=color)  # 몸통

    # 추세선 + 끝점
    pts = [(110, 430), (245, 370), (335, 395), (470, 225)]
    d.line([(p(x), p(y)) for x, y in pts], fill=(255, 214, 102), width=p(16), joint='curve')
    for x, y in pts[:-1]:
        d.ellipse([p(x - 8), p(y - 8), p(x + 8), p(y + 8)], fill=(255, 214, 102))
    ex, ey = pts[-1]
    d.ellipse([p(ex - 22), p(ey - 22), p(ex + 22), p(ey + 22)], fill=(255, 214, 102))
    d.ellipse([p(ex - 10), p(ey - 10), p(ex + 10), p(ey + 10)], fill=(255, 255, 255))

    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    assert img.size == (600, 600)
    img.save(OUT, optimize=True)
    print(f"아이콘 저장 → {os.path.normpath(OUT)}")


if __name__ == '__main__':
    main()
