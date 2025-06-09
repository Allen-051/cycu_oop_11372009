import csv
import os
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# 讀取所有公車路線的名稱與代碼
def load_route_ids_from_csv(csv_path: str):
    route_list = []
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            route_list.append((row['路線名稱'], row['路線代碼']))
    return route_list

# 根據單一路線代碼，擷取站名、站牌ID與經緯度
async def get_stops_with_lat_lon(route_id: str):
    url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id.strip()}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url)
            await page.wait_for_selector("div#GoDirectionRoute li, div#BackDirectionRoute li", timeout=20000)
            html = await page.content()
        except Exception as e:
            print(f"⚠️ 無法讀取路線 {route_id}：{e}")
            await browser.close()
            return []
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    all_stops = []

    for direction, selector in [("去程", "div#GoDirectionRoute li"), ("返程", "div#BackDirectionRoute li")]:
        li_items = soup.select(selector)
        for li in li_items:
            try:
                spans = li.select("span.auto-list-stationlist span")
                inputs = li.select("input")
                if len(spans) >= 3 and len(inputs) >= 3:
                    stop_name = spans[2].get_text(strip=True)
                    stop_id = inputs[0]['value']
                    lat = inputs[1]['value']
                    lon = inputs[2]['value']
                    all_stops.append((direction, stop_name, stop_id, lat, lon))
            except Exception as e:
                print(f"⚠️ 路線 {route_id} 某一站解析失敗：{e}")

    return all_stops


# 主函數：整合所有公車路線資料並儲存為CSV
async def get_bus_stop_lat_lon(csv_input_path: str, csv_output_path: str):
    route_list = load_route_ids_from_csv(csv_input_path)
    results = []

    for route_name, route_id in route_list:
        print(f"🔍 處理：{route_name}（{route_id}）")
        stops = await get_stops_with_lat_lon(route_id)
        for direction, stop_name, stop_id, lat, lon in stops:
            results.append([route_name, route_id, direction, stop_name, stop_id, lat, lon])

    # 寫入 CSV 檔案
    with open(csv_output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["路線名稱", "路線代碼", "方向", "站名", "站牌ID", "緯度", "經度"])
        writer.writerows(results)

    print(f"\n✅ 完成：共擷取 {len(results)} 筆站牌資料，已輸出至：{csv_output_path}")

# 若要直接執行（放在檔案底部）
if __name__ == "__main__":
    input_csv = r"C:\Users\CYCU\Desktop\cycu_oop_11372009\final\0527\taipei_bus_routes.csv"  # 請放置你路線對應檔案
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    output_csv = os.path.join(desktop, "bus_stops_with_lat_lon.csv")
    asyncio.run(get_bus_stop_lat_lon(input_csv, output_csv))
