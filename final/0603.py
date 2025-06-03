import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import pandas as pd
import os

async def find_bus(route_id: str) -> pd.DataFrame:
    """根據公車代碼(route_id)爬取站牌資訊（去程+返程），回傳 DataFrame。"""
    route_id = route_id.strip()
    url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        try:
            await page.wait_for_selector("div#GoDirectionRoute li, div#BackDirectionRoute li", timeout=10000)
        except:
            print("網頁載入超時，請確認公車代碼是否正確。")
            return pd.DataFrame()

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # 擷取去程與返程
    all_data = []
    for direction_label, selector in [("去程", "div#GoDirectionRoute li"), ("返程", "div#BackDirectionRoute li")]:
        station_items = soup.select(selector)
        if not station_items:
            continue
        for idx, li in enumerate(station_items, start=1):
            try:
                spans = li.select("span.auto-list-stationlist span")
                inputs = li.select("input")

                stop_time = spans[0].get_text(strip=True)
                stop_number = spans[1].get_text(strip=True)
                stop_name = spans[2].get_text(strip=True)

                stop_id = inputs[0]['value']
                latitude = inputs[1]['value']
                longitude = inputs[2]['value']

                all_data.append({
                    "方向": direction_label,
                    "順序": idx,
                    "到站時間": stop_time,
                    "站牌編號": stop_number,
                    "站牌名稱": stop_name,
                    "站牌ID": stop_id,
                    "緯度": latitude,
                    "經度": longitude
                })

            except Exception as e:
                print(f"{direction_label} 第 {idx} 筆資料處理錯誤：{e}")

    df = pd.DataFrame(all_data)

    if df.empty:
        print("沒有成功抓取到任何站牌資訊。")
        return df

    # 儲存到桌面
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_file = os.path.join(desktop_path, f"bus_information_{route_id}.csv")
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"\n抓到的站牌資訊（去程+返程）已儲存至：{output_file}")
    print("\n資料預覽：")
    print(df)

    return df

# 主程式
if __name__ == "__main__":
    route_id = input("請告訴我公車代碼：").strip()
    asyncio.run(find_bus(route_id))
