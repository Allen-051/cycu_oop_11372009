from bs4 import BeautifulSoup
import csv
import os

# 抓出所有ebus網站上公車路線所對應的id(數字)
def extract_bus_routes_from_html(html_path, output_csv_path=None):
    # 開啟 HTML 檔案
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # 抓取所有公車項目
    bus_data = []
    links = soup.find_all("a", href=True)

    for a in links:
        href = a["href"]
        if href.startswith("javascript:go("):
            # 擷取代碼與公車名稱
            try:
                bus_id = href.split("'")[1]
                bus_name = a.get_text(strip=True)
                if bus_name:
                    bus_data.append([bus_name, bus_id])
            except IndexError:
                continue

    # 若未指定輸出檔案，預設儲存在桌面
    if not output_csv_path:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        output_csv_path = os.path.join(desktop, "taipei_bus_routes.csv")

    # 儲存為 CSV
    with open(output_csv_path, mode="w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["路線名稱", "公車代碼"])
        writer.writerows(bus_data)

    print(f"共擷取 {len(bus_data)} 筆資料，已儲存至：{output_csv_path}")

# 呼叫主函數（請確認 HTML 路徑正確）
html_path = r"C:\Users\CYCU\Desktop\cycu_oop_11372009\final\ebus_taipei\大臺北公車.html"
extract_bus_routes_from_html(html_path)
