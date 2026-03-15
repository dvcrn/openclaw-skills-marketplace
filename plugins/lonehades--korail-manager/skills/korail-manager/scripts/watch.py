import sys
import os
import argparse
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
# The .env file should be in the skill's root directory (e.g., skills/korail-manager/.env)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

# Add local lib to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))
from korail2 import Korail, SoldOutError

def send_telegram_alert(token, chat_id, message):
    if not token or not chat_id:
        print(f"⚠️ 텔레그램 설정 누락으로 알림 발송 실패: {message}")
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ 텔레그램 발송 실패: {e}")

def send_slack_alert(webhook_url, message):
    if not webhook_url:
        # print(f"⚠️ 슬랙 설정 누락으로 알림 발송 실패")
        return
    try:
        payload = {"text": message}
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ 슬랙 발송 실패: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dep", required=True)
    parser.add_argument("--arr", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--start-time", type=int, required=True)
    parser.add_argument("--end-time", type=int, required=True)
    parser.add_argument("--interval", type=int, default=300)
    args = parser.parse_args()

    # Credentials & Config - NO HARDCODING ALLOWED
    KORAIL_ID = os.environ.get("KORAIL_ID")
    KORAIL_PW = os.environ.get("KORAIL_PW")
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
    SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

    # Validate essential credentials
    if not all([KORAIL_ID, KORAIL_PW, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        print("❌ 오류: 필수 환경 변수가 설정되지 않았습니다.")
        print("  - KORAIL_ID, KORAIL_PW")
        print("  - TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID")
        sys.exit(1)

    print(f"🚀 감시 시작: {args.date} {args.dep}->{args.arr} ({args.start_time}~{args.end_time}시)")

    korail = None
    
    while True:
        try:
            if not korail:
                korail = Korail(KORAIL_ID, KORAIL_PW)
                print("✅ 로그인 성공")

            search_time = f"{args.start_time:02d}0000"
            trains = korail.search_train(args.dep, args.arr, args.date, search_time)
            
            target_train = None
            for t in trains:
                if "KTX" not in t.train_type_name: continue
                
                dep_hour = int(t.dep_time[:2])
                if not (args.start_time <= dep_hour < args.end_time): continue
                
                # Strict station check
                if t.dep_name != args.dep or t.arr_name != args.arr: continue

                if t.has_general_seat():
                    target_train = t
                    break
            
            if target_train:
                print(f"🎯 발견: {target_train}")
                try:
                    korail.reserve(target_train)
                    msg = f"🎉 [예매 성공!]\n{target_train}\n\n🚨 즉시 결제 요망!"
                    print(msg)
                    send_telegram_alert(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, msg)
                    send_slack_alert(SLACK_WEBHOOK_URL, msg)
                    break
                except SoldOutError:
                    print("⚠️ 매진됨")
                except Exception as e:
                    print(f"❌ 예매 오류: {e}")
                    send_telegram_alert(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, f"❌ 오류: {e}")
                    send_slack_alert(SLACK_WEBHOOK_URL, f"❌ 오류: {e}")
            else:
                print(f".", end="", flush=True)

        except Exception as e:
            print(f"⚠️ 오류(재시도): {e}")
            korail = None # Force re-login
            time.sleep(10)

        time.sleep(args.interval)

if __name__ == "__main__":
    main()
