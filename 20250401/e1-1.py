import requests
import html
import pandas as pd
from bs4 import BeautifulSoup

def get_stop_info(stop_link:str) -> dict:

    url = f'https://pda5284.gov.taipei/MQS/{stop_link}'

    response = requests.get(url)
    if response.status_code == 200:

        # read id from url
        stop_id = stop_link.split("=")[1]

        with open(f"bus_stop_{stop_id}.html", "w", encoding="utf-8") as file:
            file.write(response.text)

        print(f"網頁已成功下載並儲存為 bus_{stop_link}.html")
    else:
        print(f"無法下載網頁，HTTP 狀態碼: {response.status_code}") 


def get_bus_route(rid):

    url = f'https://pda5284.gov.taipei/MQS/route.jsp?rid={rid}'

    # Send GET request
    response = requests.get(url)

    # Ensure the request is successful
    if response.status_code == 200:
        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all tables
        tables = soup.find_all("table")

        # Initialize DataFrame list
        dataframes = []

        # Iterate through tables
        for table in tables:
        # 處理去程資料
            rows_go = []
            for tr in table.find_all("tr", class_=["ttego1", "ttego2"]):
                td = tr.find("td")
                if td:
                    stop_name = html.unescape(td.text.strip())  # 解碼站點名稱
                    stop_link = td.find("a")["href"] if td.find("a") else None
                    rows_go.append({"站點名稱": stop_name, "連結": stop_link})
            if rows_go:
                df_go = pd.DataFrame(rows_go)

            # 處理返程資料
            rows_back = []
            for tr in table.find_all("tr", class_=["tteback1", "tteback2"]):
                td = tr.find("td")
                if td:
                    stop_name = html.unescape(td.text.strip())  # 解碼站點名稱
                    stop_link = td.find("a")["href"] if td.find("a") else None
                    rows_back.append({"站點名稱": stop_name, "連結": stop_link})
            if rows_back:
                df_back = pd.DataFrame(rows_back)

        # 輸出結果
        if df_go is not None:
            print("去程:")
            print(df_go)
        else:
            print("未找到去程資料。")

        if df_back is not None:
            print("\n返程:")
            print(df_back)
        else:
            print("未找到返程資料。")

# Test function
if __name__ == "__main__":
    for rid in range(36021, 36123):  # 從 36021 到 36122
        get_bus_route(rid)
