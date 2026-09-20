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
