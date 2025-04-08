import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def find_bus():
    route_id = input("請告訴我公車代碼：").strip()
    url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)  # 不等待網路穩定
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # 尋找所有站牌清單的 li 元素
    station_items = soup.select("div#GoDirectionRoute li")

    all_stations = []

    for idx, li in enumerate(station_items, start=1):
        try:
            spans = li.select("span.auto-list-stationlist span")
            inputs = li.select("input")

            time_to = spans[0].get_text(strip=True)  # 修改變數名稱為 time_to
            stop_number = spans[1].get_text(strip=True)
            stop_name = spans[2].get_text(strip=True)

            stop_id = inputs[0]['value']
            latitude = inputs[1]['value']
            longitude = inputs[2]['value']

            # 將資料以逗號分隔的格式存入陣列
            station = f"{time_to},{stop_number},{stop_name},{stop_id},{latitude},{longitude}"
            all_stations.append(station)
        except Exception as e:
            print(f"error 第 {idx} 筆資料處理錯誤：{e}")

    print("\n 抓到的站牌資訊：\n")
    for station in all_stations:
        print(station)

# 執行函數
if __name__ == "__main__":
    asyncio.run(find_bus())