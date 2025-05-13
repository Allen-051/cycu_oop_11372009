import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import time

async def fetch_ebus_snapshot():
    url = "https://ebus.gov.taipei/ebus"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        await page.wait_for_timeout(3000)  # 等待 JavaScript 載入
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # 假設某些 class 或 span 包含公車資訊（需根據真實網頁調整）
    vehicle_info = []
    for item in soup.select("div.bus-info"):
        route = item.select_one("span.routeid")
        plate = item.select_one("span.platenumber")
        if route and plate:
            vehicle_info.append({
                "route": route.text.strip(),
                "plate": plate.text.strip()
            })

    return vehicle_info

async def run_periodic_scraper(interval=10):
    while True:
        print(f"\n抓取時間：{time.strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            data = await fetch_ebus_snapshot()
            print(f"擷取到 {len(data)} 筆資料")
            for d in data:
                print(f"路線：{d['route']}, 車牌：{d['plate']}")
        except Exception as e:
            print(f"發生錯誤：{e}")

        await asyncio.sleep(interval)

# 主程序啟動
if __name__ == "__main__":
    asyncio.run(run_periodic_scraper(10))
