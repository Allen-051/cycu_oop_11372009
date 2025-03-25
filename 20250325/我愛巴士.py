from bs4 import BeautifulSoup
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 讀取 HTML 檔案
def read_html_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# 查找車站資訊並提取對應數據
def search_station(html_content, station_name):
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 遍歷所有 <tr> 標籤，尋找包含車站名稱的行
    for row in soup.find_all("tr"):
        if station_name in row.get_text():
            # 找到車站名稱所在的 <td>
            for cell in row.find_all("td"):
                if station_name in cell.get_text(strip=True):
                    next_td = cell.find_next_sibling("td")  # 找到下一個 <td>
                    if next_td:
                        return next_td.get_text(strip=True)  # 取出內容
            break  # 找到第一個匹配的行後停止搜尋
    
    return None

if __name__ == "__main__":
    file_path = input("請輸入 HTML 檔案路徑: ")
    html_content = read_html_file(file_path)
    
    station_name = input("請輸入要查詢的車站名稱: ")
    result = search_station(html_content, station_name)
    
    if result:
        print("找到對應資訊:", result)
    else:
        print("未找到相關車站資訊。")