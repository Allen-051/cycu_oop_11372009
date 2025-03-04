from turtle import *
color('blue', 'white')
begin_fill()
while True:
    forward(500)
    left(100)
    if abs(pos()) < 1:
        break
end_fill()
done()