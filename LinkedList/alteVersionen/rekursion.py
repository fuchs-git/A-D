def fakultaet(x):
    if x == 0:
        return 1
    else:
        return x * fakultaet(x -1)

print(fakultaet(15))

def fib(n):
    global counter
    counter +=1
    if n == 1:
        return 1
    elif n ==2:
        return 1
    else:
        return fib(n-1) + fib(n-2)

counter = 0
print(fib(45))
print(counter)