def bubble_sort(liste):
    n = len(liste)
    swapped = True
    while swapped:
        swapped = False
        for i in range(n-1):
            if liste[i] > liste[i+1]:
                liste[i], liste[i+1] = liste[i+1], liste[i]
                swapped = True



liste = [6, 5, 3, 1, 8, 7, 2, 4]
print(liste)
bubble_sort(liste)
print(liste)