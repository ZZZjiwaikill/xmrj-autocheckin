import requests
import os
import json
from datetime import datetime

# 从配置文件导入
try:
    from config import MOBILE, HEADERS, ENABLE_DAILY_CHECKIN_LIMIT
except ImportError:
    print("请创建config.py文件并配置你的个人信息")
    exit(1)

# 以下参数一般不需要修改
REASON = "签到"
BASE_URL = "https://www.lilibibi.cn"

# 打卡历史记录文件
CHECKIN_RECORD_FILE = "checkin_history.json"

def load_checkin_history():
    """加载打卡历史记录"""
    if os.path.exists(CHECKIN_RECORD_FILE):
        try:
            with open(CHECKIN_RECORD_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_checkin_history(history):
    """保存打卡历史记录"""
    with open(CHECKIN_RECORD_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def has_checked_today():
    """检查今天是否已经打卡"""
    history = load_checkin_history()
    today = datetime.now().strftime("%Y-%m-%d")
    return today in history

def record_checkin(success=True, points=0):
    """记录今日打卡"""
    history = load_checkin_history()
    today = datetime.now().strftime("%Y-%m-%d")
    history[today] = {
        "time": datetime.now().isoformat(),
        "success": success,
        "points_earned": points
    }
    save_checkin_history(history)

def get_points(session, mobile):
    url = f"{BASE_URL}/users_points/getManyByEqualFields"
    resp = session.post(url, headers=HEADERS, json={"mobile": mobile}, verify=False)
    resp.raise_for_status()
    points_list = resp.json().get("points", [])
    if points_list:
        # 获取最新一条积分
        return points_list[-1]["AfterPoints"]
    else:
        return 0

def get_timestamp(session):
    url = f"{BASE_URL}/users/getTimeStamp"
    resp = session.get(url, headers=HEADERS, verify=False)
    resp.raise_for_status()
    return int(resp.json()["timeStamp"])

def checkin(session, mobile, reason, before_points, after_points, create_time):
    url = f"{BASE_URL}/users_points/save"
    payload = {
        "Mobile": mobile,
        "ProcessPoints": after_points - before_points,
        "Reason": reason,
        "BeforePoints": before_points,
        "AfterPoints": after_points,
        "CreateTime": str(create_time)
    }
    resp = session.put(url, headers=HEADERS, json=payload, verify=False)
    resp.raise_for_status()
    return resp.json()

def main():
    # 检查今天是否已经打卡
    if has_checked_today():
        if ENABLE_DAILY_CHECKIN_LIMIT:
            print("今日已打卡，跳过执行")
            return
        else: 
            print("今日已打卡，但未启用每日仅能打卡1次限制功能，继续执行")
    else:
        print("今日未打卡，开始打卡~")
    
    session = requests.Session()
    try:
        print("正在获取当前积分...")
        before_points = get_points(session, MOBILE)
        print("当前积分：", before_points)
        print("正在获取服务器时间戳...")
        create_time = get_timestamp(session)
        print("时间戳：", create_time)
        after_points = before_points + 10  # 默认打卡加10分
        print("正在打卡...")
        result = checkin(session, MOBILE, REASON, before_points, after_points, create_time)
        print("打卡结果：", result)
        
        # 记录成功打卡
        record_checkin(success=True, points=10)
        print("打卡成功，已记录")
        
    except Exception as e:
        print(f"打卡失败: {e}")
        # 记录失败打卡
        record_checkin(success=False, points=0)

if __name__ == "__main__":
    main()