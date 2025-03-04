def is_divisible(x, y):
    if x % y == 0:
        return True
    else:
        return False
    
a = input('enter a numer:')
b = input('enter another numer:')

print(f'the result of {a} and {b} {is_divisible(a, b)}')
