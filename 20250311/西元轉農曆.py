from lunarcalendar import Converter, Solar, Lunar

# 十二生肖的list
zodiac = ['Rat', 'Ox', 'Tiger', 'Rabbit', 'Dragon', 'Snake', 'Horse', 'Goat', 'Monkey', 'Rooster', 'Dog', 'Pig']

# 輸入西元年、月、日
year = int(input('Please input a year (e.g., 2025): '))
month = int(input('Please input a month (1-12): '))
day = int(input('Please input a day (1-31): '))

# 建立Solar物件
solar_date = Solar(year, month, day)

# 將Solar日期轉換為Lunar日期
lunar_date = Converter.Solar2Lunar(solar_date)

# 取得農曆年份的生肖
zodiac_year = zodiac[(lunar_date.year - 4) % 12]

# 輸出結果
print(f'The lunar date is: Year {lunar_date.year}, Month {lunar_date.month}, Day {lunar_date.day}')
print(f'The zodiac sign for the lunar year {lunar_date.year} is: {zodiac_year}')