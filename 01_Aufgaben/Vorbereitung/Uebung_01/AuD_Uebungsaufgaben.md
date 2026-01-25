# Übungsaufgaben A&D – Klausurtraining

> **Wichtig:** Diese Aufgaben sind **neu formuliert**, folgen aber exakt dem **Struktur-,
> Schwierigkeits- und Abstraktionsniveau** der Klausur vom 23.01.2025.
> Keine Aufgabe ist identisch, aber **jede prüft dasselbe Verständnis**.

---

## Allgemeine Hinweise
- Programmiersprache: **Python**
- Verwenden Sie **eigene Klassen**
- Teilaufgaben bauen **aufeinander auf**
- Datenstrukturen dürfen **nicht** durch eingebaute Python-Container ersetzt werden

---

## Aufgabe 1 (AFB I – 5 Punkte) – Lineare Datenstruktur

Erstellen Sie eine Klasse `Sequenz`, die eine **linear verkettete Datenstruktur** darstellt.
Der Datenstruktur sollen schrittweise einzelne Werte hinzugefügt werden können.
Nennen Sie diese Fähigkeit `add`.

Intern soll sich die Struktur auf eine **private innere Klasse** stützen, deren Instanzen
jeweils genau **einen Nachfolger** kennen.

---

## Aufgabe 2 (AFB II – 5 Punkte) – Sequenz aufzählbar

Erweitern Sie Ihre Klasse `Sequenz` um folgende Fähigkeiten:

1. Alle enthaltenen Werte sollen **aufgezählt** werden können.
2. Die **Anzahl** der enthaltenen Werte soll zurückgegeben werden.

Die Bestimmung der Anzahl ist **rekursiv** zu implementieren.

---

## Aufgabe 3 (AFB II – 3 Punkte) – Sequenz ausgeben

Erweitern Sie Ihre Klasse `Sequenz` so, dass sie sich als **Zeichenkette darstellen** kann.

**Vorgaben:**
- Eckige Klammern `[` `]`
- Werte durch `, ` getrennt
- Verwenden Sie für die Implementierung Ihre Aufzählungslogik aus Aufgabe 2

Hinweis: Effizienz ist **nicht** entscheidend.

---

## Aufgabe 4 (AFB III – 13 Punkte) – Sortierte Kopie erzeugen (Selection Sort)

Erweitern Sie Ihre Klasse `Sequenz` um eine Methode `sorted_copy()`.

Diese Methode soll:
- eine **neue Sequenz** erzeugen,
- alle Werte der ursprünglichen Sequenz **sortiert einfügen**,
- die ursprüngliche Sequenz **nicht verändern**.

Als Sortierverfahren ist **Selection Sort** zu verwenden.

Mehrfache Vorkommen von Werten müssen erhalten bleiben.

---

## Aufgabe 5 (AFB I – 1 Punkt) – Sequenz testen

Aktivieren Sie den bereitgestellten Testcode.

Die ersten 10 Werte der sortierten Kopie sollen folgende sein:

```
0, 1, 1, 2, 3, 5, 8, 8, 9, 9
```

---

## Aufgabe 6 (AFB I–III – 15 Punkte) – Baumstruktur

Erstellen Sie eine Klasse `Suchbaum`, die einen **geordneten Baum** darstellt.

Intern soll eine **private innere Klasse** verwendet werden, deren Instanzen:
- einen gespeicherten Wert,
- einen linken Nachfolger,
- einen rechten Nachfolger besitzen.

Implementieren Sie eine Methode `add`, mit der Werte eingefügt werden.

**Besonderheit:**  
Mehrfache Werte sind erlaubt.  
Ein gleicher Wert soll **immer im rechten Teilbaum**
unterhalb des ersten Knotens mit diesem Wert eingefügt werden.

---

## Aufgabe 7 (AFB II – 8 Punkte) – Baum aufzählbar

Erweitern Sie Ihren Baum um folgende Fähigkeiten:

1. Die enthaltenen Werte sollen **in aufsteigender Reihenfolge** aufgezählt werden.
2. Die Anzahl der enthaltenen Werte soll zurückgegeben werden.

Die Zählung soll sich **auf die Aufzählung stützen**.

---

## Aufgabe 8 (AFB II – 3 Punkte) – Baum ausgeben

Erweitern Sie die Klasse `Suchbaum`, sodass sie sich als **Zeichenkette** darstellen lässt.

**Vorgaben:**
- Geschweifte Klammern `{}`
- Werte durch `, ` getrennt
- Die Reihenfolge entspricht der Aufzählung aus Aufgabe 7

---

## Aufgabe 9 (AFB I – 1 Punkt) – Baum testen

Aktivieren Sie den vorbereiteten Testcode.

Die Ausgabe des Baums soll **identisch** mit der Ausgabe der sortierten Sequenz sein.

---

## Bonus – Reflexionsfragen (freiwillig)
- Warum sind rekursive Lösungen hier besonders geeignet?
- Welche Aufgaben wären iterativ schwieriger?
- Wo entstehen Laufzeitprobleme bei ungünstigen Eingaben?

---

**Viel Erfolg beim Klausurtraining!**
