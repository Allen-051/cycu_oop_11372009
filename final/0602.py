import asyncio
import csv
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

CSV_PATH = r"C:\Users\CYCU\Desktop\cycu_oop_11372009\final\0527\all_bus_stops_by_route.csv"
ROUTE_MAP_CSV = r"C:\Users\CYCU\Desktop\cycu_oop_11372009\final\0527\taipei_bus_routes.csv"

def get_stop_id_by_direction_and_name(direction, stop_name):
    """
    根據方向與站名，回傳該站名對應的站牌ID（唯一）
    """
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["方向"].strip() == direction and row["站名"].strip() == stop_name:
                return row["站牌ID"].strip()
    return None

def load_route_mapping(csv_path):
    """
    讀取路線對應表，回傳 {路線名稱: 公車代碼} 的字典
    """
    mapping = {}
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["路線名稱"].strip()
            code = row["公車代碼"].strip()
            mapping[name] = code
    return mapping

async def fetch_bus_routes(station_id):
    """
    抓取指定站牌的所有公車路線
    """
    url = f"https://ebus.gov.taipei/Stop/RoutesOfStop?Stopid={station_id}"
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        html = await page.content()
        await browser.close()
    soup = BeautifulSoup(html, "html.parser")
    bus_items = soup.select("div#ResultList ul.auto-list-pool li")
    bus_routes = []
    for li in bus_items:
        try:
            bus_number = li.select_one("p.auto-list-routelist-bus").get_text(strip=True)
            bus_routes.append(bus_number)
        except Exception as e:
            print(f"抓取公車路線時發生錯誤：{e}")
    return set(bus_routes)

async def find_direct_bus():
    """
    查詢直達公車
    """
    direction = input("請輸入查詢方向（去程/返程）：").strip()
    if direction not in ("去程", "返程"):
        print("方向輸入錯誤，請輸入「去程」或「返程」")
        return

    start_name = input("請輸入所在車站名稱：").strip()
    dest_name = input("請輸入目的地車站名稱：").strip()

    start_id = get_stop_id_by_direction_and_name(direction, start_name)
    dest_id = get_stop_id_by_direction_and_name(direction, dest_name)

    if not start_id or not dest_id:
        print("站名或方向輸入錯誤，請確認站名與方向是否正確。")
        return

    print(f"所在車站ID: {start_id}, 目的地車站ID: {dest_id}")

    print("正在抓取所在車站的公車路線...")
    routes_1 = await fetch_bus_routes(start_id)
    print("正在抓取目的地車站的公車路線...")
    routes_2 = await fetch_bus_routes(dest_id)

    common_routes = routes_1.intersection(routes_2)
    if not common_routes:
        print("\n沒有公車可以直達兩站。")
        return

    print("\n以下公車可以直達兩站：")
    route_map = load_route_mapping(ROUTE_MAP_CSV)

    for route in sorted(common_routes):
        route_code = route_map.get(route, "（查無代碼）")
        print(f"{route} → 公車代碼：{route_code}")

if __name__ == "__main__":
    asyncio.run(find_direct_bus())