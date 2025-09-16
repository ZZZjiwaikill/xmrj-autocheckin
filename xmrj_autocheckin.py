import requests
import os
import json
from datetime import datetime
import importlib

# 支持单人或多人打卡
config_module = ["config"]   # 单人打卡格式示例
# config_module = ["config_A","config_B","config_C"]  # 多人打卡格式示例

# 以下参数一般不需要修改
REASON = "签到"
BASE_URL = "https://www.lilibibi.cn"

# 打卡历史记录文件
CHECKIN_RECORD_FILE = "checkin_history.json"

def load_checkin_history():
    """加载所有人的打卡历史记录"""
    if os.path.exists(CHECKIN_RECORD_FILE):
        try:
            with open(CHECKIN_RECORD_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_checkin_history(history):
    """保存所有人的打卡历史记录"""
    with open(CHECKIN_RECORD_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def has_checked_today(mobile):
    """检查某人今天是否已经打卡"""
    history = load_checkin_history()
    today = datetime.now().strftime("%Y-%m-%d")
    return mobile in history and today in history[mobile]

def record_checkin(mobile, success=True, points=0):
    """记录某人的今日打卡"""
    history = load_checkin_history()
    today = datetime.now().strftime("%Y-%m-%d")
    if mobile not in history:
        history[mobile] = {}
    # 覆盖同一个人同一天的打卡记录
    history[mobile][today] = {
        "time": datetime.now().isoformat(),
        "success": success,
        "points_earned": points
    }
    save_checkin_history(history)

def get_points(session, mobile, HEADERS):
    url = f"{BASE_URL}/users_points/getManyByEqualFields"
    resp = session.post(url, headers=HEADERS, json={"mobile": mobile}, verify=False)
    resp.raise_for_status()
    points_list = resp.json().get("points", [])
    if points_list:
        # 获取最新一条积分
        return points_list[-1]["AfterPoints"]
    else:
        return 0

def get_timestamp(session, HEADERS):
    url = f"{BASE_URL}/users/getTimeStamp"
    resp = session.get(url, headers=HEADERS, verify=False)
    resp.raise_for_status()
    return int(resp.json()["timeStamp"])

def checkin(session, mobile, HEADERS, reason, before_points, after_points, create_time):
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

def main(MOBILE, HEADERS, ENABLE_DAILY_CHECKIN_LIMIT):
    # 检查今天是否已经打卡
    if has_checked_today(MOBILE):
        if ENABLE_DAILY_CHECKIN_LIMIT:
            print(f"{MOBILE} 今日已打卡，跳过执行")
            return
        else: 
            print(f"{MOBILE} 今日已打卡，但未启用每日仅能打卡1次限制功能，继续执行")
    else:
        print(f"{MOBILE} 今日未打卡，开始打卡~")
    session = requests.Session()
    try:
        print("正在获取当前积分...")
        before_points = get_points(session, MOBILE, HEADERS)
        print("当前积分：", before_points)
        print("正在获取服务器时间戳...")
        create_time = get_timestamp(session, HEADERS)
        print("时间戳：", create_time)
        after_points = before_points + 10  # 默认打卡加10分
        print("正在打卡...")
        result = checkin(session, MOBILE, HEADERS, REASON, before_points, after_points, create_time)
        print("打卡结果：", result)
        # 记录成功打卡
        record_checkin(MOBILE, success=True, points=10)
        print("打卡成功，已记录\n--- done ---\n")
    except Exception as e:
        print(f"打卡失败: {e}\n--- done ---\n")
        # 记录失败打卡
        record_checkin(MOBILE, success=False, points=0)

def run_for_config(config_name):
    config = importlib.import_module(config_name)
    MOBILE = config.MOBILE
    HEADERS = config.HEADERS
    ENABLE_DAILY_CHECKIN_LIMIT = config.ENABLE_DAILY_CHECKIN_LIMIT
    main(MOBILE, HEADERS, ENABLE_DAILY_CHECKIN_LIMIT)

if __name__ == "__main__":
    for cfg in config_module:
        print(f"正在为 {cfg} 执行打卡...")
        run_for_config(cfg)