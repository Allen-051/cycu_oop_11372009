from datetime import datetime, timedelta

def calculate_julian_date(input_time_str):
    # 定義 Julian 日期的有效起始點 (公元 1 年 1 月 1 日中午)
    julian_start = datetime(1, 1, 1, 12)  # 公元 1 年 1 月 1 日中午
    julian_offset = 1721425.5  # Julian 日期從公元前 4713 年 1 月 1 日中午開始的偏移量

    # 將輸入的時間字串轉換為 datetime 物件
    try:
        input_time = datetime.strptime(input_time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        print("輸入的時間格式錯誤，請使用 YYYY-MM-DD HH:MM 格式")
        return

    # 計算該天是星期幾（中文）
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday_index = input_time.weekday()  # 0 表示星期一，6 表示星期日
    weekday = weekdays[weekday_index]
    print(f"輸入的日期是：{weekday}")

    # 計算 Julian 日期
    now = datetime.now()
    julian_date_input = (input_time - julian_start).total_seconds() / 86400.0 + julian_offset
    julian_date_now = (now - julian_start).total_seconds() / 86400.0 + julian_offset

    # 計算從輸入時間到現在的 Julian 日數差
    elapsed_days = julian_date_now - julian_date_input

    print(f"輸入時間的 Julian 日期為：{julian_date_input:.2f}")
    print(f"目前時間的 Julian 日期為：{julian_date_now:.2f}")
    print(f"從輸入時間到現在經過的太陽日數為：{elapsed_days:.2f}")

# 測試函數
input_time_str = input("請輸入時間（格式為 YYYY-MM-DD HH:MM，例如 2020-04-15 20:30）：")
calculate_julian_date(input_time_str)