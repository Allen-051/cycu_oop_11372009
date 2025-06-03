import pandas as pd
import math
import asyncio
import csv
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# 地球半徑常數
EARTH_RADIUS_KM = 6371.0

# 資料來源檔案
STOP_CSV_PATH = r"C:\Users\User\Desktop\cycu_oop_11372009\final\0527\all_bus_stops_by_route.csv"

# 計算兩點距離（公里）
def haversine(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = phi2 - phi1
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c

# 到站時間（模擬為1分鐘）
def get_mock_arrival_time(_):
    return 1

# 依站名找所有站牌 ID
def list_stop_options_by_name(stop_name, csv_path):
    unique_ids = set()
    options = []
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["站名"].strip() == stop_name:
                stop_id = row["站牌ID"].strip()
                if stop_id not in unique_ids:
                    unique_ids.add(stop_id)
                    options.append({"站牌ID": stop_id})
    return options

# 使用者選擇其中一個站牌 ID
def choose_stop_id(stop_label, csv_path):
    stop_name = input(f"請輸入{stop_label}站名：").strip()
    options = list_stop_options_by_name(stop_name, csv_path)
    if not options:
        print(f"找不到站名「{stop_name}」的資料。")
        return None, None
    if len(options) == 1:
        return stop_name, options[0]["站牌ID"]

    print(f"\n找到以下「{stop_name}」的站牌ID：")
    for idx, opt in enumerate(options, 1):
        print(f"{idx}. 站牌ID：{opt['站牌ID']}")
    while True:
        try:
            choice = int(input(f"請選擇{stop_label}對應站牌ID（輸入編號）：").strip())
            if 1 <= choice <= len(options):
                return stop_name, options[choice - 1]["站牌ID"]
            else:
                print("超出選項範圍，請重新輸入。")
        except ValueError:
            print("請輸入有效的編號。")

# 抓取某站經過的所有公車
async def fetch_bus_routes(stop_id):
    url = f"https://ebus.gov.taipei/Stop/RoutesOfStop?Stopid={stop_id}"
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        html = await page.content()
        await browser.close()
    soup = BeautifulSoup(html, "html.parser")
    bus_items = soup.select("div#ResultList ul.auto-list-pool li")
    return set(
        li.select_one("p.auto-list-routelist-bus").get_text(strip=True)
        for li in bus_items if li.select_one("p.auto-list-routelist-bus")
    )

# 從路線中擷取起點與終點之間的段落
def get_direct_segment(route_df, start_name, end_name):
    if start_name not in route_df["站名"].values or end_name not in route_df["站名"].values:
        return None
    idx_start = route_df[route_df["站名"] == start_name].index[0]
    idx_end = route_df[route_df["站名"] == end_name].index[0]
    if idx_start >= idx_end:
        return None
    return route_df.iloc[idx_start:idx_end + 1].reset_index(drop=True)

# 計算段落總距離與時間
def calculate_distance_and_time(segment_df):
    total_distance = 0
    for i in range(len(segment_df) - 1):
        lat1, lon1 = float(segment_df.iloc[i]["緯度"]), float(segment_df.iloc[i]["經度"])
        lat2, lon2 = float(segment_df.iloc[i+1]["緯度"]), float(segment_df.iloc[i+1]["經度"])
        total_distance += haversine(lat1, lon1, lat2, lon2)
    estimated_time = (total_distance / 30) * 60 + get_mock_arrival_time(segment_df.iloc[0]["站名"])
    return round(total_distance, 2), round(estimated_time, 1)

# 主流程
async def main():
    df_stops = pd.read_csv(STOP_CSV_PATH)

    start_name, start_id = choose_stop_id("出發地", STOP_CSV_PATH)
    end_name, end_id = choose_stop_id("目的地", STOP_CSV_PATH)

    if not start_id or not end_id:
        return

    print("\n查詢直達公車...")
    routes_start = await fetch_bus_routes(start_id)
    routes_end = await fetch_bus_routes(end_id)
    direct_routes = routes_start & routes_end

    if not direct_routes:
        print("\n❌ 無直達公車路線，請考慮轉乘方案。")
        return

    print(f"\n✅ 以下公車可直達：{', '.join(direct_routes)}\n")

    for route in direct_routes:
        for direction in ["去程", "返程"]:
            route_df = df_stops[(df_stops["路線名稱"] == route) & (df_stops["方向"] == direction)]
            if route_df.empty:
                continue
            segment_df = get_direct_segment(route_df, start_name, end_name)
            if segment_df is not None:
                dist_km, time_min = calculate_distance_and_time(segment_df)
                print(f"🚌 路線 {route}（{direction}）：距離約 {dist_km} 公里，預估需時 {time_min} 分鐘（含候車時間）")
                break

# 執行主程式
asyncio.run(main())

