import streamlit as st
import pandas as pd
import math
import folium
from streamlit_folium import st_folium
from folium import Map
import os
from tempfile import NamedTemporaryFile

# 載入資料
df = pd.read_csv(r"C:\Users\CYCU\Desktop\cycu_oop_11372009\final\0527\bus_stops_with_lat_lon.csv")

# 計算兩點之間的距離（Haversine公式）
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = phi2 - phi1
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c * 1000

# 查詢是否有直達車
def find_direct_route(start_name, end_name):
    routes = df[df["站名"].isin([start_name, end_name])].groupby("路線代碼").filter(lambda g: g["站名"].nunique() == 2)
    return routes["路線代碼"].unique()

# 計算距離與時間
def calculate_distance_and_time(segment):
    total_distance = 0
    for i in range(len(segment)-1):
        total_distance += haversine(segment.iloc[i]["緯度"], segment.iloc[i]["經度"],
                                    segment.iloc[i+1]["緯度"], segment.iloc[i+1]["經度"])
    time_min = round((total_distance / 1000) / 8 * 60, 1)
    return total_distance, time_min

# Streamlit 主頁面
st.title("台北市公車路線查詢")

start_name = st.selectbox("選擇起始站", sorted(df["站名"].unique()))
end_name = st.selectbox("選擇終點站", sorted(df["站名"].unique()))

if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = pd.Timestamp.now()
if "bus_map_html" not in st.session_state:
    st.session_state["bus_map_html"] = None
if "bus_info" not in st.session_state:
    st.session_state["bus_info"] = ""

query_button = st.button("查詢路線")
refresh_button = st.button("重新查詢路線（強制刷新）")
current_time = pd.Timestamp.now()
elapsed_time = (current_time - st.session_state["last_refresh"]).total_seconds()

if query_button or refresh_button or elapsed_time > 120:
    direct_routes = find_direct_route(start_name, end_name)
    if len(direct_routes) > 0:
        route_id = direct_routes[0]
        route_df = df[df["路線代碼"] == route_id].copy().reset_index(drop=True)
        route_df["順序"] = route_df.groupby("方向").cumcount() + 1
        direction = route_df[route_df["站名"] == start_name]["方向"].values[0]
        sub_df = route_df[route_df["方向"] == direction].reset_index(drop=True)

        idx_start = sub_df[sub_df["站名"] == start_name].index[0]
        idx_end = sub_df[sub_df["站名"] == end_name].index[0]

        # 修正方向順序
        if idx_start > idx_end:
            segment = sub_df.iloc[idx_end:idx_start+1].copy().iloc[::-1].reset_index(drop=True)
        else:
            segment = sub_df.iloc[idx_start:idx_end+1].copy().reset_index(drop=True)

        total_distance, time_min = calculate_distance_and_time(segment)

        m = folium.Map(location=[segment.iloc[0]["緯度"], segment.iloc[0]["經度"]], zoom_start=14)
        folium.PolyLine(
            locations=segment[["緯度", "經度"]].values.tolist(),
            color="blue", weight=5, opacity=0.8
        ).add_to(m)

        for idx, row in segment.iterrows():
            popup = folium.Popup(row["站名"], parse_html=True)
            if row["站名"] == start_name:
                folium.Marker(
                    location=[row["緯度"], row["經度"]],
                    popup=popup,
                    icon=folium.DivIcon(html=f"""
                        <div style='background:green; color:white; font-size:14pt;
                                    border-radius:50%; width:40px; height:40px;
                                    text-align:center; line-height:40px;'>GO</div>
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
                        <div style='font-size:12pt; background:orange; color:white;
                                    border-radius:50%; width:24px; height:24px;
                                    text-align:center; line-height:24px;'>
                            {idx + 1}
                        </div>
                    """)
                ).add_to(m)

        with NamedTemporaryFile(mode="w", suffix=".html", delete=False) as tmpfile:
            m.save(tmpfile.name)
            tmpfile.flush()
            st.session_state["bus_map_html"] = tmpfile.name

        st.session_state["bus_info"] = f"從「{start_name}」到「{end_name}」共 {len(segment)-1} 站，約 {round(total_distance)} 公尺，預估 {time_min} 分鐘"
        st.session_state["last_refresh"] = pd.Timestamp.now()

# 顯示地圖與資訊（只有在有 map 時顯示）
if st.session_state["bus_map_html"] is not None:
    with open(st.session_state["bus_map_html"], "r", encoding="utf-8") as f:
        folium_html = f.read()
        st.components.v1.html(folium_html, height=600)
        st.info(st.session_state["bus_info"])
        st.caption(f"地圖最後更新時間：{st.session_state['last_refresh'].strftime('%H:%M:%S')}")
