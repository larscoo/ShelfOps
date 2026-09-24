# Abnahme-Checkliste ShelfOps

Aus der CDS212-Projektvorlage übernommen und für ShelfOps ergänzt (siehe [Quellen und KI-Nutzung](docs/quellen-und-ki.md))

Stand: 24. September 2026

Vor der Abgabe des Abschlussprojekts selbst zu prüfen. 


## Git und Zusammenarbeit

- [x] Öffentliches GitHub-Repository existiert: https://github.com/larscoo/ShelfOps
- [x] **`normansuesstrunk`** ist als Collaborator eingeladen
- [x] `main` ist durch eine Branch Protection Rule gegen direkte Pushes geschützt
- [ ] Mindestens fünf Pull Requests sind gemergt.
- [ ] Jeder dieser PRs hat eine Beschreibung, die *was* und *warum* festhält.
- [ ] Jeder dieser PRs war zum Merge-Zeitpunkt grün in der CI.
- [x] [CONTRIBUTING.md](CONTRIBUTING.md) beschreibt GitHub Flow, Commit- und Selbstprüfungsregeln.
- [ ] Die Commit-Historie zeigt kontinuierliche Arbeit über die Wochen, nicht einen einzelnen Grosscommit.
- [ ] Tag `v1.0.0` ist gesetzt und ein Release mit Anmerkungen ist veröffentlicht.

## Containerisierung

- [x] `Dockerfile` verwendet einen Multi-Stage-Build.
- [x] Das Runtime-Image enthält keine Build-Tools oder pip-Caches.
- [x] `docker run --rm <image> whoami` gibt nicht `root` aus.
- [x] `docker build .` läuft ohne Fehler durch.
- [x] `curl localhost:8000/health` liefert im Container `{"status":"ok",...}`.
- [x] `docker-compose.yml` definiert die Dienste `web` und `db`.
- [x] Nach `down` und erneutem `up` sind Daten dank benanntem Volume erhalten.
- [x] `web` startet erst, wenn `db` gesund ist (`condition: service_healthy`).

Container-Nachweis vom 24.09.2026 (lokal, ARM64):
`docker build -t shelfops:local .` erfolgreich; Image-ID
`sha256:754c23e375c5f75e0704a0776e5d78241e52b6f0f694dc31dc87ea72310356e4`.
`whoami` liefert `appuser`, UID 10001. Compiler (`gcc`, `cc`), `make`,
Test-/Build-Pakete und pip-Cache sind nicht vorhanden. `/health` über den
veröffentlichten Host-Port liefert HTTP 200 mit `{"status":"ok"}`; Docker meldet
`healthy`. GUI und JavaScript sind erreichbar. `docker stop` beendet Gunicorn
per SIGTERM mit Exit-Code 0; der temporäre Testcontainer wurde entfernt.
Start- und Prüfbefehle stehen im [README](README.md#start-im-docker-container).

## Hausaufgabe Woche 04

Woche-04-Ergänzung: [Nachweise und Übertragung auf ShelfOps](abgabe/README.md).

- [x] Statistik im Compose-Container mit PostgreSQL geprüft und Antwort gespeichert.
- [x] Naives und optimiertes Image gebaut, Grössen gemessen und begründet.
- [x] Screenshot `abgabe/docker-images.png` ergänzt und beide Image-Grössen geprüft.
- [ ] Anerkennung der ShelfOps-Übertragung statt der wörtlichen Taskboard-Aufgabe geklärt.

## CI-Pipeline

- [ ] `.github/workflows/ci.yml` läuft bei jedem Pull Request.
- [ ] Die Pipeline enthält einen Lint-Schritt (`ruff check` und Formatprüfung).
- [ ] Die Pipeline führt die Tests aus (`pytest`).
- [ ] Ein Coverage-Gate von mindestens 80 % ist aktiv (`fail_under = 80`).
- [ ] Die Pipeline baut das Container-Image.
- [ ] Ein absichtlich fehlerhafter Commit macht die Pipeline nachweislich rot.
- [ ] Grüner CI-Status ist Voraussetzung zum Mergen.

## CD und Deployment

- [ ] `render.yaml` beschreibt den Dienst auf Render.
- [ ] Die Anwendung ist unter einer öffentlichen Render-URL erreichbar.
- [ ] `GET /health` liefert auf Render `200`.
- [ ] Ein Merge auf `main` löst automatisch ein neues Deployment aus.
- [ ] `DEPLOYMENT.md` beschreibt Deployment, Rollback und Störungsbehandlung.

## Infrastructure as Code

- [ ] Terraform-Konfiguration nutzt den Provider `kreuzwerker/docker`.
- [ ] `terraform init` und `terraform validate` laufen fehlerfrei.
- [ ] `terraform apply` startet den Container, `terraform destroy` entfernt ihn.
- [ ] Konfiguration nutzt Variablen statt hartkodierter Werte.
- [ ] `terraform.tfstate` und `.terraform/` stehen in `.gitignore`.

## Kubernetes

- [ ] Manifeste für Namespace, Deployment und Service liegen unter `k8s/`.
- [ ] Der Service bildet Port 80 auf targetPort 8000 ab.
- [ ] Das Deployment läuft mit mindestens zwei Replikaten.
- [ ] Eine Liveness-Probe prüft `/health`.
- [ ] Eine Readiness-Probe prüft `/ready`.
- [ ] `kubectl get pods` zeigt alle Replikate als `Running` und `READY 1/1`.

## Monitoring und Sicherheit

- [ ] Prometheus scrapt den `/metrics`-Endpunkt.
- [ ] Das Target steht in Prometheus unter `Status → Targets` auf UP.
- [ ] Ein Grafana-Dashboard „<Projekt> Overview" existiert.
- [ ] Das Dashboard zeigt mindestens Request-Rate, Fehlerrate und Latenz.
- [ ] Das Dashboard-JSON ist im Repository versioniert.
- [ ] Ein Trivy-Scan läuft in der Pipeline und ist im Log sichtbar.
- [ ] Der Trivy-Schwellwert ist gesetzt und dokumentiert.
- [ ] `git log -p` enthält keine Passwörter, Tokens oder Keys.
- [ ] Secrets liegen in GitHub Secrets bzw. der Deploy-Umgebung, nicht im Code.

## Dokumentation

- [ ] `README.md` erklärt Was, Warum und einen kopierbaren Schnellstart.
- [ ] Eine Architekturübersicht mit C4-Diagramm (Kontext + Container) existiert.
- [ ] `DEPLOYMENT.md` ist als abarbeitbares Runbook geschrieben.
- [ ] `MONITORING.md` beschreibt Metriken, Dashboard und Schwellwerte.
- [ ] Mindestens zwei ADRs unter `docs/adr/` mit den vier Pflichtabschnitten.
- [ ] Eine kursfremde Person kann das Projekt allein anhand der Doku starten.

## Selbsteinschätzung und Abgabe

- [ ] Die Selbsteinschätzung nach dem Bewertungsschema ist ausgefüllt und liegt
      als `BEWERTUNG.md` im Repository.
- [ ] Ein frischer Klon des Repositorys startet allein nach dem README.
- [x] Bisheriger Einsatz von KI-Werkzeugen ist in [docs/quellen-und-ki.md](docs/quellen-und-ki.md) deklariert, fortlaufend ergänzen.
- [ ] Tag `v1.0.0` ist gesetzt, Release mit Anmerkungen veröffentlicht.

## Zusätzliche vereinbarte Nachweise

- [x] Fachliche Szenarien aus [Umfang](docs/umfang.md) in beiden Speichern geprüft.
- [x] `/health` funktioniert auch bei Datenbankausfall; `/ready` liefert dann 503.
- [ ] CI läuft auch bei Pushes auf `main`; fehlgeschlagene Pflichtprüfungen blockieren Merge.
- [ ] CD wartet auf erfolgreiche Prüfungen des auszuliefernden Commits.
- [ ] Hosting-Angebote und Datenbankgrenzen vor Einrichtung aktuell geprüft.
- [ ] Rollback tatsächlich erprobt und dokumentiert.
- [ ] Terraform verwaltet den eigenen App-Container; Outputs und Variablen dokumentiert.
- [ ] Erneuter Terraform-Plan nach Apply zeigt keine Änderungen (Idempotenz).
- [ ] Rolling Update unter laufenden Anfragen ohne beobachteten Ausfall nachgewiesen.
- [ ] Kubernetes-Replikate verwenden dieselbe Datenbank; Resource-Limits gesetzt.
- [ ] Dashboard „ShelfOps Overview“ zeigt Veränderungen unter Testlast.
- [ ] Trivy-Bericht mit Commit/Image-Bezug abgelegt.
- [ ] Fremde Person hat den dokumentierten Start nachvollzogen; Ergebnis festgehalten.
- [ ] GitHub-Release zu `v1.0.0` nennt Funktionen, Render-URL und Einschränkungen.

Frist: **18. Januar 2027, 12:00 Uhr**.

PostgreSQL-/Compose-Nachweis: [Prüfung vom 24.09.2026](docs/nachweise/compose.md).
