import pandas as pd
import matplotlib.pyplot as plt

# 讀取Excel檔案
file_path = 'C:\\Users\\User\\Desktop\\cycu_oop_11372009\\311_test.xlsx'

df = pd.read_excel(file_path)

# 假設第一欄為x，第二欄為y
x = df.iloc[:, 0]
y = df.iloc[:, 1]

# 計算x + y並儲存到第三欄
df['x + y'] = x + y

# 儲存檔案到桌面
output_path = 'C:\\Users\\User\\Desktop\\cycu_oop_11372009\\output.xlsx'
df.to_excel(output_path, index=False)

# 繪製散佈圖
plt.scatter(x, y)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('X vs Y Scatter Plot')
plt.show()