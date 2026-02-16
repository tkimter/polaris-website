# 🍓 라즈베리파이 4 크롤러 서버 세팅 가이드

> 정부사업 공지 + 출자공고 크롤러를 라즈베리파이 4에서 자동 실행하고,
> 결과를 GitHub Pages(polaris-a.com)에 자동 업데이트하는 전체 과정입니다.

---

## 📋 목차

1. [사전 준비물](#1-사전-준비물)
2. [Raspberry Pi OS 설치](#2-raspberry-pi-os-설치)
3. [초기 시스템 설정](#3-초기-시스템-설정)
4. [GitHub SSH 키 설정 (Private 레포 접근)](#4-github-ssh-키-설정)
5. [프로젝트 클론 및 환경 구성](#5-프로젝트-클론-및-환경-구성)
6. [설정 파일 이전](#6-설정-파일-이전)
7. [동작 테스트](#7-동작-테스트)
8. [자동 실행 및 스케줄링](#8-자동-실행-및-스케줄링)
9. [모니터링 및 유지보수](#9-모니터링-및-유지보수)

---

## 1. 사전 준비물

| 항목                    | 설명                                             |
| ----------------------- | ------------------------------------------------ |
| 라즈베리파이 4          | **4GB 이상 권장** (Selenium 사용 시 메모리 필요) |
| microSD 카드            | 32GB 이상 (가능하면 USB SSD 부팅 권장)           |
| 전원 어댑터             | 5V 3A USB-C                                      |
| 이더넷 케이블 또는 WiFi | 네트워크 연결                                    |
| PC (Windows)            | 초기 설정용 (지금 쓰고 있는 PC)                  |
| microSD 카드 리더기     | OS 설치용                                        |

---

## 2. Raspberry Pi OS 설치

### 2-1. Raspberry Pi Imager 다운로드

Windows PC에서 [Raspberry Pi Imager](https://www.raspberrypi.com/software/) 다운로드 후 설치

### 2-2. OS 이미지 굽기

1. Raspberry Pi Imager 실행
2. **OS 선택**: `Raspberry Pi OS (other)` → `Raspberry Pi OS Lite (64-bit)`
   - Lite 버전 = 데스크톱 없음 → 메모리 절약
3. **저장소 선택**: microSD 카드 선택
4. **⚙️ 설정 (톱니바퀴 아이콘)** ← 이게 중요!
   - ✅ **Set hostname**: `polarispi` (또는 원하는 이름)
   - ✅ **Enable SSH**: `Use password authentication` 선택
   - ✅ **Set username and password**:
     - Username: `pi` (또는 원하는 이름)
     - Password: `원하는 비밀번호`
   - ✅ **Configure wireless LAN** (WiFi 사용 시):
     - SSID: WiFi 이름
     - Password: WiFi 비밀번호
     - Country: KR
   - ✅ **Set locale settings**:
     - Time zone: `Asia/Seoul`
     - Keyboard layout: `kr`
5. **WRITE** 클릭 → 완료될 때까지 대기

### 2-3. 부팅

1. microSD 카드를 라즈베리파이에 삽입
2. 이더넷 케이블 연결 (권장) 또는 WiFi 사용
3. 전원 연결 → 초록 LED가 깜빡이면 부팅 중
4. 1~2분 대기

---

## 3. 초기 시스템 설정

### 3-1. SSH 접속

Windows PowerShell 또는 cmd에서:

```powershell
# 이더넷으로 연결한 경우
ssh pi@polarispi.local

# 접속이 안 되면 IP 주소로 접속 (공유기 관리 페이지에서 확인)
ssh pi@192.168.0.XXX
```

> **Tip**: `polarispi.local`로 안 되면 공유기 관리자 페이지(보통 192.168.0.1)에서
> 라즈베리파이의 IP 주소를 확인하세요.

### 3-2. 시스템 업데이트

```bash
sudo apt update && sudo apt upgrade -y
```

### 3-3. 필수 패키지 설치

```bash
# Python 관련
sudo apt install -y python3 python3-pip python3-venv python3-dev

# 빌드 도구 (pip 패키지 컴파일에 필요)
sudo apt install -y build-essential libffi-dev libssl-dev

# lxml 의존성
sudo apt install -y libxml2-dev libxslt1-dev zlib1g-dev

# Git
sudo apt install -y git

# Chromium + ChromeDriver (Selenium용)
sudo apt install -y chromium-browser chromium-chromedriver
```

### 3-4. Swap 메모리 늘리기 (매우 중요!)

Selenium + Chromium이 메모리를 많이 사용하므로 swap을 2GB로 늘립니다.

```bash
# 현재 swap 확인
free -h

# swap 크기 변경
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
```

`CONF_SWAPSIZE=100`을 찾아서 아래처럼 변경:

```
CONF_SWAPSIZE=2048
```

저장 후 (Ctrl+O, Enter, Ctrl+X):

```bash
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# 확인
free -h
# Swap: 2.0Gi 가 보이면 OK
```

### 3-5. 시간대 확인

```bash
# Asia/Seoul로 되어있는지 확인
timedatectl
# 안 되어있으면:
sudo timedatectl set-timezone Asia/Seoul
```

---

## 4. GitHub SSH 키 설정

Private 레포를 클론하려면 SSH 키 인증이 필요합니다.

### 4-1. SSH 키 생성

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
```

엔터 3번 (기본 경로, 비밀번호 없이):

```
Enter file in which to save the key (/home/pi/.ssh/id_ed25519): [Enter]
Enter passphrase: [Enter]
Enter same passphrase again: [Enter]
```

### 4-2. 공개키 복사

```bash
cat ~/.ssh/id_ed25519.pub
```

출력되는 전체 문자열을 복사합니다 (ssh-ed25519 AAAA... 부터 끝까지).

### 4-3. GitHub에 SSH 키 등록

1. Windows PC에서 브라우저 열기
2. https://github.com/settings/keys 접속
3. **New SSH key** 클릭
4. - **Title**: `RaspberryPi4-Crawler` (식별용 이름)
   - **Key type**: Authentication Key
   - **Key**: 위에서 복사한 공개키 붙여넣기
5. **Add SSH key** 클릭

### 4-4. SSH 접속 테스트

```bash
ssh -T git@github.com
```

처음에 `Are you sure you want to continue connecting?` 나오면 `yes` 입력.

```
Hi tkimter! You've been successfully authenticated, but GitHub does not provide shell access.
```

이렇게 나오면 성공! ✅

### 4-5. Git 사용자 설정

```bash
git config --global user.name "tkimter"
git config --global user.email "your-email@example.com"
```

---

## 5. 프로젝트 클론 및 환경 구성

### 5-1. 작업 디렉토리 생성 및 클론

```bash
mkdir -p ~/coding && cd ~/coding

# Private 레포 (SSH URL로 클론)
git clone git@github.com:tkimter/crawling_WorkNotices.git
git clone git@github.com:tkimter/crawling_InvestmentNotice.git

# Public 레포 (SSH로 해야 push도 가능)
git clone git@github.com:tkimter/polaris-website.git
```

### 5-2. crawling_WorkNotices 가상환경 설정

```bash
cd ~/coding/crawling_WorkNotices

# 가상환경 생성
python3 -m venv venv

# 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 의존성 설치 (시간이 좀 걸립니다, 10~20분)
pip install -r requirements.txt

# Playwright 설치 (사용하는 경우)
# playwright install chromium
# playwright install-deps

# 가상환경 비활성화
deactivate
```

### 5-3. crawling_InvestmentNotice 가상환경 설정

```bash
cd ~/coding/crawling_InvestmentNotice

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

### 5-4. 디렉토리 구조 확인

```bash
ls -la ~/coding/
```

결과:

```
crawling_WorkNotices/        ← Private (정부사업 공지)
crawling_InvestmentNotice/   ← Private (출자공고)
polaris-website/             ← Public  (GitHub Pages)
```

---

## 6. 설정 파일 이전

### 6-1. config.yaml 확인

GitHub에 config.yaml이 포함되어 있지 않거나, 텔레그램 봇 토큰 등
민감한 정보가 빠져있을 수 있습니다.

**방법 A: GitHub에 config.yaml이 포함된 경우**
→ 별도 작업 필요 없음 (클론 시 자동으로 포함)

**방법 B: Windows에서 직접 SCP로 복사하는 경우**

Windows PowerShell에서:

```powershell
# 정부사업 크롤러 설정
scp C:\Users\Taemin\Documents\coding\crawling_WorkNotices\config.yaml pi@polarispi.local:~/coding/crawling_WorkNotices/config.yaml

# 출자공고 크롤러 설정
scp C:\Users\Taemin\Documents\coding\crawling_InvestmentNotice\config.yaml pi@polarispi.local:~/coding/crawling_InvestmentNotice/config.yaml
```

### 6-2. .env 파일 (있는 경우)

텔레그램 봇 토큰 등이 .env 파일에 있다면:

```powershell
scp C:\Users\Taemin\Documents\coding\crawling_WorkNotices\.env pi@polarispi.local:~/coding/crawling_WorkNotices/.env
scp C:\Users\Taemin\Documents\coding\crawling_InvestmentNotice\.env pi@polarispi.local:~/coding/crawling_InvestmentNotice/.env
```

### 6-3. data 디렉토리 생성

```bash
mkdir -p ~/coding/crawling_WorkNotices/data
mkdir -p ~/coding/crawling_InvestmentNotice/data
```

### 6-4. Selenium ChromeDriver 경로 확인

라즈베리파이에서 chromedriver 위치 확인:

```bash
which chromedriver
# 보통: /usr/bin/chromedriver

chromium-browser --version
# Chromium 버전 확인
```

크롤러 코드에서 chromedriver 경로를 하드코딩하고 있다면,
라즈베리파이의 경로(`/usr/bin/chromedriver`)로 수정이 필요할 수 있습니다.

---

## 7. 동작 테스트

### 7-1. 개별 크롤러 테스트

```bash
# 정부사업 크롤러 테스트
cd ~/coding/crawling_WorkNotices
source venv/bin/activate
python main.py crawl
deactivate

# 출자공고 크롤러 테스트
cd ~/coding/crawling_InvestmentNotice
source venv/bin/activate
python main.py crawl
deactivate
```

### 7-2. HTML 내보내기 테스트

```bash
cd ~/coding/crawling_WorkNotices
source venv/bin/activate
python run_and_export.py --no-push
deactivate

# 생성된 HTML 확인
ls -la ~/coding/polaris-website/work_notices.html
```

### 7-3. Git push 테스트

```bash
cd ~/coding/polaris-website
git status
git add .
git commit -m "Test push from Raspberry Pi"
git push
```

`Everything up-to-date` 또는 push 성공이 나오면 OK ✅

### 7-4. 통합 스크립트 테스트

```bash
cd ~/coding/polaris-website
python3 run_all.py --no-push
```

---

## 8. 자동 실행 및 스케줄링

### 8-1. 실행 스크립트 생성

```bash
cat > ~/coding/run_crawlers.sh << 'SCRIPT_EOF'
#!/bin/bash
#=============================================
# 크롤러 통합 실행 스크립트
# 라즈베리파이에서 cron/systemd로 자동 실행
#=============================================

LOG_DIR="$HOME/coding/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/crawl_$(date +%Y%m%d_%H%M%S).log"

echo "========================================" | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 크롤링 시작" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# run_all.py 실행 (각 프로젝트의 venv를 자동으로 찾아서 사용)
cd "$HOME/coding/polaris-website"
python3 run_all.py 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=$?

echo "========================================" | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 크롤링 완료 (exit: $EXIT_CODE)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 오래된 로그 삭제 (30일 이상)
find "$LOG_DIR" -name "crawl_*.log" -mtime +30 -delete

exit $EXIT_CODE
SCRIPT_EOF

chmod +x ~/coding/run_crawlers.sh
```

### 8-2. Cron 스케줄 등록

```bash
crontab -e
```

처음 실행하면 에디터 선택 → `1` (nano) 선택.

아래 내용을 맨 아래에 추가합니다:

```cron
# ============================================
# 크롤러 자동 실행 스케줄
# ============================================

# PATH 설정 (cron 환경에서 명령어를 찾기 위해 필요)
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# 매일 오전 9시 - 크롤링 실행
0 9 * * * /home/pi/coding/run_crawlers.sh >> /home/pi/coding/logs/cron.log 2>&1

# 매일 오후 2시 - 크롤링 실행
0 14 * * * /home/pi/coding/run_crawlers.sh >> /home/pi/coding/logs/cron.log 2>&1

# 매일 오후 6시 - 크롤링 실행
0 18 * * * /home/pi/coding/run_crawlers.sh >> /home/pi/coding/logs/cron.log 2>&1
```

저장: `Ctrl+O` → `Enter` → `Ctrl+X`

```bash
# 등록 확인
crontab -l
```

### 8-3. 매일 새벽 재부팅 설정

```bash
# root의 crontab에 재부팅 추가
sudo crontab -e
```

아래 내용 추가:

```cron
# 매일 새벽 4시 재부팅 (안정성 확보)
0 4 * * * /sbin/reboot

# 매주 일요일 새벽 3시 시스템 업데이트 후 재부팅
0 3 * * 0 apt update && apt upgrade -y && /sbin/reboot
```

### 8-4. 부팅 후 자동 실행 (systemd 서비스)

재부팅 후에도 크롤러가 자동으로 실행되게 합니다.

```bash
sudo nano /etc/systemd/system/crawler-startup.service
```

아래 내용 입력:

```ini
[Unit]
Description=Run crawlers after boot
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=pi
WorkingDirectory=/home/pi/coding
ExecStartPre=/bin/sleep 60
ExecStart=/home/pi/coding/run_crawlers.sh
StandardOutput=journal
StandardError=journal
TimeoutStartSec=600

[Install]
WantedBy=multi-user.target
```

저장 후:

```bash
# 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable crawler-startup.service

# 지금 바로 테스트 실행
sudo systemctl start crawler-startup.service

# 상태 확인
sudo systemctl status crawler-startup.service
```

---

## 9. 모니터링 및 유지보수

### 자주 쓰는 명령어 모음

```bash
# ---- 로그 확인 ----
# 최근 크롤링 로그 보기
tail -50 ~/coding/logs/cron.log

# 가장 최근 크롤링 로그 파일 보기
ls -lt ~/coding/logs/crawl_*.log | head -5
cat $(ls -t ~/coding/logs/crawl_*.log | head -1)

# 부팅 후 자동실행 로그
sudo journalctl -u crawler-startup.service --no-pager

# ---- 시스템 상태 ----
# 메모리 사용량
free -h

# 디스크 사용량
df -h

# CPU 온도
vcgencmd measure_temp

# 실행 중인 Python 프로세스
ps aux | grep python

# ---- 크롤러 관리 ----
# 수동으로 크롤링 실행
~/coding/run_crawlers.sh

# cron 스케줄 확인
crontab -l

# 크롤링 서비스 상태
sudo systemctl status crawler-startup.service

# ---- Git 관리 ----
# 코드 업데이트 (Windows에서 수정 후 push한 경우)
cd ~/coding/crawling_WorkNotices && git pull
cd ~/coding/crawling_InvestmentNotice && git pull

# ---- DB 확인 ----
# WorkNotices DB 크기
ls -lh ~/coding/crawling_WorkNotices/data/

# InvestmentNotice DB 크기
ls -lh ~/coding/crawling_InvestmentNotice/data/
```

### 코드 업데이트 방법

Windows에서 코드를 수정하고 GitHub에 push한 경우,
라즈베리파이에서 pull 받기만 하면 됩니다:

```bash
cd ~/coding/crawling_WorkNotices && git pull origin main
cd ~/coding/crawling_InvestmentNotice && git pull origin main
cd ~/coding/polaris-website && git pull origin main
```

### 문제 해결

#### SSH 접속이 안 될 때

```bash
# Windows에서 IP로 직접 접속
ssh pi@192.168.0.XXX
```

#### Selenium이 메모리 부족으로 죽을 때

```bash
# swap 확인
free -h

# swap이 부족하면 늘리기
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # CONF_SWAPSIZE=4096
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

#### chromedriver 버전 불일치

```bash
chromium-browser --version
chromedriver --version

# 버전이 다르면 재설치
sudo apt install --reinstall chromium-chromedriver
```

#### SD카드 수명 걱정

SD카드에 잦은 쓰기를 하면 수명이 줄어듭니다.
USB SSD 부팅을 권장합니다:

```bash
# USB SSD 부팅 설정 (별도 가이드 참고)
sudo raspi-config
# → Advanced Options → Boot Order → USB Boot
```

---

## 📊 전체 스케줄 요약

| 시간              | 동작                          | 설정 위치   |
| ----------------- | ----------------------------- | ----------- |
| **부팅 후 60초**  | 크롤링 자동 실행              | systemd     |
| **매일 09:00**    | 크롤링 + HTML 생성 + Git push | cron (pi)   |
| **매일 14:00**    | 크롤링 + HTML 생성 + Git push | cron (pi)   |
| **매일 18:00**    | 크롤링 + HTML 생성 + Git push | cron (pi)   |
| **매주 일 03:00** | apt update + upgrade + 재부팅 | cron (root) |
| **매일 04:00**    | 재부팅 (안정성)               | cron (root) |

---

## 🔄 데이터 흐름

```
[라즈베리파이]
     │
     ├── 09:00/14:00/18:00 (cron)
     │      │
     │      ├── crawling_WorkNotices/run_and_export.py
     │      │     ├── 크롤링 → SQLite DB 저장
     │      │     └── DB → work_notices.html 생성
     │      │
     │      ├── crawling_InvestmentNotice/run_and_export.py
     │      │     ├── 크롤링 → SQLite DB 저장
     │      │     └── DB → investment_notices.html 생성
     │      │
     │      └── git push → polaris-website 레포
     │                         │
     │                         ▼
     │                   GitHub Pages
     │                   (polaris-a.com)
     │
     └── 04:00 (cron) → 재부팅 → 부팅 후 60초 → 크롤링 자동 실행
```
