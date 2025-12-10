"in-place"


def sort_merge(self):
    result = self._first
    if not result: return  # n=0
    if not result.next: return  # n=1
    k = 1
    while True:
        merge = 0  # zählen, wie oft gemerged wurde
        links = rechts = result
        result = hinten = None
        while links:
            lcount = 0
            for _ in range(k):
                lcount += 1
                rechts = rechts.next
                if not rechts: break
            rcount = k
            merge += 1
            while lcount and rcount and rechts:
                if links.value < rechts.value:
                    kandidat = links
                    lcount -= 1
                    links = links.next
                else:
                    kandidat = rechts
                    rcount -= 1
                    rechts = rechts.next
                kandidat.next = None
                if not result:
                    hinten = result = kandidat
                else:
                    hinten.next = hinten = kandidat  # Reihenfolge!
            while lcount:
                kandidat = links
                links = links.next
                lcount -= 1
                kandidat.next = None
                if not result:
                    hinten = result = kandidat
                else:
                    hinten.next = hinten = kandidat  # Reihenfolge!
            while rcount and rechts:
                kandidat = rechts
                rechts = rechts.next
                rcount -= 1
                kandidat.next = None
                hinten.next = hinten = kandidat  # Reihenfolge!
            links = rechts
        if merge < 2: break
        k *= 2
    self._first = result

