from bs4 import BeautifulSoup
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def read_html_and_query_station(file_path):
    """
    讀取 HTML 檔案，根據使用者輸入的車站名稱回傳指定範圍的字元。
    
    :param file_path: str, HTML 檔案的路徑
    """
    # 讀取 HTML 檔案
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    # 詢問使用者要觀測的車站
    station_name = input("請輸入要觀測的車站名稱：")
    
    # 查找對應車站的候車資訊
    station_elements = soup.find_all(id=lambda x: x and x.startswith("tte"))
    for element in station_elements:
        if station_name in element.text:
            # 找到車站後，計算從車站名稱起算的第 51 到第 53 個字元
            text = element.text.strip()
            start_index = text.find(station_name)
            if start_index != -1:
                target_text = text[start_index + 50:start_index + 53]
                print(f"車站：{station_name}，第 51 到第 53 個字元為：{target_text}")
                return
    
    # 如果找不到車站
    print(f"找不到車站：{station_name} 的候車資訊。")

# 主程式
file_path = 'C:\\Users\\User\\Desktop\\cycu_oop_11372009\\20250325\\[忠孝幹線(公車雙向轉乘優惠)]公車動態資訊.html'
read_html_and_query_station(file_path)
