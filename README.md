# ShelfOps

ShelfOps ist eine kleine Bibliotheksverwaltung für das Semesterprojekt im Modul
CDS212 an der FH Graubünden. Bücher mit physischen Exemplaren, Mitglieder,
Ausleihen und Rückgaben bilden den fachlichen Kern. Das Projekt dient dem
nachvollziehbaren Aufbau einer vollständigen DevOps-Kette.

## Projektstand

In Woche 3 sind Bücher, physische Exemplare und Mitglieder erfassbar und
auflistbar, über die JSON-API und die Browseroberfläche unter `/`. `/health`
prüft die Liveness. Daten liegen pro App-Instanz im Arbeitsspeicher und gehen
beim Neustart verloren. Ausleihen, Rückgaben, `/ready`, `/metrics` und PostgreSQL
folgen noch. Docker und CI sind noch nicht vorhanden.

## Lokaler Schnellstart

Voraussetzungen: Python 3.12 oder neuer, Git und Make. Im Terminal:

```sh
git clone https://github.com/larscoo/ShelfOps.git
cd ShelfOps
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
make run
```

Der Entwicklungsserver läuft unter `http://127.0.0.1:8000`. Mit `Ctrl+C` stoppen.
`DATABASE_URL` muss in dieser Version ungesetzt oder leer sein. Bei gesetzter
Variable bricht der Start mit einer Erklärung ab, statt unbemerkt flüchtige Daten
zu verwenden. Öffne `http://127.0.0.1:8000` im Browser: Titel und Autor
eingeben, „Buch hinzufügen“ drücken. Das Buch erscheint direkt im Katalog.
Im Bereich „Exemplare“ ein Buch auswählen und ein physisches Exemplar anlegen.
Unter „Mitglieder“ einen erfundenen Namen erfassen. Gleiche Namen sind erlaubt;
die vergebene ID unterscheidet die Mitglieder.
Die Oberfläche verwendet dieselbe JSON-API wie die folgenden `curl`-Aufrufe.
Zum Erfassen ist JavaScript erforderlich; die bestehende Liste wird bereits
vom Server gerendert.

In einem zweiten Terminal die API bedienen:

```sh
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/books
curl -i http://127.0.0.1:8000/books \
  -H 'Content-Type: application/json' \
  -d '{"title":"Der Prozess","author":"Franz Kafka"}'
curl -i http://127.0.0.1:8000/books
```

Erwartet: HTTP 200 für Health und Listen, HTTP 201 beim Anlegen. Ein neuer
Speicher beginnt mit einer leeren Liste; das erste Buch erhält ID 1.

## Mitglieder und Exemplare

Die IDs aus der jeweiligen Antwort für weitere Aufrufe verwenden. Dieses
Beispiel setzt ein bereits erfasstes Buch mit ID 1 voraus:

```sh
curl -i http://127.0.0.1:8000/copies \
  -H 'Content-Type: application/json' -d '{"book_id":1}'
curl -i http://127.0.0.1:8000/copies
curl -i http://127.0.0.1:8000/members \
  -H 'Content-Type: application/json' -d '{"name":"Alex Beispiel"}'
curl -i http://127.0.0.1:8000/members
```

Ein Buch darf mehrere Exemplare haben. Jedes Exemplar erhält eine eigene ID
und verweist mit `book_id` auf das Buch. Noch sind alle Exemplare `available`,
weil Ausleihen erst im nächsten Schritt umgesetzt werden. Der Zustand wird
nicht als unabhängig änderbares Feld gespeichert.

| Route | Methode | Ergebnis |
|---|---|---|
| `/` | GET | Browseroberfläche |
| `/health` | GET | Liveness, ohne Speicherzugriff |
| `/books` | GET / POST | Bücher auflisten / anlegen |
| `/copies` | GET / POST | Exemplare auflisten / anlegen |
| `/members` | GET / POST | Mitglieder auflisten / anlegen |

Unbekannte `book_id`: HTTP 404. Ungültige Eingaben: HTTP 400.
IDs müssen positive Ganzzahlen sein, Texte 1–200 Zeichen nach dem Trimmen.
Falscher Content-Type beim Anlegen: HTTP 415. Fehlerantworten enthalten
`error` und `message`; eine abgelehnte Anfrage legt keine Datensätze an.

## Prüfen und bauen

```sh
make test
make cov
make lint
make build
```

`make cov` verlangt mindestens 80 % Coverage. `make lint` prüft sowohl Ruff-Regeln
als auch die Formatierung. `make build` erzeugt Wheel und Quelldistribution unter
`dist/`; diese Artefakte werden nicht eingecheckt. `make fmt` formatiert Python.
Die Make-Ziele verwenden standardmässig `.venv/bin/python`, auch ohne aktive venv.

Abhängigkeiten stehen zentral in `pyproject.toml`; `requirements-dev.txt` installiert
das Projekt editierbar inklusive Entwicklungswerkzeugen. Versionsbereiche erlauben
Updates innerhalb der angegebenen Grenzen und sind noch kein reproduzierbares
Lockfile. Wheel und sdist enthalten keine bereits installierten Abhängigkeiten.

## Aufbau

| Datei | Aufgabe |
|---|---|
| `app/__init__.py` | Application Factory: erzeugt eine eigene App mit eigenem Speicher |
| `app/models.py` | Bücher, Exemplare, Mitglieder und Eingabevalidierung |
| `app/repository.py` | Speicher-Schnittstelle und In-Memory-Implementierung |
| `app/routes.py` | Übersetzt HTTP-Anfragen in Validierung und Speicherzugriffe |
| `app/templates/`, `app/static/` | Browseroberfläche mit Jinja, CSS und kleinem JavaScript |
| `wsgi.py` | Startpunkt für Flask und später einen WSGI-Server |
| `tests/` | API- und Fehlerfalltests |
| `pyproject.toml` | Paketmetadaten, Abhängigkeiten, Build- und Prüfkonfiguration |

## Geplante Nutzung

Die erste Version wird über eine JSON-API und eine kleine Browseroberfläche bedient. Ein typischer Ablauf ist:

1. Ein Buch mit Titel und Autor erfassen.
2. Zwei physische Exemplare zu diesem Buch erfassen.
3. Ein Mitglied anlegen.
4. Ein verfügbares Exemplar für 28 Tage an das Mitglied ausleihen.
5. Exemplare auflisten: das erste ist ausgeliehen, das zweite bleibt verfügbar.
6. Die Ausleihe zurückgeben; das erste Exemplar ist wieder verfügbar.

Eine zweite aktive Ausleihe desselben Exemplars wird abgelehnt. Nach Ablauf
seiner Frist ist ein noch nicht zurückgegebenes Exemplar überfällig.
Der vollständige Vertrag steht in [docs/umfang.md](docs/umfang.md).
Bücher, Exemplare und Mitglieder sind implementiert; Ausleihen und Rückgaben folgen noch.

## Ablauf entlang des Kurses

| Woche | Arbeit an ShelfOps |
|---|---|
| 2 | Umfang, Repository, Commit-Regeln und erster PR |
| 3 | Lokale Anwendung und erste Tests |
| 4 | Docker und Compose mit PostgreSQL |
| 5 | CI mit Lint, Tests, Coverage und Image-Build |
| 6 | Render und automatisches Deployment |
| 7 | Terraform für den lokalen App-Container |
| 8 | Kubernetes mit mehreren Replikaten und Probes |
| 9 | Monitoring und Sicherheits-Scan |
| 10 | Integration, vollständige Nachweise und Abgabe |

## Dokumentation

- [Umfang, API und Geschäftsregeln](docs/umfang.md)
- [Arbeitsweise und Selbstprüfung](CONTRIBUTING.md)
- [Abnahme-Checkliste](abnahme-checkliste.md)
- [Quellen und KI-Nutzung](docs/quellen-und-ki.md)

Deployment-Runbook, Monitoring-Anleitung, C4-Architektur und ADRs entstehen mit den jeweiligen Umsetzungsschritten.

## Mitarbeit und Lizenz

Wir verwenden GitHub Flow: kurze Branches, Pull Requests und dokumentierte
Selbstprüfung. Direkte Pushes auf `main` sind nicht vorgesehen. Der technische
Branch-Schutz ist eingerichtet; CI-Pflichtprüfungen folgen mit dem Workflow; Details stehen in [CONTRIBUTING.md](CONTRIBUTING.md).

Das Projekt steht unter der [MIT-Lizenz](LICENSE).
