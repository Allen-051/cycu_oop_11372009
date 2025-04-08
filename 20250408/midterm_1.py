import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import lognorm
0.4
def plot_lognormal_cdf():
    # 詢問使用者輸入平均數和標準差
    mu = float(input("請輸入平均數 μ: "))
    sigma = float(input("請輸入標準差 σ: "))

    # 設定 x 軸範圍
    x = np.linspace(0.01, 10, 1000)

    # 計算對數常態累積分布函數
    cdf = lognorm.cdf(x, s=sigma, scale=np.exp(mu))

    # 繪製圖形
    plt.figure(figsize=(8, 6))
    plt.plot(x, cdf, label=f'Lognormal CDF (μ={mu}, σ={sigma})', color='blue')
    plt.title('Lognormal Cumulative Distribution Function')
    plt.xlabel('x')
    plt.ylabel('CDF')
    plt.legend()
    plt.grid()
    plt.show()

    # 儲存為 JPG 檔案
    output_filename = 'lognormal_cdf.jpg'
    plt.savefig(output_filename, format='jpg')
    plt.close()

    print(f"圖形已儲存為 {output_filename}")

# 呼叫函數
plot_lognormal_cdf()