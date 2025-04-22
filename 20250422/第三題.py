import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import folium
import os

async def find_bus_and_plot(route_id: str):
    """
    抓取公車站點資訊，輸出站名，並顯示在地圖上，儲存為 HTML 檔案。
    """
    route_id = route_id.strip()
    url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id}"
    
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

            stop_time = spans[0].get_text(strip=True)
            stop_number = spans[1].get_text(strip=True)
            stop_name = spans[2].get_text(strip=True)

            stop_id = inputs[0]['value']
            latitude = float(inputs[1]['value'])
            longitude = float(inputs[2]['value'])

            station = [stop_time, stop_number, stop_name, stop_id, latitude, longitude]
            all_stations.append(station)

        except Exception as e:
            print(f"第 {idx} 筆資料處理錯誤：{e}")

    if not all_stations:
        print("沒有成功抓取到任何站牌資訊。")
        return

    # 輸出所有站名
    print("\n抓到的站牌資訊如下：")
    for station in all_stations:
        print(f"站名: {station[2]}")

    # 建立地圖
    m = folium.Map(location=[all_stations[0][4], all_stations[0][5]], zoom_start=13)  # 以第一個站點為中心

    # 將站點加入地圖
    for station in all_stations:
        stop_name = station[2]
        latitude = station[4]
        longitude = station[5]
        folium.Marker(
            location=[latitude, longitude],
            popup=f"站名: {stop_name}",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    # 儲存地圖為 HTML
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_file = os.path.join(desktop_path, f"bus_stops_map_{route_id}.html")
    m.save(output_file)

    print(f"\n地圖已儲存至 {output_file}")

# 執行主程式
if __name__ == "__main__":
    route_id = input("請告訴我公車代碼：").strip()  # 在主程式中取得 route_id
    asyncio.run(find_bus_and_plot(route_id))