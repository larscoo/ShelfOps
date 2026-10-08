# ShelfOps

[![CI](https://github.com/larscoo/ShelfOps/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/larscoo/ShelfOps/actions/workflows/ci.yml)

ShelfOps ist eine kleine Bibliotheksverwaltung für das Semesterprojekt im Modul
CDS212 an der FH Graubünden. Bücher mit physischen Exemplaren, Mitglieder,
Ausleihen und Rückgaben bilden den fachlichen Kern. Das Projekt dient dem
nachvollziehbaren Aufbau einer vollständigen DevOps-Kette.

## Projektstand

Der fachliche Kern läuft mit In-Memory oder PostgreSQL 16. Docker Compose
startet die Anwendung und eine persistente Datenbank. `/health` prüft die
Liveness ohne Datenbankzugriff; `/ready` prüft den konfigurierten Speicher.
Die CI für Woche 5 läuft auf GitHub; Lint, Tests und Docker-Build sind
Pflichtprüfungen für `main`. Die App läuft auf Render; der CI-gesteuerte
CD-Workflow ist auf GitHub erfolgreich gelaufen. Der aktuelle Blueprint-Service,
sein Deploy Hook und die Smoke-Test-URL sind abgeglichen.
`/metrics` folgt in einer späteren Kurswoche.

## Continuous Integration (Woche 5)

`.github/workflows/ci.yml` prüft Pull Requests und Pushes auf `main`.
`Lint gate (ruff)` prüft Lint und Formatierung. Parallel testet
`Test (Python 3.12)` beide Speicher mit einer temporären PostgreSQL-16-Datenbank,
erzwingt mindestens 80 % Coverage und lädt `coverage.xml` als Artefakt hoch.
Erst wenn beide Jobs erfolgreich sind, baut `Build image` das Docker-Image und
prüft Nicht-root-Ausführung sowie `/health`. Das Image wird nicht veröffentlicht.

pip nutzt einen Cache auf Basis von `pyproject.toml`. Alle drei Checks sind
Pflichtprüfungen auf `main`; der PR-Branch muss vor dem Merge aktuell sein.
Vorgehen und offene Nachweise: [Woche-5-Hausaufgabe](abgabe/woche-05-ci.md).

## Schnellstart mit Compose (Woche 4)

Voraussetzung: Docker Desktop läuft. Im Projektordner einmalig:

```sh
cp .env.example .env
docker compose up --build -d --wait
```

Eine vorhandene `.env` beibehalten und bei Bedarf bearbeiten. Die Beispielwerte
sind ausschliesslich für den lokalen Demobetrieb. Benutzer, Datenbank und Passwort
müssen für die zusammengesetzte `DATABASE_URL` URL-tauglich sein; bei eigenen
lokalen Passwörtern beispielsweise nur zufällige Buchstaben und Ziffern verwenden.
Keine echten Zugangsdaten einchecken. Die `.env` ist bereits ignoriert.

Falls noch der einzelne Container `shelfops` aus dem vorigen Schritt läuft:
`docker stop shelfops` ausführen oder `WEB_PORT` in `.env` ändern. Oberfläche:
`http://localhost:8000` (beziehungsweise der gewählte Port).

```sh
curl -i http://localhost:8000/health
curl -i http://localhost:8000/ready
docker compose ps
docker compose logs web
```

`web` wartet auf den Healthcheck von `db`; das benannte Volume `db-data` hält
PostgreSQL-Daten. Zwei Gunicorn-Worker teilen sich denselben Datenbestand.
Die Datenbank veröffentlicht keinen Port auf dem Host; nur die App ist lokal
auf `127.0.0.1` erreichbar. `.env` wird von Compose gelesen, nicht automatisch
von `make run` oder einem einzelnen `docker run`.

### Persistenz selbst prüfen

1. Im Browser ein Buch, Exemplar und Mitglied anlegen, eine Ausleihe erfassen.
2. `docker compose down` ausführen.
3. Mit `docker compose up -d --wait` erneut starten.
4. Seite neu laden: Daten und Ausleihhistorie müssen noch vorhanden sein.

`down` behält das Volume. **`down -v` löscht die Daten dauerhaft** und gehört
nicht zu diesem Persistenztest. Das Volume ist an den Compose-Projektnamen
gebunden; beim Neustart im gleichen Projektordner bleiben. Änderungen von
DB-Benutzer/Passwort in `.env` ändern keine bereits initialisierten DB-Rollen.

### Datenbankausfall selbst prüfen

```sh
docker compose stop db
curl -i http://localhost:8000/health  # 200
curl -i http://localhost:8000/ready   # 503
curl -i http://localhost:8000/books   # 503
docker compose up -d --wait db
curl -i http://localhost:8000/ready   # wieder 200
```

Es gibt bei Datenbankfehlern keinen stillen Wechsel auf In-Memory. Bereits
bestehende Daten bleiben erhalten. Der Docker-Liveness-Healthcheck bleibt bei
einem DB-Ausfall grün; das ist bewusst von Readiness getrennt.

## Lokaler Start ohne Datenbank

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
`DATABASE_URL` ungesetzt oder leer lassen, um In-Memory zu verwenden.
Eine gesetzte PostgreSQL-Verbindungsadresse aktiviert die Datenbank.
Ohne Datenbank gehen die Daten beim Serverneustart verloren. Öffne `http://127.0.0.1:8000` im Browser: Titel und Autor
eingeben, „Buch hinzufügen“ drücken. Das Buch erscheint direkt im Katalog.
Im Bereich „Exemplare“ ein Buch auswählen und ein physisches Exemplar anlegen.
Unter „Mitglieder“ einen erfundenen Namen erfassen. Gleiche Namen sind erlaubt;
die vergebene ID unterscheidet die Mitglieder.
Unter „Ausleihen“ ein verfügbares Exemplar und ein Mitglied auswählen. Nach dem
Ausleihen zeigt die Historie die Frist und bietet eine Rückgabe-Schaltfläche.
Nach Ausleihe und Rückgabe lädt die Seite neu. Zeiten werden in UTC angezeigt;
für den aktuellen Überfälligkeitsstatus die Seite erneut laden.
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

## Start im Docker-Container

Voraussetzung: Docker Desktop läuft. Im Projektordner:

```sh
docker build -t shelfops:local .
docker run --rm shelfops:local whoami
docker run --rm --name shelfops -p 127.0.0.1:8000:8000 shelfops:local
```

`whoami` muss `appuser` ausgeben. Falls `make run` noch Port 8000 belegt,
den Entwicklungsserver vorher mit `Ctrl+C` stoppen. Anschliessend die Oberfläche
unter `http://localhost:8000` öffnen. In einem zweiten Terminal:

```sh
curl -i http://localhost:8000/health
docker inspect --format '{{.State.Health.Status}}' shelfops
docker logs shelfops
docker stop shelfops
```

Nach dem ersten erfolgreichen Healthcheck steht der Status auf `healthy`.
`docker stop` beendet Gunicorn kontrolliert; `--rm` entfernt danach den Container.
Alle Daten sind weiterhin flüchtig. `DATABASE_URL` bleibt ungesetzt und
`GUNICORN_WORKERS` auf `1`, weil mehrere Prozesse getrennte In-Memory-Daten hätten.

Das [Dockerfile](Dockerfile) basiert auf `beispiel-app/Dockerfile` des CDS212-Kurses:

- `base`: Python 3.12 slim, Arbeitsverzeichnis und Python-Umgebung.
- `builder`: liest Laufzeit-Abhängigkeiten aus `pyproject.toml` und installiert
  sie ohne pip-Cache nach `/install`, vor dem Kopieren des Anwendungscodes.
- `runtime`: übernimmt nur installierte Laufzeitpakete und Anwendungscode;
  startet als `appuser` (UID 10001) mit Gunicorn auf Port 8000.
- Der Healthcheck fragt `/health` mit Pythons Standardbibliothek ab.
- `exec` im Startbefehl reicht Stop-Signale direkt an Gunicorn weiter.

[.dockerignore](.dockerignore) lässt nur Dockerfile, Paketkonfiguration und
Anwendungscode in den Build-Kontext. `.git`, `.venv`, Tests, `.env` und lokale
Build-Artefakte bleiben draussen. Es gibt keinen Bind-Mount: Änderungen am Code
werden erst nach erneutem Build und Containerstart sichtbar.

## Render-Blueprint (Woche 6, Schritt 9)

`render.yaml` im Repository-Wurzelverzeichnis beschreibt einen Docker-Web-Service
namens `shelfops`: Free-Instanz in Frankfurt, Branch `main`, Build-Kontext `.`,
Dockerfile `./Dockerfile`, Healthcheck `/health`, `PORT=8000` und ein Worker.
Ohne `DATABASE_URL` sind Daten flüchtig; es wird keine Datenbank angelegt.
Die Region entspricht der Laborvorlage und muss mit der Region des vorhandenen
Dienstes verglichen werden.

Für Schritt 10 steht `autoDeployTrigger` auf `off`: GitHub Actions löst den
Deploy Hook nach grüner CI aus. `APP_VERSION=1.0.0` wird in `/health` angezeigt;
`LOG_LEVEL` wird nicht ausgewertet. Der aktuelle Dienst wird über den Blueprint
verwaltet; Konfigurationsänderungen erfolgen über die versionierte Datei.

Der Projektverantwortliche hat die früheren Dienste entfernt und am 04.10.2026
den Blueprint `exs-db19pf942hec73emj8rg` angelegt. Dessen Service
`srv-db19pnid0e5s73ep7isg` ist unter https://shelfops.onrender.com erreichbar.
Eine erneute Neuanlage ist nicht nötig. Für einen eigenen Nachbau beschreibt
[DEPLOYMENT.md](DEPLOYMENT.md) den vollständigen Blueprint-Hauptpfad.

Referenzen (geprüft am 04.10.2026):
[Blueprint-Spezifikation](https://render.com/docs/blueprint-spec),
[Free-Tier-Grenzen](https://render.com/docs/free).

## Smoke-Test einer laufenden Instanz (Woche 6)

Das an das Kursskript angelehnte Skript benötigt Bash, curl und Python 3.
Im ShelfOps-Wurzelverzeichnis ausführen und die Beispiel-URL ersetzen:

```sh
chmod +x scripts/smoke-test.sh
./scripts/smoke-test.sh https://DEINE-APP.onrender.com
```

Es prüft `/health` (mit Wiederholungen für einen Cold Start), `/ready`, das
Anlegen und Lesen eines Buchs, Exemplars und Mitglieds sowie Ausleihe und
Rückgabe. Dabei werden die tatsächlichen IDs verwendet; die Datenbank muss
nicht leer sein. Nur wenn alle HTTP- und JSON-Prüfungen erfolgreich sind,
erscheint `SMOKE TEST PASSED` und das Skript endet mit Exit-Code 0.
Fehlgeschlagene Prüfungen liefern Exit-Code 1, ungültige Aufrufe Exit-Code 2.

**Testdaten bleiben erhalten:** Pro Lauf entstehen ein Buch, ein Exemplar,
ein Mitglied und eine zurückgegebene Ausleihe. Namen beginnen mit `smoke-test-`.
ShelfOps hat keine Lösch-API. Bei einem Abbruch nach dem Ausleihen kann die
Ausleihe offen bleiben; die ausgegebene ID hilft bei der Rückgabe über die GUI.
Schreibende Anfragen werden nicht automatisch wiederholt.

Bei Bedarf `PYTHON=/pfad/zu/python3` setzen. `HEALTH_RETRIES` (Standard 12)
und `BACKOFF_SECONDS` (Standard 5) steuern die Startversuche; zwischen ihnen
wächst die Wartezeit linear. Jeder HTTP-Aufruf hat ein Zeitlimit von 60 Sekunden.
Lokal sind Tests etwa gegen `http://127.0.0.1:8000` möglich. Ohne Datenbank
muss die Zielinstanz mit einem Worker laufen. Das Skript prüft die Funktion,
mit `EXPECTED_COMMIT=<vollständige Commit-SHA>` zusätzlich, ob genau dieser
Commit in `/health` erscheint. Erst danach werden Testdaten angelegt.
Ohne diese Variable bleibt der manuelle Funktionstest unverändert.

## Continuous Deployment (Woche 6, Schritt 10)

`.github/workflows/cd.yml` wartet auf erfolgreiche `CI`-Läufe für Pushes auf
`main`. PR-Läufe lösen keine Deployments aus. Auch ein manueller Start über
**Actions → CD → Run workflow → main** verlangt einen erfolgreichen Push-CI-Lauf
für denselben Commit. Veraltete Commits werden vor dem Hook-Aufruf abgelehnt.
Gleichzeitige CD-Läufe werden serialisiert.

Voraussetzungen in GitHub unter **Settings → Secrets and variables → Actions**:

- Secret `RENDER_DEPLOY_HOOK`: vollständige geheime Hook-URL aus Render.
- Variable `APP_URL`: öffentliche Basis-URL, hier `https://shelfops.onrender.com`.

Im bestehenden Render-Service **Auto-Deploy abschalten** und `APP_VERSION=1.0.0`
setzen, falls noch nicht vorhanden. `PORT=8000`, `GUNICORN_WORKERS=1` und
Healthcheck `/health` beibehalten. Die Hook-URL nicht in Dateien oder Logs kopieren.

Der Workflow checkt den geprüften Commit aus und übergibt seine SHA als `ref`
an den Hook. `/health` meldet neben `status` und `version` den `commit` aus
Renders Variable `RENDER_GIT_COMMIT` (lokal ohne diese Variable: `unknown`).
Eine alte, noch gesunde Instanz genügt nicht: Der Smoke-Test wartet zunächst auf
den erwarteten Commit und prüft anschliessend den vollständigen Bibliotheksablauf.
Das erste Deployment dieses Workflows führt diese zusätzliche Health-Angabe ein.
Der Job ist auf 25 Minuten begrenzt; ein Fehler erfordert Prüfung der Render-Events.
Ein neuerer Push während eines laufenden Deployments wird durch den nächsten
CI/CD-Lauf bearbeitet. Der bereits gestartete Hook wird nicht abgebrochen.

Nach dem Merge prüfen:

1. CI für den Merge-Commit auf `main` ist grün.
2. Der anschliessende CD-Lauf zeigt einen akzeptierten Hook-Aufruf.
3. Render Events zeigt einen durch den Hook ausgelösten Deploy desselben Commits.
4. Der CD-Schritt endet mit `SMOKE TEST PASSED`; `/health` meldet dieselbe SHA.

Die frühere Abweichung zwischen Hook-Ziel und Smoke-Test-URL ist behoben.
[CD-Lauf 37225622868](https://github.com/larscoo/ShelfOps/actions/runs/37225622868)
und der Live-Deploy `dep-db19tcnavr4c73aunf80` wurden gegen denselben aktuellen
Service abgeglichen. Ein Code-Rollback und die Wiederherstellung wurden ebenfalls
erprobt. Runbook und Nachweise: [DEPLOYMENT.md](DEPLOYMENT.md).

Lokale Vorprüfung am 04.10.2026: 214 Tests bestanden, 3 PostgreSQL-spezifische
Fälle für In-Memory übersprungen, Coverage 98,42 %; Ruff und YAML-/Shell-Syntax
erfolgreich. Gegen temporäre lokale Server geprüft: erwarteter Commit erscheint
verzögert (Erfolg), dauerhaft alter Commit (Abbruch ohne Schreibzugriff),
manueller Test ohne Commit-Vorgabe (Erfolg). Mit simulierten Antworten geprüft:
veralteter Commit oder fehlende/rote CI wird abgelehnt; Hook-HTTP 200/202 wird
akzeptiert und 401 abgelehnt.

Quellen zur Umsetzung:
[Render Deploy Hooks](https://render.com/docs/deploy-hooks),
[Render-Umgebungsvariablen](https://render.com/docs/environment-variables),
[GitHub workflow_run](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_run).

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
und verweist mit `book_id` auf das Buch. Der Zustand (`available`, `on_loan` oder `overdue`) wird aus der aktiven Ausleihe
und der aktuellen Zeit berechnet, nicht als unabhängig änderbares Feld gespeichert.

| Route | Methode | Ergebnis |
|---|---|---|
| `/` | GET | Browseroberfläche |
| `/health` | GET | Liveness, ohne Speicherzugriff |
| `/ready` | GET | Speicher verfügbar: 200; Datenbank nicht bereit: 503 |
| `/books` | GET / POST | Bücher auflisten / anlegen |
| `/copies` | GET / POST | Exemplare auflisten / anlegen |
| `/copies/stats` | GET | Gesamtzahl sowie verfügbare, ausgeliehene und überfällige Exemplare |
| `/members` | GET / POST | Mitglieder auflisten / anlegen |
| `/loans` | GET / POST | Ausleihhistorie auflisten / Ausleihe anlegen |
| `/loans/{id}/return` | POST | Rückgabe ohne Request-Body verarbeiten |

Unbekannte `book_id`: HTTP 404. Ungültige Eingaben: HTTP 400.
Die Statistik zählt `on_loan` und `overdue` getrennt: Ihre Summe mit `available`
ergibt `total`. Nachweise zur Docker-Hausaufgabe stehen unter [abgabe/](abgabe/README.md).
IDs müssen positive Ganzzahlen sein, Texte 1–200 Zeichen nach dem Trimmen.
Falscher Content-Type beim Anlegen: HTTP 415. Fehlerantworten enthalten
`error` und `message`; eine abgelehnte Anfrage legt keine Datensätze an.

## Ausleihen und Rückgaben

Nach Anlegen eines Exemplars und Mitglieds deren IDs einsetzen (hier jeweils 1):

```sh
curl -i http://127.0.0.1:8000/loans \
  -H 'Content-Type: application/json' -d '{"copy_id":1,"member_id":1}'
curl -i http://127.0.0.1:8000/loans
curl -i http://127.0.0.1:8000/copies
curl -i -X POST http://127.0.0.1:8000/loans/1/return
```

Eine Ausleihe dauert exakt 28 Tage ab dem serverseitigen UTC-Zeitpunkt.
JSON-Zeitstempel sind ISO-8601 mit `+00:00`; `returned_at` ist bis zur Rückgabe
`null`. Ein Mitglied kann beliebig viele verschiedene Exemplare ausleihen.
Ein bereits ausgeliehenes Exemplar wird mit HTTP 409 abgelehnt, auch wenn die
Ausleihe überfällig ist. Gleichzeitige Schreibzugriffe werden im In-Memory-Speicher
mit einem Lock geschützt; diese Garantie gilt innerhalb eines Prozesses.

Genau zum Fälligkeitszeitpunkt ist das Exemplar noch `on_loan`, erst danach
`overdue`. Eine Rückgabe macht es wieder `available`. Die Ausleihhistorie bleibt
erhalten. Wiederholte Rückgaben liefern HTTP 200 und verändern das ursprüngliche
Rückgabedatum nicht, auch wenn das Exemplar inzwischen erneut ausgeliehen wurde.
Unbekannte Exemplare, Mitglieder oder Ausleihen liefern HTTP 404.

## Prüfen und bauen

```sh
make test
make cov
make lint
make build
```

`make test` läuft ohne Docker; PostgreSQL-Fälle werden ohne `TEST_DATABASE_URL`
explizit übersprungen. Für die vollständige Prüfung benötigt `make cov` Docker
Desktop und die aktualisierte virtuelle Umgebung:

```sh
.venv/bin/python -m pip install -r requirements-dev.txt
make cov
```

`make cov` startet automatisch eine eigene PostgreSQL-16-Testdatenbank auf einem
freien lokalen Port, führt die fachlichen Tests mit beiden Speichern aus und
entfernt den Testcontainer danach. Die Testdaten liegen nur im RAM (`tmpfs`),
nicht im Anwendungsvolume. `make test-db` führt dieselben Tests ohne Coverage aus.
Jeder Datenbanktest erhält ein eigenes Schema. Für eine extern bereitgestellte
Testdatenbank ist `TEST_DATABASE_URL` möglich; sie muss ausdrücklich
`shelfops_test` heissen. Diese Variable niemals auf die Anwendungsdatenbank setzen.

Das vollständige Coverage-Gate verlangt mindestens 80 % Abdeckung inklusive
PostgreSQL-Code. `make lint` prüft sowohl Ruff-Regeln
als auch die Formatierung. `make build` erzeugt Wheel und Quelldistribution unter
`dist/`; diese Artefakte werden nicht eingecheckt. `make fmt` formatiert Python.
Die Tests verwenden eine kontrollierbare Uhr und prüfen Fälligkeitsgrenzen ohne
reale Wartezeiten. Auch konkurrierende Ausleihen und wiederholte Rückgaben
werden geprüft.
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
| `app/postgres.py` | PostgreSQL-Tabellen und transaktionale Speicheroperationen |
| `docker-compose.yml` | Anwendung und PostgreSQL mit persistentem Volume |
| `docker-compose.test.yml` | Isolierte kurzlebige Testdatenbank |
| `app/routes.py` | Übersetzt HTTP-Anfragen in Validierung und Speicherzugriffe |
| `app/templates/`, `app/static/` | Browseroberfläche mit Jinja, CSS und kleinem JavaScript |
| `wsgi.py` | Startpunkt für Flask und später einen WSGI-Server |
| `tests/` | API- und Fehlerfalltests |
| `pyproject.toml` | Paketmetadaten, Abhängigkeiten, Build- und Prüfkonfiguration |

## Datenbankaufbau

Die Implementierung orientiert sich am Repository-Muster der CDS212-Beispiel-App.
Jede Operation verwendet eine kurze psycopg-Verbindung mit Transaktion statt
eines dauerhaften Pools. Für das kleine Projekt vereinfacht das Lebensdauer und
Wiederverbindung nach Ausfällen; zusätzlicher Verbindungsaufbau kostet etwas Zeit.
Verbindungsversuche sind auf 3 Sekunden begrenzt, SQL-Statements auf 5 Sekunden.

Die Tabellen entstehen beim ersten Speicherzugriff, nicht beim App-Start.
Dadurch bleibt `/health` auch bei einer schon beim Start fehlenden DB erreichbar.
Ein PostgreSQL-Advisory-Lock serialisiert die erstmalige Schema-Erstellung zwischen
Workern. `CREATE TABLE IF NOT EXISTS` ist noch kein Migrationssystem: spätere
Schemaänderungen benötigen einen eigenen, dokumentierten Migrationsschritt.

Fremdschlüssel sichern Beziehungen. Eine Transaktion mit Zeilensperre und ein
partieller eindeutiger Index auf `loans(copy_id) WHERE returned_at IS NULL`
verhindern doppelte aktive Ausleihen. Rückgaben sperren die betroffene Ausleihe,
sodass Wiederholungen das Rückgabedatum nicht überschreiben. IDs können in
PostgreSQL nach zurückgerollten Transaktionen Lücken enthalten.

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
Dieser fachliche Ablauf ist mit In-Memory und PostgreSQL implementiert.
Die gleichen fachlichen Regeln werden mit beiden Speicherarten geprüft.

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
- [PostgreSQL-/Compose-Prüfnachweis](docs/nachweise/compose.md)
- [Lokaler Betrieb mit Terraform](terraform/README.md)

Deployment-Runbook, Monitoring-Anleitung, C4-Architektur und ADRs entstehen mit den jeweiligen Umsetzungsschritten.

## Mitarbeit und Lizenz

Wir verwenden GitHub Flow: kurze Branches, Pull Requests und dokumentierte
Selbstprüfung. Direkte Pushes auf `main` sind nicht vorgesehen. Der technische
Branch-Schutz ist eingerichtet; CI-Pflichtprüfungen folgen mit dem Workflow; Details stehen in [CONTRIBUTING.md](CONTRIBUTING.md).

Das Projekt steht unter der [MIT-Lizenz](LICENSE).
