import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

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
    station_id_1 = input("請輸入所在車站的站牌代碼：").strip()
    station_id_2 = input("請輸入目的地車站的站牌代碼：").strip()

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