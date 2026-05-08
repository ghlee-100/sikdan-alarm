import requests
import json
import os
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
today = datetime.now(KST)

MEAL_FILE = "meal_data.json"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_today_meal():
    KST = timezone(timedelta(hours=9))
    today = datetime.now(KST)
    if today.weekday() >= 5:
        print("주말이라 식단 알림 없음")
        return None

    date_key = today.strftime("%Y-%m-%d")
    weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
    today_str = date_key + f"({weekday_names[today.weekday()]})"

    try:
        with open(MEAL_FILE, "r", encoding="utf-8") as f:
            meal_data = json.load(f)
    except:
        return f"⭐ {today_str}\n식단 파일이 없습니다."

    today_meal = meal_data.get(date_key)
    if not today_meal:
        return f"⭐ {today_str}\n오늘 식단 정보가 없습니다."

    result = f"{today_str}\n\n"
    if today_meal.get("오전간식"):
        result += f"🥐 오전간식:\n{today_meal['오전간식']}\n\n"
    if today_meal.get("점심"):
        result += f"☀️ 점심:\n{today_meal['점심']}\n\n"
    if today_meal.get("오후간식"):
        result += f"🧁 오후간식:\n{today_meal['오후간식']}\n\n"
    return result.strip()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    })
    result = response.json()
    if result.get("ok"):
        print("텔레그램 메시지 전송 성공")
    else:
        print(f"메시지 전송 실패: {result}")

if __name__ == "__main__":
    meal_info = get_today_meal()
    if meal_info:
        print(meal_info)
        send_telegram_message(meal_info)
