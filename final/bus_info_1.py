import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def get_bus_route_stops(route_id: str) -> dict:
    base_url = "https://ebus.gov.taipei/Route/StopsOfRoute?routeid="
    url = f"{base_url}{route_id}"

    result = {"去程": [], "返程": []}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        await page.wait_for_selector("div#GoDirectionRoute li", timeout=10000)
        go_html = await page.content()

        # 使用 JavaScript 切換到返程頁籤，避免點擊失效
        # 檢查返程按鈕是否存在
        if not await page.query_selector("a#Return"):
            print("返程按鈕不存在，無法切換到返程頁籤。")
            back_html = None
        else:
            try:
                await page.evaluate("document.querySelector('a#Return').click()")
                await page.wait_for_selector("div#BackDirectionRoute li", timeout=15000)  # 延長等待時間
                back_html = await page.content()
            except Exception as e:
                print(f"切換到返程頁籤時發生錯誤：{e}")
                back_html = None

        await browser.close()

    # 處理去程資料（加上順序編號）
    soup_go = BeautifulSoup(go_html, "html.parser")
    go_items = soup_go.select("div#GoDirectionRoute li")
    for idx, li in enumerate(go_items, start=1):
        spans = li.select("span.auto-list-stationlist span")
        inputs = li.select("input")
        if len(spans) >= 3 and len(inputs) >= 3:
            result["去程"].append({
                "順序": idx,
                "站名": spans[2].get_text(strip=True),
                "站牌ID": inputs[0]['value'],
                "lat": float(inputs[1]['value']),
                "lon": float(inputs[2]['value'])
            })

    # 處理返程資料（加上順序編號）
    if back_html:
        soup_back = BeautifulSoup(back_html, "html.parser")
        back_items = soup_back.select("div#BackDirectionRoute li")
        for idx, li in enumerate(back_items, start=1):
            spans = li.select("span.auto-list-stationlist span")
            inputs = li.select("input")
            if len(spans) >= 3 and len(inputs) >= 3:
                result["返程"].append({
                    "順序": idx,
                    "站名": spans[2].get_text(strip=True),
                    "站牌ID": inputs[0]['value'],
                    "lat": float(inputs[1]['value']),
                    "lon": float(inputs[2]['value'])
                })

    # 除錯：輸出返程 HTML 內容
    if back_html:
        print("成功抓取返程資料。")
    else:
        print("未能抓取返程資料，請檢查公車代碼或網站結構。")

    return result

# 測試用例
if __name__ == "__main__":
    async def test():
        route_info = await get_bus_route_stops("0100002200")  # 22路公車
        for direction, stops in route_info.items():
            print(f"\n--- {direction} ---")
            for stop in stops:
                # 輸出格式：順序, 站名, 站牌ID, 緯度, 經度
                print(",".join(map(str, stop.values())))

    asyncio.run(test())
