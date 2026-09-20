# ShelfOps

ShelfOps ist eine kleine Bibliotheksverwaltung für das Semesterprojekt im Modul
CDS212 an der FH Graubünden. Bücher mit physischen Exemplaren, Mitglieder,
Ausleihen und Rückgaben bilden den fachlichen Kern. Das Projekt dient dem
nachvollziehbaren Aufbau einer vollständigen DevOps-Kette.

## Projektstand

Der erste Teil von Woche 3 ist implementiert: Bücher erfassen und auflisten
sowie `/health`, mit einer kleinen Browseroberfläche unter `/`. Daten liegen pro App-Instanz im Arbeitsspeicher und gehen bei
einem Neustart verloren. Exemplare, Mitglieder, Ausleihen, `/ready`, `/metrics`
und PostgreSQL folgen in weiteren Schritten. Docker und CI sind noch nicht vorhanden.

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

Vor dem Merge liegt dieser Stand auf `feature/book-catalog`; nach dem Klonen
zuerst `git switch feature/book-catalog` ausführen. Der Branch muss dafür gepusht sein.

Der Entwicklungsserver läuft unter `http://127.0.0.1:8000`. Mit `Ctrl+C` stoppen.
`DATABASE_URL` muss in dieser Version ungesetzt oder leer sein. Bei gesetzter
Variable bricht der Start mit einer Erklärung ab, statt unbemerkt flüchtige Daten
zu verwenden. Öffne `http://127.0.0.1:8000` im Browser: Titel und Autor
eingeben, „Buch hinzufügen“ drücken. Das Buch erscheint direkt im Katalog.
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
| `app/models.py` | Buchdaten und Validierung |
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
Bücher sind bereits implementiert; die weiteren Schritte dieses Ablaufs folgen noch.

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
