import random
import time

def bubble_sort(liste):
    n = len(liste)
    swapped = True
    while swapped:
        swapped = False
        for i in range(n-1):
            if liste[i] > liste[i+1]:
                liste[i], liste[i+1] = liste[i+1], liste[i]
                swapped = True

def quicksort(l: list) -> list:
    if len(l) <= 1: return l  # Abbruch, wenn kürzer als 2 (dann ist das nämlich schon sortiert)
    pivot = l[0]  # willkürlich das Erste Element als Pivot
    left, right = [], []  # zunächst leere Teillisten
    for e in l[1:]:  # Liste in Teillisten aufspalten, Pivot dabei weglassen
        if e < pivot:
            left.append(e)
        else:
            right.append(e)
    left, right = quicksort(left), quicksort(right)  # Teillisten rekursiv sortieren
    return left + [pivot] + right  # die sortierten Teillisten und das Pivot-Element zusammen als Lösung ausgeben

n = 50_000
list_basis = [random.randint(1,n) for x in range(n)]
print(list_basis)
l1 = list_basis.copy()
l2 = list_basis.copy()


start =time.time()
bubble_sort(l1)
print(f'Bubblesort {time.time()-start}')

start =time.time()
l2 = quicksort(l2)
print(f'Quicksort {time.time()-start}')