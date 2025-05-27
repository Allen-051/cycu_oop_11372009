import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 讀取 CSV 檔案
file_path = '20250520/example/midterm_scores.csv'
df = pd.read_csv(file_path)

# 設定分數組距
bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
labels = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90-100']

# 需要繪製的科目
subjects = ['Chinese', 'English', 'Math', 'History', 'Geography', 'Physics', 'Chemistry']
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']  # 彩虹顏色順序

# 計算每個分數組距的學生數量
hist_data = {}
for subject in subjects:
    hist_data[subject] = pd.cut(df[subject], bins=bins, labels=labels).value_counts().sort_index()

# 繪製柱狀圖
x = np.arange(len(labels))  # X 軸位置
width = 0.1  # 每個柱狀圖的寬度

fig, ax = plt.subplots(figsize=(14, 8))

# 為每個科目繪製柱狀圖，並加上黑色邊框
for i, subject in enumerate(subjects):
    ax.bar(
        x + i * width, 
        hist_data[subject], 
        width, 
        label=subject, 
        color=colors[i], 
        edgecolor='black'  # 加上黑色邊框
    )

# 設定圖表標籤和標題
ax.set_xlabel('Score Range')
ax.set_ylabel('Number of Students')
ax.set_title('Distribution of Scores by Subject')
ax.set_xticks(x + width * (len(subjects) - 1) / 2)
ax.set_xticklabels(labels)
ax.legend(title='Subjects')

# 儲存圖形為 JPG 檔案
output_file_path = '20250520/example/score_distribution_all_subjects.jpg'
plt.savefig(output_file_path, format='jpg')
plt.show()

print(f"Bar chart with all subjects has been saved to {output_file_path}")