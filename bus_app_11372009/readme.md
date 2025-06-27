# 台北市公車動態查詢系統

本公車爬蟲程式碼由中原大學土木工程系 OOP 第二組製作
組員:
土木碩一 11372004周芷琦
土木碩一 11372009邱昱倫
土木碩一 11372011涂子彧
土木碩一 11372013羅于翔

主要功能：提供台北市公車直達與轉乘路線查詢，支援 Folium 地圖顯示與即時到站預測。

---

## 📦 安裝方式

1. 請先安裝 Python 3.9 以上版本。
2. 於終端機進入本專案資料夾（`bus_app_11372009`），執行：

    ```bash
    pip install .
    ```

    或直接安裝已打包的檔案：

    ```bash
    pip install bus_app_11372009-0.1.0.tar.gz
    ```

---

## 🚀 如何啟動 Streamlit 公車查詢介面

請勿直接執行 `cycu11372009_bus_info.py`，而是於終端機輸入：

```bash
streamlit run bus_app_11372009/final_bus_info/cycu11372009_bus_info.py
```

---

## 🛠️ 如何在程式中 import 主要功能

安裝本 package 後，可於 Python 程式中 import 主要模組：

```python
from final_bus_info import cycu11372009_bus_info
# 或
from final_bus_info.cycu11372009_bus_info import <function_name>
```

---

## 📁 專案結構說明

- `final_bus_info/cycu11372009_bus_info.py`：Streamlit 主程式，含查詢、地圖、即時到站等功能
- `final_bus_info/bus_stops_with_lat_lon.csv`：公車站點資料
- `final_bus_info/__init__.py`：package 初始化
- `pyproject.toml`：套件安裝與依賴設定
- `MANIFEST.in`：資料檔案打包設定
- `LICENSE`：授權條款
- `readme.md`：本說明文件

---

## 🔗 相關連結

- [原始碼 Github](https://github.com/Allen-051/cycu_oop_11372009)

---

## ❓ 常見問題

- 若遇到套件安裝問題，請確認 Python 版本與 pip 已更新。
- 若遇到地圖或即時資訊無法顯示，請檢查網路連線或稍後再試。

---

如有其他問題，歡迎聯絡作者。
