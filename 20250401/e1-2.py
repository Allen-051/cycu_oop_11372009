import requests
import html
import pandas as pd
from bs4 import BeautifulSoup

def get_stop_info(stop_link:str) -> dict:

    url = f'https://pda5284.gov.taipei/MQS/{stop_link}'
    # get url and save to html file 
    # the html file is saved files as bus_{stop_link}.html
    response = requests.get(url)
    if response.status_code == 200:

        # read id from url
        stop_id = stop_link.split("=")[1]

        with open(f"bus_stop_{stop_id}.html", "w", encoding="utf-8") as file:
            file.write(response.text)

        #print(f"網頁已成功下載並儲存為 bus_{stop_link}.html")
    else:
        #print(f"無法下載網頁，HTTP 狀態碼: {response.status_code}") 
        pass


def get_bus_route(rid):
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
        print("去程(往松山車站):")
        print(df1)
        print("\n返程(往蘆洲):")
        print(df2)
    except ValueError as e:
        print(f"Error: {e}")