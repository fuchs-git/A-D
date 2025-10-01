import liste

liste_meine = liste.Liste()
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

# Ausgabe
print(f'{liste_meine=}')
print(f'{liste_python=}')
assert print(liste_meine) == print(liste_python), 'Ausgabe ist nicht gleich'

# Länge
print(f'{len(liste_meine)=}')
print(f'{len(liste_python)=}')
assert len(liste_python) == len(liste_meine), 'Länge der Listen sind nicht gleich!'

# print(liste_meine.ausgabe())