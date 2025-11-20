def quicksort(s) -> str:
    if isinstance(s, list):
        s = " ".join(s)

    if len(s) <= 1:    # Abbruch, wenn kürzer als 2 (dann ist das nämlich schon sortiert)
        return s

    pivot = s[0]  # willkürlich das Erste Element als Pivot
    left = right = ''  # zunächst leere Teilstrings

    for c in s[1:]:  # String in Teilstrings aufspalten, Pivot dabei weglassen
        if c < pivot:
            left += c
        else:
            right += c

    left, right = quicksort(left), quicksort(right)  # Teilstrings rekursiv sortieren

    return left + pivot + right  # die sortierten Teil-Strings und das Pivot-Element zusammen als Lösung ausgeben

#print(quicksort("Die Katze tritt die Treppe krumm."))
liste = "Die Katze tritt die Treppe krumm.".split()
print(quicksort(liste))