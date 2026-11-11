# Quellen und KI-Nutzung

## Kursmaterial

Referenz: CDS212 – IT Development and Operations, FH Graubünden.

- Repository: https://git.fhgr.ch/suesstnorman/cds-devops.git
- Gelesener Stand: `eddec9b3fa6c3b603626e8e80fad2a7488abe215`
- Lokal gelesen am 19. und 20. September 2026

Taskboard ist eine Referenz, keine übernommene Komplettlösung. Es wurde kein Anwendungscode kopiert.

## KI-Nutzung

Werkzeug: ChatGPT / OpenAI Codex

| Datum | Einsatz |
| --- | --- |
| 19.09.2026 | Bestandsaufnahme, Kursabgleich und Vorschlag einer schrittweisen Umsetzung |
| 20.09.2026 | README, Abnahme-Checkliste und `.gitignore` vorbereitet |
| 20.–24.09.2026 | Unterstützung bei Flask-Anwendung, Browseroberfläche, API, Eingabevalidierung, Ausleihen und Rückgaben, Code und Tests überarbeitet, Build- und Prüfergebnisse ausgewertet |
| 24.09.2026 | Docker-/Compose-Konfiguration korrigiert, Imagevergleich und Nachweise vorbereitet, CI mit Ruff, Tests, Coverage und Build sowie Rot-Grün-Nachweis begleitet |
| 04.10.2026 | Render-Blueprint, CD-Workflow und Smoke-Test unterstützt, Deployment-Runbook und Rollback-Dokumentation überarbeitet |
| 08.10.2026 | Terraform-Konfigurationen für ShelfOps und nginx kontrolliert, Prüfabläufe und Dokumentation vorbereitet |
| 11.10.2026 | Kubernetes-Manifeste und Anleitungen unterstützt, Ergebnisse zu Probes, Rolling Update, Rollback und HPA ausgewertet und dokumentiert |
| 12.10.2026 | Prometheus-/Grafana-Konfiguration kontrolliert, Dashboard und Lastskript unterstützt, Trivy-Scans erklärt, Vorher-/Nachher-Vergleich und Image-Metadaten vorbereitet |
| 13.–14.10.2026 | `MONITORING.md` mit Panel-Dokumentation erstellt, SLOs, Error Budgets, eigener Alarmregel und Runbook kontrolliert, Trivy-Gate in CI, C4-Architektur und zwei ADRs ergänzt, Projektprüfung und Aktualisierung der Nachweisdokumentation durchgeführt |
| 22.10.2026 | Hilfstellung für Labor- und Hausaufgaben bis W9, Git-Historie und Nachweisen abgeglichen |
| 11.11.2026 | Markdown-Dokumentation und Abgabevorgaben geprüft, Pflichtdokumente und offene Ergänzungen aufgelistet, Vorlage `BEWERTUNG.md` nach dem Kursraster erstellt, Zusammensuchen der Belege für BEWERTUNG.md und entsprechend ergänzt |

KI hat mir ausserdem Theorien erklärt und Verständnisfragen beantwortet.
Ebenfalls wurden einige Git-Commit-Texte von Codex vorbereitet, Hilfstellung bezüglich Terminal Git-Befehle gab es auch.

Ausserdem wurden erste Fassungen vieler Markdown-Dateien von Codex entworfen.
Gerade Dokumentationen oder README's, da dies i.d.R. viel Fleissarbeit beinhalten.

## Verwendete Vorlagen und Anforderungen

Die folgenden Pfade beziehen sich auf das oben genannte Kursrepository:

| Quelle | Verwendung |
|---|---|
| `woche-10-abschlussprojekt/code/projekt-vorlage/abnahme-checkliste.md` | Grundlage der übernommenen und angepassten Abnahme-Checkliste |
| `woche-10-abschlussprojekt/code/projekt-vorlage/CONTRIBUTING.md` | GitHub Flow, Conventional Commits und schriftliche Selbstprüfung adaptiert |
| `woche-10-abschlussprojekt/docs/01-projektanforderungen.md` | Fachlicher Kern der Bibliotheksverwaltung und technische Anforderungen |
| `woche-10-abschlussprojekt/docs/03-bewertungsschema.md` | Nachweise und Kriterien der Abschlussabnahme |
| `woche-02-git-github/hausaufgabe/README.md` | Projektstart mit fünf aussagekräftigen Commits und einem gemergten PR |
| `beispiel-app/README.md` | Referenz für Betriebsendpunkte, Speicherwechsel und die Grenzen von In-Memory |
