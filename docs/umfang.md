# Fachlicher Umfang von ShelfOps

Ausleihdauer: 28 Tage, ohne Ausleihlimit pro Mitglied.

## Zweck und Grenzen

Bibliothekspersonal erfasst Bücher, physische Exemplare und Mitglieder und verwaltet Ausleihen und Rückgaben über eine JSON-API.

## Datenmodell

Alle IDs sind vom Server vergebene positive Ganzzahlen. Clients können IDs nicht
selbst festlegen. Beziehungen verweisen auf bestehende Datensätze.

| Entität | Gespeicherte Felder | Regel |
|---|---|---|
| Buch | `id`, `title`, `author` | Titel und Autor erforderlich, je 1–200 Zeichen |
| Exemplar | `id`, `book_id` | Gehört genau zu einem Buch; ID dient als Inventarnummer |
| Mitglied | `id`, `name` | Name erforderlich, 1–200 Zeichen; gleiche Namen erlaubt |
| Ausleihe | `id`, `copy_id`, `member_id`, `loaned_at`, `due_at`, `returned_at` | Genau ein Exemplar und ein Mitglied; Rückgabe zunächst `null` |

Bücher mit identischem Titel und Autor sind erlaubt. ISBN, Kontaktdaten und
separate Inventarnummern werden nicht benötigt. Ein Buch darf zunächst ohne
Exemplare bestehen. Texte werden an den Rändern getrimmt; leere Texte sind ungültig.

## Ausleihe und Rückgabe

1. Ein vorhandenes, verfügbares Exemplar kann an ein vorhandenes Mitglied
   ausgeliehen werden. Mehrere aktive Ausleihen pro Mitglied sind erlaubt.
2. Der Server setzt `loaned_at` auf den aktuellen UTC-Zeitpunkt und `due_at`
   auf 28 Tage später. Clients liefern keine eigenen Zeitstempel.
3. Pro Exemplar darf auch bei gleichzeitigen Anfragen höchstens eine aktive
   Ausleihe bestehen. Prüfung und Anlegen müssen atomar erfolgen.
4. Eine Ausleihe ist aktiv, solange `returned_at` gleich `null` ist. Auch eine
   überfällige Ausleihe blockiert eine weitere Ausleihe desselben Exemplars.
5. Bei Rückgabe setzt der Server `returned_at` auf den aktuellen UTC-Zeitpunkt.
   Die Ausleihe bleibt als Historie erhalten; das Exemplar ist wieder verfügbar.
6. Wiederholung derselben Rückgabe liefert die bereits abgeschlossene Ausleihe
   mit HTTP 200. Das ursprüngliche Rückgabedatum wird nicht überschrieben.

## Zustand eines Exemplars

Der Zustand wird berechnet, nicht unabhängig gespeichert:

| Zustand (`status`) | Bedingung |
|---|---|
| `available` | Keine aktive Ausleihe |
| `on_loan` | Aktive Ausleihe und aktueller Zeitpunkt ≤ `due_at` |
| `overdue` | Aktive Ausleihe und aktueller Zeitpunkt > `due_at` |

Genau zum Fälligkeitszeitpunkt ist eine Ausleihe noch nicht überfällig.
Eine verspätete Rückgabe macht das Exemplar ebenfalls wieder verfügbar.

## Geplante API

Fünf fachliche Pfade, insgesamt neun HTTP-Operationen

| Methode | Pfad | Eingabe / Ergebnis |
|---|---|---|
| GET | `/books` | Bücher auflisten |
| POST | `/books` | `title`, `author`; Buch anlegen |
| GET | `/copies` | Exemplare mit `book_id` und berechnetem `status` auflisten |
| POST | `/copies` | `book_id`; Exemplar anlegen |
| GET | `/members` | Mitglieder auflisten |
| POST | `/members` | `name`; Mitglied anlegen |
| GET | `/loans` | Ausleihhistorie inklusive offener Ausleihen auflisten |
| POST | `/loans` | `copy_id`, `member_id`; Ausleihe anlegen |
| POST | `/loans/{id}/return` | Kein Body erforderlich; Rückgabe verarbeiten |

Listen liefern HTTP 200 und ein JSON-Array, sortiert nach ID; leere Listen `[]`.
Anlegen liefert HTTP 201 und das angelegte Objekt, Rückgaben HTTP 200 mit der Ausleihe.

## Fehlervertrag

Fehler liefern ein JSON-Objekt mit `error` (stabiler Code) und `message` (verständliche Beschreibung), keine internen Datenbankdetails.

| HTTP | Situation |
|---|---|
| 400 | Ungültiges JSON, fehlende/unbekannte Felder, leere oder zu lange Texte, falsche Typen |
| 404 | Unbekanntes Buch, Exemplar, Mitglied oder unbekannte Ausleihe |
| 409 | Exemplar hat bereits eine aktive Ausleihe |
| 415 | Anlegen mit einem anderen Content-Type als `application/json` |
| 503 | Konfigurierte Datenbank für die Operation nicht erreichbar |

IDs in JSON müssen positive Ganzzahlen sein, keine Strings oder booleschen Werte.
Ungültige Anfragen hinterlassen keine teilweise angelegten Datensätze.

## Betriebsvertrag und Speicherung

- Port 8000; Konfiguration über Umgebungsvariablen.
- `GET /health`: HTTP 200 mit mindestens `{"status":"ok"}`, ohne Datenbankzugriff.
- `GET /ready`: HTTP 200 bei nutzbarem Speicher, HTTP 503 bei ausgefallener konfigurierter Datenbank. Ohne `DATABASE_URL` ist In-Memory bereit.
- `GET /metrics`: Metriken im Prometheus-Format.
- Ohne `DATABASE_URL`: flüchtiger Speicher für genau einen Prozess. Neustarts löschen die Daten. Mit gesetzter Variable: PostgreSQL 16, kein stiller Rückfall auf In-Memory bei einem Datenbankfehler.
- Beide Speicher erfüllen dieselben fachlichen Regeln. Mehrere Worker oder Kubernetes-Replikate benötigen eine gemeinsame Datenbank.

## Fachliche Abnahmeszenarien für die Umsetzung

- Buch, zwei Exemplare und Mitglied anlegen und in Listen wiederfinden.
- Erstes Exemplar ausleihen; zweites bleibt verfügbar.
- Doppel-Ausleihe ablehnen, auch bei konkurrierenden Anfragen.
- Unbekannte Beziehungen und ungültige Felder ohne Seiteneffekte ablehnen.
- Fälligkeit exakt auf der Grenze und unmittelbar danach prüfen.
- Normale sowie verspätete Rückgabe verarbeiten und erneute Ausleihe ermöglichen.
- Rückgabe wiederholen, ohne Datum oder neue aktive Ausleihe zu verändern.
- Dieselben fachlichen Szenarien mit In-Memory und PostgreSQL prüfen.
