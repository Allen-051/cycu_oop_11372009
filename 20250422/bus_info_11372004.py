import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import csv
import os
import pandas as pd
import bus_info_11372009  # 匯入 bus_info_11372009 模組

# 執行主程式
if __name__ == "__main__":
    route_id = input("請告訴我公車代碼：").strip()  # 在主程式中取得 route_id
    asyncio.run(bus_info_11372009.find_bus(route_id))  # 使用模組名稱呼叫 find_bus 函數