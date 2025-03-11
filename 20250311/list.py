# 星期幾的list
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
# 月份的list
month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
# 十二生肖的list
zodiac = ['Rat', 'Ox', 'Tiger', 'Rabbit', 'Dragon', 'Snake', 'Horse', 'Goat', 'Monkey', 'Rooster', 'Dog', 'Pig']

ask_year = input('Please input a month:')
print('The month you input is:', month[int(ask_year)-1])
ask_day = input('Please input a day:')
print('The day you input is:', weekdays[int(ask_day)-1])



