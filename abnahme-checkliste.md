# Abnahme-Checkliste ShelfOps

Aus der CDS212-Projektvorlage übernommen und für ShelfOps ergänzt (siehe [Quellen und KI-Nutzung](docs/quellen-und-ki.md))

Stand: 11. November 2026

Die Haken beziehen sich auf die jeweils verlinkte Konfiguration oder den
dokumentierten Prüflauf. Lokale Labor-Stacks wurden danach gestoppt bzw.
entfernt; ein Haken behauptet keinen dauerhaft laufenden Dienst.

## Git und Zusammenarbeit

- [x] Öffentliches GitHub-Repository existiert: https://github.com/larscoo/ShelfOps
- [x] **`normansuesstrunk`** ist als Collaborator eingeladen
- [x] `main` ist durch eine Branch Protection Rule gegen direkte Pushes geschützt
- [x] Mindestens fünf Pull Requests sind gemergt.
- [x] Jeder dieser PRs hat eine Beschreibung, die *was* und *warum* festhält.
- [x] Jeder dieser PRs war zum Merge-Zeitpunkt grün in der CI.
- [x] [CONTRIBUTING.md](CONTRIBUTING.md) beschreibt GitHub Flow, Commit- und Selbstprüfungsregeln.
- [x] Die Commit-Historie zeigt kontinuierliche Arbeit über die Wochen, nicht einen einzelnen Grosscommit.
- [ ] Tag `v1.0.0` ist gesetzt und ein Release mit Anmerkungen ist veröffentlicht.

GitHub-Abgleich vom 13./14.10.2026: 23 gemergte PRs, alle mit Beschreibung;
`normansuesstrunk` ist als Collaborator aufgeführt. Für
[#19](https://github.com/larscoo/ShelfOps/pull/19),
[#20](https://github.com/larscoo/ShelfOps/pull/20),
[#21](https://github.com/larscoo/ShelfOps/pull/21),
[#22](https://github.com/larscoo/ShelfOps/pull/22) und
[#23](https://github.com/larscoo/ShelfOps/pull/23) wurden die erfolgreichen
Checks samt Abschlusszeitpunkten vor dem jeweiligen Merge geprüft.
Frühe PRs ohne CI werden für diesen Nachweis nicht mitgezählt.
Branch-Schutz: PR-Pflicht, aktuelle Branches, drei Pflichtchecks,
Admin-Durchsetzung, keine Force-Pushes und keine Branch-Löschung.
Die Historie enthält Arbeitsschritte im September und Oktober 2026.

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

GitHub-Läufe und Pflichtchecks sind geprüft. Der rote Demo-Lauf samt Merge-Sperre
und der anschliessende grüne Lauf mit Merge-Freigabe sind dokumentiert.
Der Demo-PR #10 ist seit dem 24.09.2026 gemergt.
Belege: [Woche-5-Hausaufgabe](abgabe/woche-05-ci.md).

- [x] `.github/workflows/ci.yml` läuft bei jedem Pull Request.
- [x] Die Pipeline enthält einen Lint-Schritt (`ruff check` und Formatprüfung).
- [x] Die Pipeline führt die Tests aus (`pytest`).
- [x] Ein Coverage-Gate von mindestens 80 % ist aktiv (`fail_under = 80`).
- [x] Die Pipeline baut das Container-Image.
- [x] Ein absichtlich fehlerhafter Commit macht die Pipeline nachweislich rot.
- [x] Grüner CI-Status ist Voraussetzung zum Mergen.

## CD und Deployment

- [x] `render.yaml` beschreibt den Dienst auf Render.
- [x] Die Anwendung ist unter einer öffentlichen Render-URL erreichbar.
- [x] `GET /health` liefert auf Render `200`.
- [x] Ein Merge auf `main` löst automatisch ein neues Deployment aus.
- [x] `DEPLOYMENT.md` beschreibt Deployment, Rollback und Störungsbehandlung.

Hook und Smoke-Test-Ziel sind für den neuen Blueprint-Service abgeglichen.
Code-Rollback mit Wiederherstellung erfolgreich erprobt. Der vollständige
Neuaufbau durch eine fachfremde Person bleibt offen; siehe [Runbook](DEPLOYMENT.md).

Aktueller Integrationsnachweis vom 13.10.2026:
[CI 38411801620](https://github.com/larscoo/ShelfOps/actions/runs/38411801620)
und [CD 38411945331](https://github.com/larscoo/ShelfOps/actions/runs/38411945331)
erfolgreich. Die öffentliche Instanz lieferte beim Abschlussabgleich
`/health` mit `status: ok`, Version `1.0.0` und Commit
`9ef0a9706cbc712a5483a194577faf613b293c28`; `/ready` lieferte `status: ready`.

## Infrastructure as Code

- [x] Terraform-Konfiguration nutzt den Provider `kreuzwerker/docker`.
- [x] `terraform init` und `terraform validate` laufen fehlerfrei.
- [x] `terraform apply` startet den Container, `terraform destroy` entfernt ihn.
- [x] Konfiguration nutzt Variablen statt hartkodierter Werte.
- [x] `terraform.tfstate` und `.terraform/` stehen in `.gitignore`.

Labor vom 08.10.2026: [Anleitung, Grenzen und Prüfgrundlage](terraform/README.md).

### Hausaufgabe Woche 07

- [x] Separate nginx-Konfiguration mit eigener HTML-Seite und schreibgeschütztem Bind-Mount.
- [x] Numerische Port-Variable mit Validierung und vollständige URL als Output.
- [x] `init`, `fmt -check`, `validate`, `apply` und HTTP-Abruf erfolgreich geprüft.
- [x] Port 80 wird abgelehnt; erneuter Plan nach Apply meldet `No changes`.
- [x] Screenshot des Erstellungsplans als `terraform/plan-screenshot.png` abgelegt.
- [x] nginx-Übungscontainer nach der Prüfung mit `terraform destroy` entfernt; State leer.

Konfiguration und Anleitung: [terraform/nginx](terraform/nginx/README.md).

- [x] Bonus: Zwei nginx-Instanzen via `for_each` auf unterschiedlichen Ports erstellt.
- [x] Bonus: Beide URLs ausgegeben und per HTTP geprüft; Plan danach ohne Änderungen.
- [x] Bonus: Gleiche Host-Ports werden vor dem Anwenden abgelehnt.
- [x] Bonus: Beide Übungscontainer nach der Browser-Prüfung aufgeräumt.

Abschluss inklusive `terraform destroy` in
[PR #18](https://github.com/larscoo/ShelfOps/pull/18) dokumentiert.

## Kubernetes

- [x] Manifeste für Namespace, Deployment und Service liegen unter `k8s/`.
- [x] Der Service bildet Port 80 auf targetPort 8000 ab.
- [x] Das Deployment läuft mit mindestens zwei Replikaten.
- [x] Eine Liveness-Probe prüft `/health`.
- [x] Eine Readiness-Probe prüft `/ready`.
- [x] `kubectl get pods` zeigt alle Replikate als `Running` und `READY 1/1`.

Nachweise: [Startanleitung und Manifeste](k8s/README.md),
[drei bereite Pods im Hausaufgabenlauf](woche08/protokoll-scale.txt),
[Rollout-Status](woche08/protokoll-rollout-status.txt),
[Anfrageprotokoll](woche08/protokoll-rollout.txt),
[Rollback](woche08/protokoll-rollback.txt) und [Analyse](woche08/analyse.md).
Der Cluster wurde nach den Übungen entfernt. Die Betriebsnachweise gelten
für die damaligen Laborstände; die gemeinsame Datenhaltung bleibt offen.

## Monitoring und Sicherheit

- [x] Prometheus scrapt den `/metrics`-Endpunkt.
- [x] Das Target steht in Prometheus unter `Status → Targets` auf UP.
- [x] Ein Grafana-Dashboard „ShelfOps Overview" existiert.
- [x] Das Dashboard zeigt mindestens Request-Rate, Fehlerrate und Latenz.
- [x] Das Dashboard-JSON ist im Repository versioniert.
- [x] Ein Trivy-Scan läuft in der Pipeline und ist im Log sichtbar.
- [x] Der Trivy-Schwellwert ist gesetzt und dokumentiert.
- [ ] `git log -p` enthält keine Passwörter, Tokens oder Keys.
- [x] Secrets liegen in GitHub Secrets bzw. der Deploy-Umgebung, nicht im Code.

Monitoring-Nachweise vom 12./13.10.2026:
[Dashboard](docs/woche-09/dashboard.png),
[Firing-Alarm](docs/woche-09/alert-firing.png),
[Dashboard-JSON](monitoring/grafana/dashboards/shelfops-overview.json) und
[MONITORING.md](MONITORING.md). Der Target-UP-Status wurde im Labor bestätigt;
der lokale Stack wurde anschliessend gestoppt.
Trivy lief in [CI 38411801620](https://github.com/larscoo/ShelfOps/actions/runs/38411801620)
erfolgreich. Das Artefakt `trivy-gate-report` wurde bei der Abschlussprüfung
als vorhanden und nicht abgelaufen bestätigt (Aufbewahrung: 14 Tage).

Secret-Prüfstand: Keine `.env`, privaten Schlüssel oder Terraform-State-Dateien
versioniert. Die Workflows referenzieren GitHub Secrets, Compose eine lokale
`.env`; versionierte Testwerte sind als Beispiele erkennbar.
Eine begrenzte Mustersuche in der Git-Historie fand keine typischen
GitHub-Tokens, AWS-Zugriffsschlüssel, privaten Schlüssel oder Render-Hook-Keys.
Das ist keine vollständige Secret-Prüfung; Screenshots wurden dabei nicht
erneut geprüft. Deshalb bleibt die umfassende Historienprüfung oben offen.

## Dokumentation

- [x] `README.md` erklärt Was, Warum und einen kopierbaren Schnellstart.
- [x] Eine Architekturübersicht mit C4-Diagramm (Kontext + Container) existiert.
- [x] `DEPLOYMENT.md` ist als abarbeitbares Runbook geschrieben.
- [x] `MONITORING.md` beschreibt Metriken, Dashboard und Schwellwerte.
- [x] Mindestens zwei ADRs unter `docs/adr/` mit den vier Pflichtabschnitten.
- [ ] Eine kursfremde Person kann das Projekt allein anhand der Doku starten.

Vorhanden: [Architektur mit C4-Diagrammen](docs/architektur.md),
[Deployment-Runbook](DEPLOYMENT.md), [Monitoring](MONITORING.md),
[ADR 0001](docs/adr/0001-speicherstrategie.md) und
[ADR 0002](docs/adr/0002-ci-gesteuertes-render-deployment.md).
Der [Compose-Schnellstart](README.md#schnellstart-mit-compose-woche-4)
beginnt mit `git clone`. Der
[Monitoring-Schnellstart](MONITORING.md#lokalen-monitoring-stack-starten)
beschreibt Konfiguration, Start, URLs, Grafana-Anmeldung, Last und Aufräumen.
Der praktische Nachweis aus einem frischen Klon allein nach der Dokumentation
bleibt offen; die ergänzten Anleitungen wurden dafür noch nicht neu ausgeführt.

## Selbsteinschätzung und Abgabe

- [x] Die Selbsteinschätzung nach dem Bewertungsschema ist ausgefüllt und liegt
      lokal als [BEWERTUNG.md](BEWERTUNG.md) mit acht Kriterien, Punkten und Belegen vor.
- [ ] Ein frischer Klon des Repositorys startet allein nach dem README.
- [x] Quellen- und KI-Deklaration für den bisherigen Arbeitsstand ergänzt.
      [docs/quellen-und-ki.md](docs/quellen-und-ki.md) enthält Einträge bis
      11.11.2026; bei weiteren Arbeiten bis zur Abgabe nachführen.
- [ ] Tag `v1.0.0` ist gesetzt, Release mit Anmerkungen veröffentlicht.

Die lokal ausgefüllte Selbsteinschätzung und die Dokumentationsänderungen
müssen noch über Commit und Pull Request in den finalen `main`-Stand
übernommen werden. Die Haken für vorhandene Texte ersetzen weder diesen
Schritt noch die weiterhin offenen praktischen Prüfungen.

## Zusätzliche vereinbarte Nachweise

- [x] Fachliche Szenarien aus [Umfang](docs/umfang.md) in beiden Speichern geprüft.
- [x] `/health` funktioniert auch bei Datenbankausfall; `/ready` liefert dann 503.
- [x] CI läuft auch bei Pushes auf `main`; fehlgeschlagene Pflichtprüfungen blockieren Merge.
- [x] CD wartet auf erfolgreiche Prüfungen des auszuliefernden Commits.
- [x] Hosting- und Datenbankgrenzen für die damalige Render-Einrichtung dokumentiert
      ([README, Stand 04.10.2026](README.md#render-blueprint-woche-6-schritt-9));
      keine Zusicherung unveränderter Plattformbedingungen bis zur Abgabe.
- [x] Rollback tatsächlich erprobt und dokumentiert (früheren Commit neu deployt,
      aktuellen Stand wiederhergestellt; kein Artefakt-/Datenbank-Restore).
- [x] Terraform verwaltet den eigenen App-Container; Outputs und Variablen dokumentiert.
- [x] Erneuter Terraform-Plan nach Apply zeigt keine Änderungen (Idempotenz).
- [x] Rolling Update unter laufenden Anfragen ohne beobachteten Ausfall nachgewiesen.
- [x] Resource-Limits sind in den Kubernetes-Deployments gesetzt.
- [ ] Kubernetes-Replikate verwenden dieselbe Datenbank; aktuell getrennte In-Memory-Speicher.
- [x] Dashboard „ShelfOps Overview“ zeigt Veränderungen unter Testlast.
- [x] Trivy-Bericht mit Commit/Image-Bezug abgelegt.
- [ ] Fremde Person hat den dokumentierten Start nachvollzogen; Ergebnis festgehalten.
- [ ] GitHub-Release zu `v1.0.0` nennt Funktionen, Render-URL und Einschränkungen.

Frist: **18. Januar 2027, 12:00 Uhr**.

PostgreSQL-/Compose-Nachweis: [Prüfung vom 24.09.2026](docs/nachweise/compose.md).
