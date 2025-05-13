import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import csv
import os

async def get_bus_info_go(bus_id):
    bus_id = input("請告訴我公車代碼：").strip()
    url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={bus_id}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        try:
            await page.wait_for_selector("div#GoDirectionRoute li", timeout=10000)
        except:
            print("網頁載入超時，請確認公車代碼是否正確。")
            return

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    station_items = soup.select("div#GoDirectionRoute li")

    if not station_items:
        print("未找到任何站牌資料，請確認公車代碼是否正確。")
        return

    all_stations = []

    for idx, li in enumerate(station_items, start=1):
        try:
            spans = li.select("span.auto-list-stationlist span")
            inputs = li.select("input")

            stop_id = inputs[0]['value']
            
            station = [stop_id]
            all_stations.append(station)

        except Exception as e:
            print(f"第 {idx} 筆資料處理錯誤：{e}")

    if not all_stations:
        print("沒有成功抓取到任何站牌資訊。")
        return


    print("\n抓到的站牌資訊如下：\n")
    for station in all_stations:
        print(", ".join(station))  # 顯示時省略 raw_html

# 執行主程式
if __name__ == "__main__":
    asyncio.run(get_bus_info_go('bus_id'))
