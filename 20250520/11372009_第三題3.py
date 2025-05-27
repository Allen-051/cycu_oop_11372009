import geopandas as gpd
import matplotlib.pyplot as plt
import folium
import os
import asyncio
import csv
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# === 公車路線站牌資訊擷取 ===
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
                    "lon": float(inputs[2]['value'])
                })

    return result

# === 將公車資訊輸出到 CSV ===
def save_bus_data_to_csv(route_data: dict, route_id: str, output_folder: str):
    output_file = os.path.join(output_folder, f"bus_route_{route_id}.csv")
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["方向", "順序", "站名", "站牌ID", "緯度", "經度"])
        for direction in ["去程", "返程"]:
            for stop in route_data[direction]:
                writer.writerow([direction, stop["順序"], stop["站名"], stop["站牌ID"], stop["lat"], stop["lon"]])
    print(f"公車資訊已儲存至：{output_file}")
    return output_file

# === 繪製公車路線到 Shapefile 的區界圖 ===
def plot_bus_route_on_shapefile(route_data: dict, shapefile_path: str, output_path: str):
    # 讀取 Shapefile
    gdf = gpd.read_file(shapefile_path)

    # 過濾北北基桃的區界資料
    target_cities = ["基隆市", "臺北市", "新北市", "桃園市"]
    gdf = gdf[gdf["COUNTYNAME"].isin(target_cities)]

    # 繪製底圖
    fig, ax = plt.subplots(figsize=(12, 12))
    gdf.plot(ax=ax, color="beige", edgecolor="black", linestyle="--")  # 米色填充，黑色虛線邊界

    # 繪製公車站點和路線
    for direction, color in zip(["去程", "返程"], ["red", "blue"]):
        stops = route_data.get(direction, [])
        if stops:
            # 提取經緯度
            lons, lats = zip(*[(stop["lon"], stop["lat"]) for stop in stops])
            # 繪製路線
            ax.plot(lons, lats, color=color, linewidth=2, label=f"{direction} 路線")
            # 繪製站點
            ax.scatter(lons, lats, color=color, label=f"{direction} 站點")

    # 美化圖表
    ax.set_title("公車路線與北北基桃區界圖", fontsize=16)
    ax.set_axis_off()
    plt.legend(loc="upper right")

    # 儲存圖形
    plt.savefig(output_path, format="jpg")
    plt.show()
    print(f"地圖已儲存至：{output_path}")

# === 主程序 ===
async def main():
    # 輸入公車路線代號
    route_id = input("請輸入公車路線代號（如 0100002200）：").strip()

    # 抓取公車路線資料
    print("\n正在抓取公車路線資料...")
    route_data = await get_bus_route_stops(route_id)

    # 輸出 CSV
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    csv_file = save_bus_data_to_csv(route_data, route_id, desktop)

    # 繪製地圖
    shapefile_path = r"C:\Users\User\Desktop\cycu_oop_11372009\20250520\OFiles_9e222fea-bafb-4436-9b17-10921abc6ef2\TOWN_MOI_1140318.shp"
    output_map_path = os.path.join(desktop, f"bus_route_map_{route_id}.jpg")
    plot_bus_route_on_shapefile(route_data, shapefile_path, output_map_path)

# 執行主程序
if __name__ == "__main__":
    asyncio.run(main())