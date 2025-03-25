import pandas as pd
import matplotlib.pyplot as plt

def read_and_plot_csv(file_path):
    # 讀取 CSV 檔案，跳過第一列資料
    df = pd.read_csv(file_path, skiprows=1, header=None, encoding='utf-8')
    
    # 假設第一行為日期，第四行為 y1，十四行為 y2
    x = pd.to_datetime(df.iloc[:, 0], format='%Y%m%d')  # 將日期轉換為 datetime 格式
    y1 = df.iloc[:, 3]  # 第四行數列
    y2 = df.iloc[:, 13]  # 第十四行數列

    # 按日期排序
    sorted_indices = x.argsort()
    x = x.iloc[sorted_indices]
    y1 = y1.iloc[sorted_indices]
    y2 = y2.iloc[sorted_indices]

    # 繪製圖表
    plt.figure(figsize=(10, 6))
    plt.plot(x, y1, color ='red',label='buy in')
    plt.plot(x, y2, color ='blue',label='sold out')
    plt.xlabel('date')
    plt.ylabel('NTD to USD Exchange Rate')
    plt.title('Bank of Taiwan Exchange Rate')
    plt.ylim(31.6, 33.6)  # 設定 y 軸範圍
    plt.legend()
    plt.xticks(rotation=60)  # 日期旋轉以便顯示
    plt.tight_layout()
    plt.show()

# 使用範例
file_path = 'C:\\Users\\User\\Desktop\\cycu_oop_11372009\\ExchangeRate@202503251849.csv'
read_and_plot_csv(file_path)