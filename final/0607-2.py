import pandas as pd
import math
import folium
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import os
from branca.element import Template, MacroElement

# Haversine 距離計算 (公尺)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = phi2 - phi1
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c * 1000

# 使用 playwright 擷取公車到站時間
async def get_real_time_info(route_id: str):
    url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id.strip()}"
    result = {"去程": [], "返程": []}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url)
            await page.wait_for_selector("div#GoDirectionRoute li, div#BackDirectionRoute li", timeout=20000)
            html = await page.content()
        except:
            await browser.close()
            return result
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    for direction, selector in [("去程", "div#GoDirectionRoute li"), ("返程", "div#BackDirectionRoute li")]:
        for li in soup.select(selector):
            spans = li.select("span.auto-list-stationlist span")
            inputs = li.select("input")
            if len(spans) >= 3 and len(inputs) >= 3:
                stop_name = spans[2].get_text(strip=True)
                stop_id = inputs[0]['value']
                eta_text = spans[0].get_text(strip=True)
                lat = float(inputs[1]['value'])
                lon = float(inputs[2]['value'])
                result[direction].append({
                    "站名": stop_name,
                    "站牌ID": stop_id,
                    "到站時間": eta_text,
                    "lat": lat,
                    "lon": lon
                })
    return result

# 主流程
async def main():
    df = pd.read_csv(r"C:\Users\CYCU\Desktop\cycu_oop_11372009\final\0527\bus_stops_with_lat_lon.csv")
    start_name = input("請輸入起始站（中文）: ").strip()
    end_name = input("請輸入終點站（中文）: ").strip()

    candidates = df[df["站名"].isin([start_name, end_name])]
    route_groups = candidates.groupby("路線代碼").filter(lambda g: g["站名"].nunique() == 2)
    matched_routes = route_groups["路線代碼"].unique()

    if len(matched_routes) == 0:
        print("❌ 沒有找到同一條路線包含起點與終點")
        return

    for route_id in matched_routes:
        route_df = df[df["路線代碼"] == route_id].copy().reset_index(drop=True)
        route_df["順序"] = route_df.groupby("方向").cumcount() + 1
        direction = route_df[route_df["站名"] == start_name]["方向"].values[0]
        sub_df = route_df[route_df["方向"] == direction].reset_index(drop=True)

        try:
            idx_start = sub_df[sub_df["站名"] == start_name].index[0]
            idx_end = sub_df[sub_df["站名"] == end_name].index[0]
        except IndexError:
            continue

        if idx_start >= idx_end:
            continue

        segment = sub_df.iloc[idx_start:idx_end+1].copy()
        num_stations = len(segment) - 1

        real_time = await get_real_time_info(route_id)
        eta_str = next((s["到站時間"] for s in real_time[direction] if s["站名"] == start_name), "1")
        wait_min = 1
        if "分鐘" in eta_str:
            try:
                wait_min = int(eta_str.replace("分鐘", "").strip())
            except:
                wait_min = 1

        total_distance = 0
        for i in range(len(segment)-1):
            total_distance += haversine(segment.iloc[i]["緯度"], segment.iloc[i]["經度"],
                                        segment.iloc[i+1]["緯度"], segment.iloc[i+1]["經度"])
        time_min = round((total_distance / 1000) / 8 * 60 + wait_min, 1)

        # 地圖建立
        m = folium.Map(location=[segment.iloc[0]["緯度"], segment.iloc[0]["經度"]], zoom_start=14)

        html_box = f"""
            <div id='custom-float-box' style="
                position: fixed;
                bottom: 40px;
                right: 40px;
                z-index: 9999;
                font-size:10pt;
                font-size:10pt;
                background-color:white;
                width:160px;
                height:250px;
                padding:10px;
                border:1px solid #333;
                border-radius:10px;
                text-align:center;
                box-shadow: 3px 3px 5px gray;">
                <strong>🚌 路線名稱</strong><br>{segment.iloc[0]['路線名稱']}<br><br>
                <strong>🚏 總站數</strong><br>{num_stations}<br><br>
                <strong>🛣️ 通勤距離</strong><br>{round(total_distance)} 公尺<br><br>
                <strong>🕒 預估時間</strong><br>{time_min} 分鐘
            </div>
        """
        folium.Marker(
            location=[segment.iloc[0]["緯度"] + 0.002, segment.iloc[0]["經度"]],
            icon=folium.DivIcon(html=html_box)
        ).add_to(m)

        for idx, row in segment.iterrows():
            popup = folium.Popup(row["站名"], parse_html=True)
            if row["站名"] == start_name:
                folium.Marker(
                    location=[row["緯度"], row["經度"]],
                    popup=popup,
                    icon=folium.DivIcon(html=f"""
                        <div style="background:green; color:white; font-size:14pt;
                                    border-radius:50%; width:40px; height:40px;
                                    text-align:center; line-height:40px;">
                            GO
                        </div>
                    """)
                ).add_to(m)
            elif row["站名"] == end_name:
                folium.Marker(
                    location=[row["緯度"], row["經度"]],
                    popup=popup,
                    icon=folium.Icon(color="red", icon="flag", prefix="fa")
                ).add_to(m)
            else:
                folium.Marker(
                    location=[row["緯度"], row["經度"]],
                    popup=popup,
                    icon=folium.DivIcon(html=f"""
                        <div style="font-size:12pt; background:#444; color:white;
                                    border-radius:50%; width:24px; height:24px;
                                    text-align:center; line-height:24px;">
                            {idx + 1}
                        </div>
                    """)
                ).add_to(m)

        folium.PolyLine(
            locations=segment[["緯度", "經度"]].values.tolist(),
            color="blue",
            weight=5,
            opacity=0.8
        ).add_to(m)

        # 儲存至桌面
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        map_file = os.path.join(desktop, f"bus_map_{route_id}.html")
        m.save(map_file)
        print(f"\n🗺️ 已完成地圖繪製並儲存：{map_file}")
        print(f"✅ 路線名稱：{segment.iloc[0]['路線名稱']}，方向：{direction}")
        print(f"從「{start_name}」到「{end_name}」共 {num_stations} 站，約 {round(total_distance)} 公尺，預估 {time_min} 分鐘")

# 執行
if __name__ == "__main__":
    asyncio.run(main())
