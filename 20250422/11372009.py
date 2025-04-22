import asyncio
import os
import bus_info_11372009  # 匯入用來讀取巴士資訊並輸出 CSV 的模組
import bus_info_matplotlib  # 匯入用來處理公車座標並繪製圖的模組
import bus_info_geojson  # 匯入用來將公車路線資訊儲存成 HTML 的模組

if __name__ == "__main__":
    # 使用者輸入公車代碼
    route_id = input("請輸入公車代碼：").strip()

    # 使用者輸入檔案儲存路徑
    save_path = input("請輸入檔案儲存的資料夾路徑：").strip()

    # 呼叫 bus_info_11372009 模組的函數，抓取公車資訊並輸出 CSV 和 GeoJSON
    geojson_file = asyncio.run(bus_info_11372009.find_bus(route_id))

    if geojson_file:
        # 繪製公車路線圖
        output_image = os.path.join(save_path, f"bus_route_{route_id}.png")
        bus_info_matplotlib.plot_bus_stops(geojson_file, output_image)

        # 顯示圖片
        bus_info_matplotlib.show_image(output_image)

        # 使用 bus_info_geojson 模組將公車路線資訊儲存成 HTML
        output_html = os.path.join(save_path, f"bus_route_{route_id}.html")
        bus_info_geojson.leafjet_plot_bus(geojson_file, output_html)

        print(f"公車路線的互動式地圖已儲存至 {output_html}")