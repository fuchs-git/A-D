import time
import liste
import liste_Iter

liste_meine = liste.Liste()
liste_iter = liste_Iter.Liste()
liste_python = list() # []

print(f'{liste_meine=}\n{liste_python=}')

# if str(liste_meine) != str(liste_python):
#     print('Alarm, es ist nicht gleich')


assert str(liste_meine) == str(liste_python), 'es ist nicht gleich'


liste_meine.append(1)
liste_python.append(1)
liste_meine.append(2)
liste_python.append(2)
liste_meine.append("drei")
liste_python.append('drei')
for i in range(990):
    liste_meine.append(i)
    liste_python.append(i)


# Ausgabe
print(f'{liste_meine=}')
print(f'{liste_python=}')
assert print(liste_meine) == print(liste_python), 'Ausgabe ist nicht gleich'

# Länge
print(f'{len(liste_meine)=}')
print(f'{len(liste_python)=}')
assert len(liste_python) == len(liste_meine), 'Länge der Listen sind nicht gleich!'

# print(liste_meine.ausgabe())

# Laufzeit
liste_iter = liste_Iter.Liste()
liste_rek = liste.Liste()
liste_py = []

for i in range(996):
    liste_iter.append(i)
    liste_rek.append(i)
    liste_py.append(i)

for x in (liste_iter, liste_rek, liste_py):
    start = time.time()
    print(len(x),time.time() - start, "sek")