from typing import Any


class Dict:
    class _Element:

        def __init__(self, key, value: Any):
            self.next = None
            self.key = key
            self.value = value

        def __iter__(self):
            now: Dict._Element
            now = self
            while now is not None:
                yield now.key, now.value
                now = now.next

        def __repr__(self):
            if self.next is None:
                return f'{repr(self.key)}: {repr(self.value)}'
            else:
                return f'{repr(self.key)}: {repr(self.value)}, {repr(self.next)}'

        def append(self, key, value):
            if self.key == key:
                self.value = value
                return

            if self.next is None:
                self.next = Dict._Element(key, value)
                return

            self.next.append(key, value)

    def __init__(self):
        self.first = None

    def __repr__(self):
        if self.first is None:
            return '{}'
        return f'{{{self.first}}}'

    def set(self, key, value: Any):
        if self.first is None:
            self.first = Dict._Element(key=key, value=value)
        else:
            self.first.append(key, value)
        return


mein_dict = Dict()
mein_dict.set('test', 'wert')
mein_dict.set('test2', 'wert2')
mein_dict.set('test2', 42)
print(mein_dict)

test = {}
test['key'] = 'value'
test['key2'] = 'value2'
print(test)
