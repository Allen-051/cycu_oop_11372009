import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import csv
import os
import folium

CSV_PATH = r"C:\Users\CYCU\Desktop\cycu_oop_11372009\final\0527\all_bus_stops_by_route.csv"
ROUTE_MAP_CSV = r"C:\Users\CYCU\Desktop\cycu_oop_11372009\final\0527\taipei_bus_routes.csv"

def load_route_mapping(csv_path):
    mapping = {}
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["路線名稱"].strip()
            code = row["路線代碼"].strip()
            mapping[name] = code
    return mapping

def list_stop_options_by_name(stop_name):
    unique_ids = set()
    options = []
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["站牌名稱"].strip() == stop_name:
                stop_id = row["站牌ID"].strip()
                if stop_id not in unique_ids:
                    unique_ids.add(stop_id)
                    options.append({"站牌ID": stop_id})
    return options

async def fetch_bus_routes(station_id):
    url = f"https://ebus.gov.taipei/Stop/RoutesOfStop?Stopid={station_id}"
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        html = await page.content()
        await browser.close()
    soup = BeautifulSoup(html, "html.parser")
    bus_items = soup.select("div#ResultList ul.auto-list-pool li")
    return {li.select_one("p.auto-list-routelist-bus").get_text(strip=True) for li in bus_items}

async def get_bus_route_stops(route_id: str) -> dict:
    url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id.strip()}"
    result = {"去程": [], "返程": []}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        try:
            await page.wait_for_selector("div#GoDirectionRoute li, div#BackDirectionRoute li", timeout=80000)
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
            arrival_time = "無資料"
            try:
                arrival_time = spans[0].get_text(strip=True)
            except Exception:
                pass
            if len(spans) >= 3 and len(inputs) >= 3:
                result[direction].append({
                    "順序": idx,
                    "站牌名稱": spans[2].get_text(strip=True),
                    "站牌ID": inputs[0]['value'],
                    "lat": float(inputs[1]['value']),
                    "lon": float(inputs[2]['value']),
                    "到站時間": arrival_time
                })
    return result

def plot_combined_segment_map(route_id, route_data, start_name, dest_name, output_path):
    m = folium.Map(location=[25.0330, 121.5654], zoom_start=13)
    segment_color = "orange"
    valid_direction = None
    all_stops = []

    for direction in ["去程", "返程"]:
        stops = route_data.get(direction, [])
        try:
            idx_start = next(i for i, stop in enumerate(stops) if stop["站牌名稱"] == start_name)
            idx_end = next(i for i, stop in enumerate(stops) if stop["站牌名稱"] == dest_name)
            if idx_start <= idx_end:
                valid_direction = direction
                all_stops = stops
                break
        except StopIteration:
            continue

    if not valid_direction:
        print("⚠️ 無法在任一方向中找到符合順序的起點與終點，無法繪圖。")
        return

    coords_all = []
    for i, stop in enumerate(all_stops, start=1):
        coords_all.append((stop["lat"], stop["lon"]))
        folium.CircleMarker(
            location=(stop["lat"], stop["lon"]),
            radius=8,
            color=segment_color,
            fill=True,
            fill_color=segment_color,
            fill_opacity=0.7
        ).add_child(folium.Popup(f'{valid_direction}：{stop["站牌名稱"]}\n即時到站時間：{stop.get("到站時間", "無資料")}')).add_to(m)

        folium.map.Marker(
            [stop["lat"], stop["lon"]],
            icon=folium.DivIcon(html=f"""<div style="font-size:10pt; color:white;
                background:{segment_color}; border-radius:50%; width:18px; height:18px;
                text-align:center; line-height:18px;">{i}</div>""")
        ).add_to(m)

    folium.PolyLine(coords_all, color=segment_color, weight=4, opacity=0.9).add_to(m)

    for stop in all_stops:
        if stop["站牌名稱"] == start_name:
            folium.Marker(
                location=[stop['lat'], stop['lon']],
                popup=f"起點站：{stop['站牌名稱']}\n即時到站時間：{stop.get('到站時間', '無資料')}",
                icon=folium.Icon(color="green", icon="play")
            ).add_to(m)
        if stop["站牌名稱"] == dest_name:
            folium.Marker(
                location=[stop['lat'], stop['lon']],
                popup=f"終點站：{stop['站牌名稱']}\n即時到站時間：{stop.get('到站時間', '無資料')}",
                icon=folium.Icon(color="darkred", icon="flag")
            ).add_to(m)

    # ✅ 新增推估公車位置（根據到站時間）
    estimated_bus_idx = None
    for i, stop in enumerate(all_stops):
        eta = stop.get("到站時間", "")
        if "進站" in eta or "即將" in eta or "1分" in eta:
            estimated_bus_idx = i
            break
        elif "分鐘" in eta:
            try:
                mins = int(eta.replace("分鐘", "").strip())
                if mins <= 2:
                    estimated_bus_idx = i
                    break
            except:
                continue

    if estimated_bus_idx is not None and estimated_bus_idx > 0:
        lat1, lon1 = all_stops[estimated_bus_idx - 1]["lat"], all_stops[estimated_bus_idx - 1]["lon"]
        lat2, lon2 = all_stops[estimated_bus_idx]["lat"], all_stops[estimated_bus_idx]["lon"]
        est_lat = (lat1 + lat2) / 2
        est_lon = (lon1 + lon2) / 2

        folium.Marker(
            location=[est_lat, est_lon],
            icon=folium.Icon(color="blue", icon="bus", prefix='fa'),
            popup="🚌 推估公車目前所在區間"
        ).add_to(m)

    
    # === 預估總花費時間（等車 + 車程） ===
    try:
        idx_start = next(i for i, stop in enumerate(all_stops) if stop["站牌名稱"] == start_name)
        idx_end = next(i for i, stop in enumerate(all_stops) if stop["站牌名稱"] == dest_name)
    except StopIteration:
        idx_start, idx_end = 0, 0

    eta_str = all_stops[idx_start].get("到站時間", "")
    wait_min = 0
    if "進站" in eta_str or "即將" in eta_str:
        wait_min = 0
    elif "分鐘" in eta_str:
        try:
            wait_min = int(eta_str.replace("分鐘", "").strip())
        except:
            wait_min = 0

    num_stations = max(0, idx_end - idx_start)
    ride_min = num_stations * 2  # 每站預估 2 分鐘（可自行調整）
    total_time = wait_min + ride_min

    # 顯示於起點站旁邊（略為向北偏移）
    offset_lat = all_stops[idx_start]["lat"] + 0.0015
    offset_lon = all_stops[idx_start]["lon"]

    folium.Marker(
        location=[offset_lat, offset_lon],
        icon=folium.Icon(color="purple", icon="info-sign"),
        popup=f"🕒 預估總花費時間：約 {total_time} 分鐘\n（等車 {wait_min} 分 + 車程 {ride_min} 分）"
    ).add_to(m)

    m.save(output_path)
    return output_path

async def find_direct_bus_with_arrival_time_and_map():
    print("📍 請選擇出發與目的地站牌：\n")
    start_name = input("請輸入出發地站牌名稱：").strip()
    dest_name = input("請輸入目的地站牌名稱：").strip()

    start_options = list_stop_options_by_name(start_name)
    dest_options = list_stop_options_by_name(dest_name)

    if not start_options or not dest_options:
        print("❌ 找不到相關站牌資料。")
        return

    print(f"\n找到以下出發地站牌ID：{[opt['站牌ID'] for opt in start_options]}")
    print(f"\n找到以下目的地站牌ID：{[opt['站牌ID'] for opt in dest_options]}")

    print("\n正在查詢公車路線...")
    routes_start = set()
    for start_id in [opt["站牌ID"] for opt in start_options]:
        routes_start.update(await fetch_bus_routes(start_id))

    routes_dest = set()
    for dest_id in [opt["站牌ID"] for opt in dest_options]:
        routes_dest.update(await fetch_bus_routes(dest_id))

    common_routes = routes_start.intersection(routes_dest)
    route_map = load_route_mapping(ROUTE_MAP_CSV)

    if not common_routes:
        print("\n❌ 無公車可直達兩站。")
        return

    print("\n✅ 以下公車可直達兩站：")
    for route_name in sorted(common_routes):
        route_code = route_map.get(route_name, None)
        if not route_code or not route_code.isdigit():
            print(f"{route_name} → （無法取得有效代碼，無法查詢到站時間）")
            continue

        route_stops = await get_bus_route_stops(route_code)

        valid_direction = None
        for direction in ["去程", "返程"]:
            stops = route_stops.get(direction, [])
            try:
                idx_start = next(i for i, stop in enumerate(stops) if stop["站牌名稱"] == start_name)
                idx_dest = next(i for i, stop in enumerate(stops) if stop["站牌名稱"] == dest_name)
                if idx_start < idx_dest:
                    if all(stop.get("到站時間", "") in ("", "無資料") for stop in stops):
                        continue
                    valid_direction = direction
                    break
            except StopIteration:
                continue

        if not valid_direction:
            print(f"{route_name}（代碼 {route_code}）→ 無法找到先到出發地再到目的地且有即時資料的方向，跳過此路線。")
            continue

        filtered_stops = route_stops[valid_direction]

        print(f"{route_name}（代碼 {route_code}）→ {valid_direction} 各站即將到站時間：")
        for stop in filtered_stops:
            arrival = stop.get("到站時間", "無資料")
            print(f"  {stop['順序']}. {stop['站牌名稱']} → {arrival}")

        print(f"🗺️ 正在繪製路線圖 {route_name} ...")
        map_file = os.path.join(os.path.expanduser("~"), "Desktop", f"直達公車_{route_name}_{valid_direction}_區段圖.html")
        plot_combined_segment_map(route_code, {valid_direction: filtered_stops}, start_name, dest_name, map_file)
        print(f"✅ 地圖已儲存至：{map_file}")

if __name__ == "__main__":
    asyncio.run(find_direct_bus_with_arrival_time_and_map())
