"""
Unterricht am 11.11.2025
"""
liste = '5 2 1 3 4 0'.split()
# Wähle ein Element der Liste und nenne es pivot Element
pivot = 3
# Listen werden geteilt
# alle Elemente die kleiner sind, kommt in liste 1 alle anderen in liste 2
l1 = [2, 1, 3, 0]
l2 = [5, 4]

pivotl1a = 2
l1a = [1, 0]
l1b = [2, 3]


###

def quicksort(s: str) -> str:
    if len(s) < 2:
        return s

    pivot = s[0]
    links = rechts = ''

    for z in s[1:]:
        if z > pivot:
            rechts += z
        else:
            links += z

    links = quicksort(links)
    rechts = quicksort(rechts)
    return links + pivot + rechts


s = 'Die Katze tritt die Treppe krumm.'
s = quicksort(s)
print(s)
