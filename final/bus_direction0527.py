import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def fetch_station_id(station_name):
    """
    根據站牌名稱查詢站牌代碼
    """
    url = f"https://ebus.gov.taipei/Station/Search?keyword={station_name}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # 假設站牌代碼在某個特定的 HTML 標籤中（需根據實際網頁調整）
    try:
        station_id = soup.select_one("div.station-id").get_text(strip=True)
        return station_id
    except Exception as e:
        print(f"無法找到站牌代碼，請檢查站牌名稱是否正確：{e}")
        return None

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

    # 抓取該站牌的所有公車路線
    bus_items = soup.select("div#ResultList ul.auto-list-pool li")
    bus_routes = []

    for li in bus_items:
        try:
            # 抓取公車號碼
            bus_number = li.select_one("p.auto-list-routelist-bus").get_text(strip=True)
            bus_routes.append(bus_number)
        except Exception as e:
            print(f"抓取公車路線時發生錯誤：{e}")

    return set(bus_routes)  # 返回集合以便後續比較

async def find_direct_bus():
    """
    檢查兩個站牌是否有公車可以直達
    """
    station_name_1 = input("請輸入所在車站的站牌名稱：").strip()
    station_name_2 = input("請輸入目的地車站的站牌名稱：").strip()

    # 將站牌名稱轉換為站牌代碼
    print("正在查詢第一個站牌的代碼...")
    station_id_1 = await fetch_station_id(station_name_1)
    if not station_id_1:
        print("無法找到第一個站牌的代碼，請檢查名稱是否正確。")
        return

    print("正在查詢第二個站牌的代碼...")
    station_id_2 = await fetch_station_id(station_name_2)
    if not station_id_2:
        print("無法找到第二個站牌的代碼，請檢查名稱是否正確。")
        return

    # 分別抓取兩個站牌的公車路線
    print("正在抓取第一個站牌的公車路線...")
    routes_1 = await fetch_bus_routes(station_id_1)
    print("正在抓取第二個站牌的公車路線...")
    routes_2 = await fetch_bus_routes(station_id_2)

    # 找出兩站共有的公車路線
    common_routes = routes_1.intersection(routes_2)

    if common_routes:
        print("\n以下公車可以直達兩站：")
        for route in common_routes:
            print(route)
    else:
        print("\n沒有公車可以直達兩站。")

# 執行函數
if __name__ == "__main__":
    asyncio.run(find_direct_bus())