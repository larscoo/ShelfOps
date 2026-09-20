# ShelfOps

ShelfOps ist eine kleine Bibliotheksverwaltung für das Semesterprojekt im Modul
CDS212 an der FH Graubünden. Bücher mit physischen Exemplaren, Mitglieder,
Ausleihen und Rückgaben bilden den fachlichen Kern. Das Projekt dient dem
nachvollziehbaren Aufbau einer vollständigen DevOps-Kette.

## Projektstand

Projektplanung und Repository-Grundgerüst sind vorbereitet. Es gibt noch keine
ausführbare Anwendung, keine Tests, keine CI und kein Deployment. Die Dokumente
beschreiben den geplanten Umfang.

## Einstieg

Voraussetzung für den aktuellen Dokumentationsstand ist Git:

```sh
git clone https://github.com/larscoo/ShelfOps.git
cd ShelfOps
```

Ein kopierbarer Anwendungsstart folgt mit der ersten lauffähigen Version.
Geplant sind Python 3.12 mit Flask und PostgreSQL 16. Ohne `DATABASE_URL` soll
die Anwendung einen flüchtigen In-Memory-Speicher verwenden. Der Dienst wird
auf Port 8000 laufen und `/health`, `/ready` und `/metrics` bereitstellen.

## Geplante Nutzung

Die erste Version wird über eine JSON-API bedient. Ein typischer Ablauf ist:

1. Ein Buch mit Titel und Autor erfassen.
2. Zwei physische Exemplare zu diesem Buch erfassen.
3. Ein Mitglied anlegen.
4. Ein verfügbares Exemplar für 28 Tage an das Mitglied ausleihen.
5. Exemplare auflisten: das erste ist ausgeliehen, das zweite bleibt verfügbar.
6. Die Ausleihe zurückgeben; das erste Exemplar ist wieder verfügbar.

Eine zweite aktive Ausleihe desselben Exemplars wird abgelehnt. Nach Ablauf
seiner Frist ist ein noch nicht zurückgegebenes Exemplar überfällig.
Der vollständige Vertrag steht in [docs/umfang.md](docs/umfang.md).
Die API ist noch nicht implementiert; ausführbare Aufrufbeispiele folgen in Woche 3.

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
