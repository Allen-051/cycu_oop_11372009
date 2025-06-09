import pandas as pd
import os

def main():
    # 讀取 all_bus_stop_by_route.csv
    all_stop_path = input("請輸入 all_bus_stop_by_route.csv 路徑: ").strip()
    if all_stop_path == "":
        all_stop_path = "all_bus_stop_by_route.csv"
    # 讀取 bus_stop_with_lat_lon.csv
    latlon_path = input("請輸入 bus_stop_with_lat_lon.csv 路徑: ").strip()
    if latlon_path == "":
        latlon_path = "bus_stop_with_lat_lon.csv"
    # 讀取csv
    df_all = pd.read_csv(all_stop_path)
    df_latlon = pd.read_csv(latlon_path)
    # 合併
    df_merged = pd.merge(
        df_all,
        df_latlon[["方向", "站牌名稱", "站牌ID", "緯度", "經度"]],
        on=["方向", "站牌名稱", "站牌ID"],
        how="left"
    )
    # 輸出路徑
    save_path = input("請輸入結果儲存資料夾路徑（直接Enter則預設桌面）: ").strip()
    if save_path == "":
        save_path = os.path.join(os.path.expanduser("~"), "Desktop")
        print(f"未輸入路徑，預設儲存於：{save_path}")
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    output_file = os.path.join(save_path, "all_bus_stop_info.csv")
    df_merged.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"已儲存至：{output_file}")

if __name__ == "__main__":
    main()
