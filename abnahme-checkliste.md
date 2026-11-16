# Abnahme-Checkliste ShelfOps

Aus der CDS212-Projektvorlage übernommen und für ShelfOps ergänzt (siehe [Quellen und KI-Nutzung](docs/quellen-und-ki.md))

Stand: 16. November 2026

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
Die Historie enthält Arbeitsschritte im September, Oktober und November 2026.

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

PostgreSQL-/Compose-Nachweis: [Prüfung vom 24.09.2026](docs/nachweise/compose.md).

## Hausaufgabe Woche 04

Woche-04-Ergänzung: [Nachweise und Übertragung auf ShelfOps](abgabe/README.md).

- [x] Statistik im Compose-Container mit PostgreSQL geprüft und Antwort gespeichert.
- [x] Naives und optimiertes Image gebaut, Grössen gemessen und begründet.
- [x] Screenshot `abgabe/docker-images.png` ergänzt und beide Image-Grössen geprüft.
- [x] Anerkennung der ShelfOps-Übertragung statt der wörtlichen Taskboard-Aufgabe
      durch die Kursleitung bestätigt; vom Projektverantwortlichen am 16.11.2026 mitgeteilt.

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

Historischer Integrationsnachweis vom 13.10.2026:
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
für die damaligen Laborstände. Die gemeinsame Datenbank wurde am 16.11.2026
bewusst aus dem Abgabeumfang ausgeschlossen; die Einschränkung ist unten
und in den Release-Anmerkungen dokumentiert.

## Monitoring und Sicherheit

- [x] Prometheus scrapt den `/metrics`-Endpunkt.
- [x] Das Target steht in Prometheus unter `Status → Targets` auf UP.
- [x] Ein Grafana-Dashboard „ShelfOps Overview" existiert.
- [x] Das Dashboard zeigt mindestens Request-Rate, Fehlerrate und Latenz.
- [x] Das Dashboard-JSON ist im Repository versioniert.
- [x] Ein Trivy-Scan läuft in der Pipeline und ist im Log sichtbar.
- [x] Der Trivy-Schwellwert ist gesetzt und dokumentiert.
- [x] Git-Historie und Screenshots auf versehentlich veröffentlichte Passwörter,
      Tokens und Schlüssel geprüft, keine bestätigten Secrets gefunden ([Prüfnachweis vom 15.11.2026](docs/nachweise/secret-pruefung.md)).
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

Secret-Prüfstand vom 15.11.2026: 80 erreichbare Commits mit 203 Text- und
elf Screenshot-Dateiversionen sowie Git-Metadaten geprüft. Trivy meldete keine
Secrets; zusätzliche Muster-Treffer wurden als Demo-/Testwerte,
Variablenreferenzen oder öffentliche IDs eingeordnet. Keine `.env`, privaten
Schlüssel oder Terraform-State-Dateien in der geprüften Historie gefunden.
Verfahren, Grenzen und Ergebnis stehen im [Secret-Prüfnachweis](docs/nachweise/secret-pruefung.md).

## Dokumentation

- [x] `README.md` erklärt Was, Warum und einen kopierbaren Schnellstart.
- [x] Eine Architekturübersicht mit C4-Diagramm (Kontext + Container) existiert.
- [x] `DEPLOYMENT.md` ist als abarbeitbares Runbook geschrieben.
- [x] `MONITORING.md` beschreibt Metriken, Dashboard und Schwellwerte.
- [x] Mindestens zwei ADRs unter `docs/adr/` mit den vier Pflichtabschnitten.
- [x] Start anhand der Dokumentation in einem frischen Klon praktisch simuliert
      ([Compose-Prüfnachweis](docs/nachweise/frischer-klon.md)); kein unabhängiger Personentest behauptet.

Vorhanden: [Architektur mit C4-Diagrammen](docs/architektur.md),
[Deployment-Runbook](DEPLOYMENT.md), [Monitoring](MONITORING.md),
[ADR 0001](docs/adr/0001-speicherstrategie.md) und
[ADR 0002](docs/adr/0002-ci-gesteuertes-render-deployment.md).
Der [Compose-Schnellstart](README.md#schnellstart-mit-compose-woche-4)
beginnt mit `git clone`. Der
[Monitoring-Schnellstart](MONITORING.md#lokalen-monitoring-stack-starten)
beschreibt Konfiguration, Start, URLs, Grafana-Anmeldung, Last und Aufräumen.
Der [Compose-Start aus einem frischen Klon](docs/nachweise/frischer-klon.md)
wurde am 11.11.2026 erfolgreich geprüft, einschliesslich API-Smoke-Test
und Persistenz nach `down`/`up`. Der Test wurde durch Codex ausgeführt;
eine unabhängige kursfremde Person und der Monitoring-Neuaufbau waren nicht
Teil dieses Prüflaufs.

## Selbsteinschätzung und Abgabe

- [x] Die Selbsteinschätzung nach dem Bewertungsschema ist ausgefüllt und liegt
      als [BEWERTUNG.md](BEWERTUNG.md) mit acht Kriterien, Punkten und Belegen vor.
- [x] Ein frischer Klon des Repositorys startet nach dem Compose-Schnellstart im README
      ([Prüfnachweis vom 11.11.2026](docs/nachweise/frischer-klon.md)).
- [x] Quellen- und KI-Deklaration für den bisherigen Arbeitsstand ergänzt.
      [docs/quellen-und-ki.md](docs/quellen-und-ki.md) enthält Einträge bis
      16.11.2026 einschliesslich Klontest, Secret-Prüfung und Abschlussvorbereitung.

Selbsteinschätzung und Dokumentationsänderungen wurden mit
[PR #24](https://github.com/larscoo/ShelfOps/pull/24) auf `main` übernommen
(Commit `cbe0cbbc44d967ff75b703254aee1d6ac7753a43`). Der danach erstellte
Nachweis des frischen Klons ist mit
[PR #25](https://github.com/larscoo/ShelfOps/pull/25) übernommen worden,
[PR #26](https://github.com/larscoo/ShelfOps/pull/26) ergänzt die Secret-Prüfung.
Tag und Release werden erst nach dem Merge dieser Abschlussvorbereitung
und erfolgreichen Prüfungen des finalen `main`-Commits veröffentlicht.

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
- [x] Betriebsgrenze der Kubernetes-Demo dokumentiert: getrennte In-Memory-Speicher,
      keine gemeinsame Datenbank im gewählten Abgabeumfang.
- [x] Dashboard „ShelfOps Overview“ zeigt Veränderungen unter Testlast.
- [x] Trivy-Bericht mit Commit/Image-Bezug abgelegt.

Optional: Ein zusätzlicher Test durch eine unabhängige fremde Person wurde
nicht durchgeführt. Der praktische Starttest wurde durch Codex simuliert
und ist oben verlinkt.

## Bewusste Umfangsentscheidung: Kubernetes-Demo

Entscheidung vom **16.11.2026**: Eine gemeinsame
PostgreSQL-Datenbank in Kubernetes wird für diese Abgabe nicht ergänzt.
Die Kurs-Mindestkriterien für Kubernetes sind Namespace, Deployment,
Service mit Port 80 → 8000, mindestens zwei Replikate sowie Liveness- und
Readiness-Probes. Sie sind durch die vorhandenen Manifeste und Laborprotokolle
belegt. Die gemeinsame Kubernetes-Datenbank war ein zusätzliches eigenes
Ziel und wird deshalb nicht mehr als unerledigter Pflichtpunkt geführt.

Die drei Pods teilen keine Bibliotheksdaten. Daten können je nach
angesprochenem Pod unterschiedlich sein und gehen beim Ersetzen eines Pods
verloren. Der Cluster demonstriert Skalierung und Rollouts, konsistenter
persistenter Fachbetrieb ist lokal über Compose mit PostgreSQL nachgewiesen.
Die Demo-Grenze bleibt in [k8s/README.md](k8s/README.md),
[Architektur](docs/architektur.md) und [Release-Anmerkungen](RELEASE_NOTES.md)
sichtbar. Es wird keine bereits vorhandene gemeinsame Datenhaltung behauptet.

## Abschlussvorbereitung und Veröffentlichung

Die noch offenen Veröffentlichungsaufgaben sind ausschliesslich hier aufgeführt,
um dieselben Schritte nicht mehrfach als offene Punkte zu führen. Vorbereitete
Texte und bestandene Tests sind erledigt; Merge, Prüfung des dabei entstehenden
Commits sowie Tag und Release werden erst nach Durchführung abgehakt.

- [x] Release-Anmerkungen als [RELEASE_NOTES.md](RELEASE_NOTES.md) vorbereitet:
      Funktionen, öffentliche URL, bekannte Einschränkungen und Rückblick.
- [x] Vorbereitungsstand `664429963dbe656d87a6a82ea3846a33bef79f62`:
      [CI 43738544669](https://github.com/larscoo/ShelfOps/actions/runs/43738544669)
      und [CD 43738678144](https://github.com/larscoo/ShelfOps/actions/runs/43738678144)
      erfolgreich, am 16.11.2026 lesend geprüft.
- [x] Öffentliche Instanz am 16.11.2026 lesend geprüft:
      `/health` HTTP 200 mit `status: ok`, Version `1.0.0` und Commit
      `664429963dbe656d87a6a82ea3846a33bef79f62`; `/ready` HTTP 200 mit
      `status: ready`. Dies bestätigt den Vorbereitungsstand, nicht einen
      künftig entstehenden Release-Commit.
- [ ] Diese Dokumentationsänderungen über einen PR mergen; CI und CD für den
      dadurch entstehenden finalen `main`-Commit erneut bestätigen.
- [ ] Vor dem Tag die öffentliche Render-Instanz auf passende Commit-SHA,
      `/health` und `/ready` prüfen.
- [x] Quellen-/KI-Deklaration für den Abschlussvorbereitungsstand vom 16.11.2026
      nachgeführt; weitere Unterstützung bis zur Veröffentlichung gegebenenfalls ergänzen.
- [x] Übertragung der Woche-4-Aufgabe auf ShelfOps ist laut Bestätigung des
      Projektverantwortlichen vom 16.11.2026 von der Kursleitung anerkannt
      ([Nachweisdokumentation](abgabe/README.md)).
- [ ] Tag `v1.0.0` auf dem geprüften finalen `main` setzen und das GitHub-Release
      mit Funktionen, Render-URL, Einschränkungen und Rückblick veröffentlichen.

Frist: **18. Januar 2027, 12:00 Uhr**.
