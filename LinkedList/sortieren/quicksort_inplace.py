def sort_quick(self):
    def quicksort(links, rechts):
        if links is rechts: return
        pivot = links.value  # Pivot
        aktuell = links  # aktuell Untersuchter
        vorgrenze = links  # Vorgänger von Obergrenze
        grenze = links  # Oberster, der kleiner/gleich dem Pivot ist
        while True:
            aktuell = aktuell.next
            if aktuell is rechts: break
            if aktuell.value < pivot:
                vorgrenze = grenze
                grenze = grenze.next
                grenze.value, aktuell.value = aktuell.value, grenze.value
        links.value, grenze.value = grenze.value, links.value
        if grenze is not rechts:
            vorgrenze = grenze
            grenze = grenze.next
        quicksort(links, vorgrenze)
        quicksort(grenze, rechts)

    quicksort(self._first, None)
