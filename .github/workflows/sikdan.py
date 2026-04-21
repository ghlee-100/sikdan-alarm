import requests
import json
import os
from datetime import datetime

KAKAO_REST_API_KEY = "dea7d1fa29f51adb7f595a00ea763914"
KAKAO_CLIENT_SECRET = "oc9Xo304w1G25EoHQf4fW7EvNoZTm2wv"
MEAL_FILE = "meal_data.json"
TOKEN_FILE = "tokens.json"

def load_tokens():
    access_token = os.environ.get("KAKAO_ACCESS_TOKEN")
    refresh_token = os.environ.get("KAKAO_REFRESH_TOKEN")
    return {"access_token": access_token, "refresh_token": refresh_token}

def refresh_access_token(refresh_token):
    response = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "refresh_token",
            "client_id": KAKAO_REST_API_KEY,
            "client_secret": KAKAO_CLIENT_SECRET,
            "refresh_token": refresh_token,
        }
    )
    result = response.json()
    if "access_token" in result:
        print("토큰 갱신 성공!")
        return result["access_token"]
    else:
        raise Exception(f"토큰 갱신 실패: {result}")

def get_today_meal():
    today = datetime.now()
    weekday = today.weekday()
    if weekday >= 5:
        print("주말이라 식단 알림 없음")
        return None

    today_str = today.strftime("%Y-%m-%d")

    try:
        with open(MEAL_FILE, "r", encoding="utf-8") as f:
            meal_data = json.load(f)
    except:
        return f"📅 {today_str}\n식단 파일이 없습니다."

    today_meal = meal_data.get(today_str)
    if not today_meal:
        return f"📅 {today_str}\n오늘 식단 정보가 없습니다."

    result = f"🍱 {today_str} 어린이집 식단\n\n"
    if today_meal.get("오전간식"):
        result += f"🌅 오전간식:\n{today_meal['오전간식']}\n\n"
    if today_meal.get("점심"):
        result += f"🍚 점심:\n{today_meal['점심']}\n\n"
    if today_meal.get("오후간식"):
        result += f"🌆 오후간식:\n{today_meal['오후간식']}\n\n"

    return result.strip()

def send_kakao_message(message, access_token):
    def do_send(token):
        return requests.post(
            "https://kapi.kakao.com/v2/api/talk/memo/default/send",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "template_object": json.dumps({
                    "object_type": "text",
                    "text": message,
                    "link": {
                        "web_url": "https://www.sneducare.or.kr",
                        "mobile_web_url": "https://www.sneducare.or.kr"
                    }
                })
            }
        )

    response = do_send(access_token)
    result = response.json()

    if result.get("code") == -401:
        print("토큰 만료, 자동 갱신 중...")
        tokens = load_tokens()
        access_token = refresh_access_token(tokens["refresh_token"])
        response = do_send(access_token)
        result = response.json()

    if result.get("result_code") == 0:
        print("카카오톡 메시지 전송 성공!")
    else:
        print(f"메시지 전송 실패: {result}")

if __name__ == "__main__":
    tokens = load_tokens()
    meal_info = get_today_meal()
    if meal_info:
        print(meal_info)
        send_kakao_message(meal_info, tokens["access_token"])
