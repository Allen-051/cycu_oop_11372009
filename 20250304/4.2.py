def gcd(a, b):
    if b == 0:
        return a
    else:
        return gcd(b, a % b)
    
x = 11
y = 121
print(f'GCD of {x} and {y} is {gcd(x, y)}.')
x = 7
y = 49
print(f'GCD of {x} and {y} is {gcd(x, y)}.')