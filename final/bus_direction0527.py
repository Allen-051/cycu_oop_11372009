import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def get_routes_by_stop_name(stop_name: str) -> set:
    url = "https://ebus.gov.taipei/"
    routes = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        await page.fill("input#stopInput", stop_name)
        await page.keyboard.press("Enter")

        try:
            await page.wait_for_selector("div.stop-data > div", timeout=8000)
            html = await page.content()
        except:
            print(f"查無 {stop_name} 的資料")
            await browser.close()
            return routes

        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    route_sections = soup.select("div.stop-data > div")

    for section in route_sections:
        spans = section.select("span.routeid")
        for sp in spans:
            routes.add(sp.text.strip())

    return routes

async def find_direct_buses_between_stops():
    start = input("請輸入出發地（例如：台北101）：").strip()
    end = input("請輸入目的地（例如：松山車站）：").strip()

    print(f"\n🔍 正在查詢「{start}」經過的路線...")
    start_routes = await get_routes_by_stop_name(start)
    print(f"🔍 正在查詢「{end}」經過的路線...")
    end_routes = await get_routes_by_stop_name(end)

    if not start_routes or not end_routes:
        print("查詢失敗，站名可能輸入錯誤")
        return

    direct_routes = sorted(start_routes & end_routes)

    if direct_routes:
        print(f"\n從「{start}」可直達「{end}」的公車路線：")
        for route in direct_routes:
            print(f"🚌 {route}")
    else:
        print(f"\n無法從「{start}」直達「{end}」，建議查詢轉乘")

if __name__ == "__main__":
    asyncio.run(find_direct_buses_between_stops())
