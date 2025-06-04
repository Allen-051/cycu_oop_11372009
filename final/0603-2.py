import asyncio
import csv
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
import os

async def get_lat_lon_from_html(route_id):
    """
    根據路線代碼抓取站牌的經緯度
    """
    url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id.strip()}"
    all_stops_data = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, timeout=2_000_000)  # 設定超長timeout
            await page.wait_for_selector("div#GoDirectionRoute li, div#BackDirectionRoute li", timeout=2_000_000)
            html = await page.content()
            await browser.close()
        soup = BeautifulSoup(html, "html.parser")
        # ...原本的資料擷取程式...
        for direction_label, selector in [("去程", "div#GoDirectionRoute li"), ("返程", "div#BackDirectionRoute li")]:
            station_items = soup.select(selector)
            if not station_items:
                continue
            for li in station_items:
                try:
                    spans = li.select("span.auto-list-stationlist span")
                    inputs = li.select("input")
                    stop_name = spans[2].get_text(strip=True)
                    stop_id = inputs[0]['value']
                    latitude = inputs[1]['value']
                    longitude = inputs[2]['value']
                    all_stops_data.append({
                        "方向": direction_label,
                        "站牌名稱": stop_name,
                        "站牌ID": stop_id,
                        "緯度": latitude,
                        "經度": longitude
                    })
                except Exception as e:
                    print(f"抓取資料時發生錯誤：{e}")
    except Exception as e:
        print(f"⚠️ 路線 {route_id} 連線失敗或超時（略過）：{e}")
        return []
    return all_stops_data

# 儲存結果至 CSV
def save_to_csv(all_data, csv_output_path):
    with open(csv_output_path, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["方向", "站牌名稱", "站牌ID", "緯度", "經度"])
        writer.writeheader()
        writer.writerows(all_data)

# 主函數：遍歷每條公車路線，抓取經緯度並儲存
async def main(csv_input_path, csv_output_path):
    # 讀取路線資料
    df_routes = pd.read_csv(csv_input_path)
    all_stops_data = []

    for route_id in df_routes["路線代碼"]:
        print(f"📡 正在抓取路線 {route_id} 的資料...")
        route_data = await get_lat_lon_from_html(route_id)
        all_stops_data.extend(route_data)

    # 儲存至 CSV
    save_to_csv(all_stops_data, csv_output_path)
    print(f"\n 資料已儲存至：{csv_output_path}")

# 執行主程式
if __name__ == "__main__":
    csv_input_path = r"C:\Users\CYCU\Desktop\cycu_oop_11372009\final\0527\taipei_bus_routes.csv"  # 讀取公車路線資料 CSV 檔
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    csv_output_path = os.path.join(desktop, "bus_stops_with_lat_lon.csv")  # 輸出檔案到桌面

    asyncio.run(main(csv_input_path, csv_output_path))
