import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

def plot_normal_pdf():
    # 詢問使用者輸入 mu 和 sigma
    try:
        mu = float(input("請輸入平均值 mu: "))
        sigma = float(input("請輸入標準差 sigma: "))
        if sigma <= 0:
            raise ValueError("標準差 sigma 必須大於 0")
    except ValueError as e:
        print(f"輸入錯誤: {e}")
        return

    # 定義 x 範圍
    x = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 1000)
    # 計算 PDF
    pdf = norm.pdf(x, mu, sigma)

    # 繪製圖形
    plt.figure(figsize=(8, 6))
    plt.plot(x, pdf, label=f'N({mu}, {sigma}^2)', color='blue')
    plt.title('Normal Distribution PDF')
    plt.xlabel('x')
    plt.ylabel('Probability Density')
    plt.legend()
    plt.grid()

    # 儲存圖片到桌面
    output_path = r'c:\Users\CYCU\Desktop\normal_pdf.jpg'
    plt.savefig(output_path)
    print(f"圖片已儲存至 {output_path}")

    # 顯示圖形
    plt.show()

# 呼叫函數
plot_normal_pdf()