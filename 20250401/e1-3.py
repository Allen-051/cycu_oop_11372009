from requests_html import HTMLSession
import requests
import html
import pandas as pd
from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright

def get_stop_info(stop_link: str) -> dict:
    stop_id = stop_link.split("=")[1]
    url = f'https://pda5284.gov.taipei/MQS/stoplocation.jsp?slid={stop_id}'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 關閉無頭模式
        page = browser.new_page()
        page.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        page.goto(url)
        page.wait_for_load_state("networkidle")  # 等待網頁完全加載
        page.wait_for_selector("table.formattable1")  # 等待目標表格出現
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # 滾動到頁面底部
        content = page.content()
        with open(f"bus_stop_{stop_id}.html", "w", encoding="utf-8") as file:
            file.write(content)
        browser.close()

    return {"stop_id": stop_id, "html_file": f"bus_stop_{stop_id}.html"}


def get_bus_route(rid):
    """
    Retrieve two DataFrames containing bus stop names and their corresponding URLs based on the route ID (rid).

    Args:
        rid (str): Bus route ID.

    Returns:
        tuple: Two Pandas DataFrames, each corresponding to one direction of the bus route.

    Raises:
        ValueError: If the webpage cannot be downloaded or if insufficient table data is found.
    """
    url = f'https://pda5284.gov.taipei/MQS/route.jsp?rid={rid}'

    # Send GET request
    response = requests.get(url)
    # write the response to a file route_{rid}.html
    with open(f"bus_route_{rid}.html", "w", encoding="utf-8") as file:
        file.write(response.text)

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
            # Find all tr tags with the specified classes
            # find all go1 and go2
            trs = table.find_all("tr", class_=["ttego1", "ttego2"])
            if trs:
                rows = []               
                for tr in trs:
                    # Extract stop name and link
                    td = tr.find("td")
                    if td:
                        stop_name = html.unescape(td.text.strip())
                        stop_link = td.find("a")["href"] if td.find("a") else None
                        rows.append({"stop_name": stop_name, "stop_link": stop_link})
                if rows:
                    df = pd.DataFrame(rows)
                    dataframes.append(df)                

            # find all back1 and back2
            trs = table.find_all("tr", class_=["tteback1", "tteback2"])
            if trs:
                rows = []               
                for tr in trs:
                    # Extract stop name and link
                    td = tr.find("td")
                    if td:
                        stop_name = html.unescape(td.text.strip())
                        stop_link = td.find("a")["href"] if td.find("a") else None
                        rows.append({"stop_name": stop_name, "stop_link": stop_link})
                if rows:
                    df = pd.DataFrame(rows)
                    dataframes.append(df)

        # Return two DataFrames
        if len(dataframes) >= 6:

            go_dataframe = dataframes[0]
            back_dataframe = dataframes[3]

            for index, row in go_dataframe.iterrows():
                stop_link = row['stop_link']
                if stop_link:
                    get_stop_info(stop_link)
                    #print(f"get stop info from {stop_link}")

            for index, row in back_dataframe.iterrows():
                stop_link = row['stop_link']
                if stop_link:
                    get_stop_info(stop_link)
                    #print(f"get stop info from {stop_link}")


            return go_dataframe, back_dataframe
        else:
            print('length of dataframes:', len(dataframes))
            raise ValueError("Insufficient table data found.")
    else:
        raise ValueError(f"Failed to download webpage. HTTP status code: {response.status_code}")

# Test function
if __name__ == "__main__":
    rid = "10417"  # Test route ID
    try:
        df1, df2 = get_bus_route(rid)
        print("First DataFrame:")
        print(df1)
        print("\nSecond DataFrame:")
        print(df2)
    except ValueError as e:
        print(f"Error: {e}")