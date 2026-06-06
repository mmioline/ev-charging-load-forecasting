import requests
import random
import os

# 配置地址
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:28010/login")
CHARGING_SERVICE_URL = os.getenv("CHARGING_SERVICE_URL", "http://localhost:28012/charging")
SEED_STATION_IDS = [
    int(station_id)
    for station_id in os.getenv("SEED_STATION_IDS", "1,2").split(",")
    if station_id.strip()
]

def get_token():
    """自动化获取 Token"""
    payload = {'username': 'manual_tester', 'password': 'password123'}
    try:
        response = requests.post(USER_SERVICE_URL, data=payload)
        return response.json().get("access_token")
    except Exception as e:
        print(f"无法连接用户服务: {e}")
        return None

def seed_charging_records():
    token = get_token()
    if not token:
        print("Token 获取失败，请检查用户服务地址。")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    print("开始注入种子数据...")
    for i in range(100):
        payload = {
            "station_id": random.choice(SEED_STATION_IDS),
            "duration_minutes": random.randint(30, 120),
            "kwh_consumed": random.randint(10, 50)
        }
        
        try:
            response = requests.post(CHARGING_SERVICE_URL, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"成功模拟第 {i+1} 条充电记录")
            else:
                print(f"充电记录发送失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"无法连接充电服务: {e}")
            break

if __name__ == "__main__":
    seed_charging_records()
