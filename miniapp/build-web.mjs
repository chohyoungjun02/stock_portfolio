// 프로젝트 venv의 파이썬으로 정적 웹 번들(dist) 생성 (시스템 python은 Windows Store 바로가기일 수 있음)
import { execFileSync } from 'node:child_process';

const python = process.platform === 'win32' ? '../venv/Scripts/python.exe' : '../venv/bin/python';
execFileSync(python, ['../scripts/build_miniapp_web.py'], { stdio: 'inherit' });
