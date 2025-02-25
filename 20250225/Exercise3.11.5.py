
def print_right(string):
    str_len = len(string)
    space = 40 - str_len
    result = ' ' * space + string
    print(result)

print_right("Monty")
print_right("Python's")
print_right("Flying Circus")