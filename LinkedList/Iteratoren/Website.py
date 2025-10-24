quadrate = [1, 4, 9, 16, 25]

mein_iterator = iter(quadrate)  # iter erzeugt aus dem Iterable einen Iterator

print(next(mein_iterator))      # next holt ein Element aus dem Iterator
print(next(mein_iterator))
print(next(mein_iterator))
print(next(mein_iterator))
print(next(mein_iterator))
# print(next(mein_iterator))  #  das geht schief, der Iterator ist "erschöpft"

i = iter(quadrate)
try:
    while True:
        print(next(i))
except StopIteration:
    pass

