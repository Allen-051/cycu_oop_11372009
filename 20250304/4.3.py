def absolute_value_wrong(x):
    if x < 0:
        return -x
    if x >= 0:
        return x
    
n = int(input('enter a number:'))
print(f'Absolute value is {absolute_value_wrong(n)}\n')

###########################################################
def is_divisible(x, y):
    if x % y == 0:
        print(f'{x} and {y} are divisible.')
        return True
    else:
        print(f'{x} and {y} are not divisible.')
        
    
a = int(input('enter a numer:'))
b = int(input('enter another numer:'))

is_divisible(a, b)