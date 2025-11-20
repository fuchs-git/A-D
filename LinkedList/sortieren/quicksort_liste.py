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


print(quicksort([23, 12, 15, 33, 46, 87, 52, 24, 11, 72, 65]))