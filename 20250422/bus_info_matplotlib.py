import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

def plot_bus_stops(geojson_file: str, output_image: str):
    
    try:
        # 讀取 GeoJSON 檔案為 GeoDataFrame
        gdf = gpd.read_file(geojson_file)
        
        # 檢查是否有幾何資料
        if gdf.empty or gdf.geometry.is_empty.all():
            print("GeoJSON 檔案中沒有幾何資料。")
            return
        
        # 繪製站點
        fig, ax = plt.subplots(figsize=(10, 10))
        gdf.plot(ax=ax, color='blue', markersize=10, alpha=0.7)
        
        # 設定圖表標題與軸標籤
        ax.set_title("Bus Stops", fontsize=16)
        ax.set_xlabel("Longitude", fontsize=12)
        ax.set_ylabel("Latitude", fontsize=12)
        
        # 儲存圖片
        plt.savefig(output_image, dpi=300)
        plt.close()
        print(f"站點圖已儲存至 {output_image}")
    
    except Exception as e:
        print(f"發生錯誤：{e}")

def show_image(image_path: str):
    """
    顯示圖片
    """
    try:
        img = mpimg.imread(image_path)
        plt.imshow(img)
        plt.axis('off')  # 隱藏軸
        plt.show()
    except Exception as e:
        print(f"無法顯示圖片：{e}")

if __name__ == "__main__":
    # 輸入 GeoJSON 檔案路徑
    geojson_file = input("請輸入 GeoJSON 檔案路徑：").strip()
    
    # 輸入輸出圖片的資料夾路徑
    output_dir = input("請輸入輸出圖片的資料夾路徑：").strip()
    
    # 將圖片檔名固定為 bus_stops.png
    output_image = os.path.join(output_dir, "bus_stops.png")
    
    # 繪製並儲存圖片
    plot_bus_stops(geojson_file, output_image)
    
    # 顯示圖片
    show_image(output_image)