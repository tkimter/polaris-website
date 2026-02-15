# -*- coding: utf-8 -*-
"""
정부사업 + 출자공고 크롤러 통합 실행 + GitHub Pages 업데이트

두 크롤링 프로젝트를 순차적으로 실행하고,
결과를 polaris-website에 내보낸 뒤 한 번에 Git push 합니다.

사용법:
    python run_all.py               # 크롤링 + HTML 생성 + Git push
    python run_all.py --no-push     # 크롤링 + HTML 생성 (push 안함)
    python run_all.py --export-only # HTML 생성만 (크롤링 안함)
"""
import sys
import os
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.parent
WORK_NOTICES_DIR = SCRIPT_DIR / "crawling_worknotices"
INVESTMENT_DIR = SCRIPT_DIR / "crawling_investmentnotices"
WEBSITE_DIR = SCRIPT_DIR / "polaris-website"


def run_project_script(project_dir: Path, venv_python: str, extra_args: list):
    """각 프로젝트의 run_and_export.py를 --no-push로 실행"""
    script = project_dir / "run_and_export.py"
    if not script.exists():
        print(f"[ERROR] 스크립트를 찾을 수 없습니다: {script}")
        return False
    
    python_path = project_dir / "venv" / "Scripts" / "python.exe"
    if not python_path.exists():
        python_path = project_dir / "venv" / "bin" / "python"
    if not python_path.exists():
        python_path = sys.executable  # fallback
    
    cmd = [str(python_path), str(script), "--no-push"] + extra_args
    print(f"\n{'='*60}")
    print(f"실행: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, cwd=str(project_dir))
    return result.returncode == 0


def git_push_website():
    """polaris-website Git push"""
    if not WEBSITE_DIR.exists():
        print(f"[ERROR] 웹사이트 저장소를 찾을 수 없습니다: {WEBSITE_DIR}")
        return False
    
    try:
        original_dir = os.getcwd()
        os.chdir(WEBSITE_DIR)
        
        # Git 상태 확인
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not result.stdout.strip():
            print("[INFO] 변경사항이 없습니다. 푸시 건너뜀.")
            os.chdir(original_dir)
            return True
        
        print(f"\n[GIT] 변경된 파일:")
        print(result.stdout)
        
        # add + commit + push
        subprocess.run(["git", "add", "."], check=True)
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        commit_msg = f"Update notices - {now}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
        
        print("[INFO] GitHub Pages 업데이트 완료!")
        os.chdir(original_dir)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git 명령 실패: {e}")
        try:
            os.chdir(original_dir)
        except:
            pass
        return False


def main():
    parser = argparse.ArgumentParser(description="통합 크롤링 + GitHub Pages 업데이트")
    parser.add_argument("--no-push", action="store_true", help="Git push 안함")
    parser.add_argument("--export-only", action="store_true", help="HTML 생성만 (크롤링 안함)")
    args = parser.parse_args()
    
    extra_args = []
    if args.export_only:
        extra_args.append("--export-only")
    
    success = True
    
    # 1. 정부사업 공지 크롤링 + HTML 생성
    print("\n" + "=" * 60)
    print("📋 정부사업 공지 크롤링")
    print("=" * 60)
    if not run_project_script(WORK_NOTICES_DIR, "python", extra_args):
        print("[WARN] 정부사업 공지 크롤링에서 오류 발생")
        success = False
    
    # 2. 출자공고 크롤링 + HTML 생성
    print("\n" + "=" * 60)
    print("💰 출자공고 크롤링")
    print("=" * 60)
    if not run_project_script(INVESTMENT_DIR, "python", extra_args):
        print("[WARN] 출자공고 크롤링에서 오류 발생")
        success = False
    
    # 3. Git push (한 번에)
    if not args.no_push:
        print("\n" + "=" * 60)
        print("🚀 GitHub Pages 업데이트")
        print("=" * 60)
        if not git_push_website():
            success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 전체 파이프라인 완료!")
    else:
        print("⚠️ 일부 단계에서 오류가 발생했습니다.")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
