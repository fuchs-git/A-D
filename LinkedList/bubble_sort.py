import random
import time

def bubble_sort(liste, demo = False):
    n = len(liste)
    swapped = True
    while swapped:                                              # wurde im letzten Durchlauf getauscht?
        swapped = False
        for i in range(1,n):
            if liste[i - 1] > liste[i]:                         # größeres vor kleinerem?
                liste[i - 1], liste[i] = liste[i], liste[i - 1] # tauschen
                swapped = True                                  # merken, dass es in diesem Durchlauf Änderungen gab

def bubble_sort_optimiert(liste, demo = False):
    n = len(liste)
    swapped = True
    while swapped:                                              # wurde im letzten Durchlauf getauscht?
        swapped = False
        for i in range(1,n):
            if liste[i - 1] > liste[i]:                         # größeres vor kleinerem?
                liste[i - 1], liste[i] = liste[i], liste[i - 1] # tauschen
                swapped = True                                  # merken, dass es in diesem Durchlauf Änderungen gab
        n -= 1

n = 5_000
l1 =  [random.randint(1,n) for _ in range(n)]
l2 = l1.copy()


start = time.time()
bubble_sort(l1)
print(time.time()-start)

start = time.time()
bubble_sort_optimiert(l2)
print(time.time()-start)

assert sorted(l1) == l1, "Fehler bei der Sortierung"
assert sorted(l2) == l2, "Fehler bei der Sortierung"

l3 = [ n-x for x in range(n)] # alle Elemente müssen sortiert werden
start = time.time()
bubble_sort_optimiert(l3)
print(time.time()-start)
