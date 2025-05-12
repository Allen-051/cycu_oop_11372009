import folium
import os
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# 公車路線站牌資訊擷取：改為直接從 HTML 擷取兩個方向（不依賴 tab 點擊）
async def get_bus_route_stops(route_id: str) -> dict:
    url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id.strip()}"
    result = {"去程": [], "返程": []}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        try:
            await page.wait_for_selector("div#GoDirectionRoute li, div#BackDirectionRoute li", timeout=10000)
        except:
            print("無法載入公車站牌頁面，請確認路線代碼是否正確。")
            return result

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    for direction, selector in [("去程", "div#GoDirectionRoute li"), ("返程", "div#BackDirectionRoute li")]:
        station_items = soup.select(selector)
        for idx, li in enumerate(station_items, start=1):
            spans = li.select("span.auto-list-stationlist span")
            inputs = li.select("input")
            if len(spans) >= 3 and len(inputs) >= 3:
                result[direction].append({
                    "順序": idx,
                    "站名": spans[2].get_text(strip=True),
                    "站牌ID": inputs[0]['value'],
                    "lat": float(inputs[1]['value']),
                    "lon": float(inputs[2]['value'])})

    return result

#  畫地圖函數：去程紅圓＋編號；返程藍圓＋編號
def plot_route_map_with_stops(route_data: dict, output_path: str):
    m = folium.Map(location=[25.0330, 121.5654], zoom_start=13)
    for direction, color in zip(["去程", "返程"], ["red", "blue"]):
        stops = route_data.get(direction, [])
        if not stops:
            continue
        for stop in stops:
            folium.CircleMarker(
                location=[stop["lat"], stop["lon"]],
                radius=12,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7
            ).add_child(folium.Popup(f'{direction}：{stop["站名"]}')).add_to(m)

            folium.map.Marker(
                [stop["lat"], stop["lon"]],
                icon=folium.DivIcon(html=f"""<div style="font-size:10pt; color:white; 
                    background:{color}; border-radius:50%; width:18px; height:18px; 
                    text-align:center; line-height:18px;">{stop["順序"]}</div>""")
            ).add_to(m)

    m.save(output_path)
    return output_path

#整合主程序
async def main_query_plot():
    route_id = input("請輸入公車路線代號（如 0100002200）：").strip()

    print("\n正在抓取公車路線資料...")
    route_data = await get_bus_route_stops(route_id)

    for direction in ["去程", "返程"]:
        for stop in route_data[direction]:
            print(f"{direction},{stop['順序']},{stop['站名']},{stop['站牌ID']},{stop['lat']},{stop['lon']}")

    # 詢問儲存路徑
    user_path = input("\n請輸入輸出 HTML 地圖完整檔名（可留空使用桌面）：").strip()
    if not user_path:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        user_path = os.path.join(desktop, f"bus_route_{route_id}.html")

    print("\n正在建立地圖並標註站牌...")
    output_map_path = plot_route_map_with_stops(route_data, user_path)

    print(f"\n地圖已儲存至：{output_map_path}")

# 執行整合程序
if __name__ == "__main__":
    asyncio.run(main_query_plot())
