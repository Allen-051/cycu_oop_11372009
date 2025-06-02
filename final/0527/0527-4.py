import csv
import os
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

#  讀取路線代碼產生所有公車站牌id的清單
def load_route_ids_from_csv(csv_path: str):
    route_list = []
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            route_list.append((row['路線名稱'], row['公車代碼']))
    return route_list

#  擷取該公車路線的所有站名與站牌ID
async def get_stops_by_route(route_id: str):
    url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id.strip()}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        try:
            await page.wait_for_selector("div#GoDirectionRoute li, div#BackDirectionRoute li", timeout=10000)
        except:
            print(f" 無法讀取 routeid={route_id}")
            await browser.close()
            return []
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    all_stops = []

    for section in [("去程", "div#GoDirectionRoute li"), ("返程", "div#BackDirectionRoute li")]:
        direction, selector = section
        li_items = soup.select(selector)
        for li in li_items:
            spans = li.select("span.auto-list-stationlist span")
            inputs = li.select("input")
            if len(spans) >= 3 and len(inputs) >= 3:
                stop_name = spans[2].get_text(strip=True)
                stop_id = inputs[0]['value']
                all_stops.append((direction, stop_name, stop_id))
    return all_stops

#  主函數：逐個 route 擷取資料並儲存
async def main_extract_all_stops(csv_input_path: str, csv_output_path: str):
    route_list = load_route_ids_from_csv(csv_input_path)

    results = []
    for route_name, route_id in route_list:
        print(f"\n 處理公車：{route_name}（{route_id}）")
        stops = await get_stops_by_route(route_id)
        for direction, stop_name, stop_id in stops:
            print(f"{route_name},{route_id},{direction},{stop_name},{stop_id}")
            results.append([route_name, route_id, direction, stop_name, stop_id])

    # 儲存 CSV
    with open(csv_output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["路線名稱", "路線代碼", "方向", "站名", "站牌ID"])
        writer.writerows(results)

    print(f"\n全部資料已輸出至：{csv_output_path}")

# 執行程式（手動設定路徑）
if __name__ == "__main__":
    input_csv = r"C:\Users\CYCU\Desktop\taipei_bus_routes.csv"  # 請換成你實際的路線代碼檔案
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    output_csv = os.path.join(desktop, "all_bus_stops_by_route.csv")
    asyncio.run(main_extract_all_stops(input_csv, output_csv))
