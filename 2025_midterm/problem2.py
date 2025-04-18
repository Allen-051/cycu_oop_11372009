from datetime import datetime

def analyze_date():
    try:
        # 請使用者輸入日期
        user_input = input("請輸入日期 (格式: YYYY-MM-DD HH:MM): ")
        input_date = datetime.strptime(user_input, "%Y-%m-%d %H:%M")
    except ValueError:
        print("輸入格式錯誤，請使用 YYYY-MM-DD HH:MM 格式")
        return

    # 1. 輸出該日期為星期幾
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekdays[input_date.weekday()]
    print(f"該日期為: {weekday}")

    # 2. 輸出該日期是當年的第幾天
    day_of_year = input_date.timetuple().tm_yday
    print(f"該日期是當年的第 {day_of_year} 天")

    # 3. 計算輸入時間到現在經過的太陽日
    now = datetime.now()
    delta = now - input_date
    julian_days = delta.total_seconds() / 86400  # 1 太陽日 = 86400 秒
    print(f"從輸入的時間到現在，共經過 {julian_days:.4f} 太陽日")

# 呼叫函數
analyze_date()