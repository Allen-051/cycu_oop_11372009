import turtle

# 設置螢幕
screen = turtle.Screen()
screen.setup(200, 200)  # 設定畫布大小

# 創建海龜
t = turtle.Turtle()

# 繪製正方形
for _ in range(4):
    t.forward(25)  # 移動 25 單位
    t.left(90)      # 左轉 90 度

# 等待使用者關閉視窗
turtle.done()