# ShelfOps v1.0.0 – Abschlussprojekt CDS212

ShelfOps ist eine kleine Bibliotheksverwaltung mit Browseroberfläche und
JSON-API. Das Semesterprojekt zeigt eine DevOps-Kette von GitHub-Pull-Requests
über automatisierte Prüfungen und Deployment bis zum lokalen Monitoring.

**Öffentliche Demo:** https://shelfops.onrender.com

## Funktionen

- Bücher, physische Exemplare und Mitglieder erfassen und auflisten.
- Verfügbare Exemplare für 28 Tage ausleihen und zurückgeben.
- Doppelte aktive Ausleihen verhindern und überfällige Exemplare kennzeichnen.
- Bestandsstatistik sowie Ausleihhistorie anzeigen.
- Betriebsendpunkte `/health`, `/ready` und `/metrics` bereitstellen.

## Technischer Umfang und Nachweise

- Python/Flask mit Gunicorn; Multi-Stage-Image und Nicht-root-Betrieb.
- Lokales Docker Compose mit PostgreSQL 16 und persistentem Daten-Volume.
- CI mit Ruff, Tests beider Speicher, Coverage-Gate von mindestens 80 %,
  Image-Build, Smoke-Test und Trivy-Gate für behebbare HIGH-/CRITICAL-Funde.
- Automatisches Render-Deployment nach erfolgreicher CI für den aktuellen
  `main`-Commit, gefolgt von Commit-Prüfung und fachlichem Smoke-Test.
- Lokale Terraform-Konfiguration mit Variablen, Outputs und Idempotenznachweis.
- Kubernetes-Labor mit drei Replikaten, Probes, Ressourcenlimits,
  Rolling Update, Rollback und dokumentierter HPA-Zusatzaufgabe.
- Lokales Prometheus-/Grafana-Monitoring mit fünf Dashboard-Panels,
  Alarmregeln, SLOs und Error-Budget-Rechnungen.
- Dokumentierter Start aus einem frischen Klon mit Funktionstest und
  Persistenzprüfung sowie Secret-Prüfung der Git-Historie und Screenshots.

## Bekannte Einschränkungen

- Die öffentliche Render-Demo nutzt einen In-Memory-Speicher mit einem Worker.
  Ihre Daten können bei Neustart oder Deployment verloren gehen. Die Instanz
  kann nach Inaktivität einen Cold Start benötigen.
- Die Kubernetes-Pods haben getrennte In-Memory-Speicher. Sie bilden keinen
  gemeinsamen Bibliotheksbestand; die Konfiguration dient dem Nachweis von
  Skalierung, Probes und Rollouts. Eine gemeinsame Datenbank ist bewusst nicht
  Teil dieser Abgabe. Persistenter Fachbetrieb ist lokal in Compose umgesetzt.
- Es gibt keine Anmeldung oder Rollenverwaltung. Ausschliesslich erfundene
  Demo-Daten verwenden, keine echten personenbezogenen Mitgliederdaten.
- Schema-Erstellung ersetzt kein Migrationssystem. Ein automatisiertes
  Datenbank-Backup-/Restore-Verfahren ist nicht implementiert.
- Prometheus und Grafana laufen lokal im Observability-Stack. Alarmregeln
  sind in Prometheus sichtbar; externe Benachrichtigungen sind nicht eingerichtet.
  Die SLOs sind vorgeschlagene Ziele, keine belegten 30-Tage-Zusicherungen.
- Render baut aus dem getesteten Commit ein eigenes Image. Bewegliche
  Basisimage-Tags und Abhängigkeitsbereiche können zu Unterschieden gegenüber
  dem CI-Image führen. Das Trivy-Gate berücksichtigt nur HIGH-/CRITICAL-Funde
  mit verfügbarem Fix; ein grünes Gate bedeutet keine vollständige Befundfreiheit.
- Lokale Labor-Stacks und Cluster müssen nach Anleitung gestartet werden;
  die gespeicherten Nachweise behaupten keinen dauerhaften lokalen Betrieb.

## Persönlicher Rückblick

Zu Beginn war die Git-Arbeitsweise für mich neu, und ich habe Änderungen
zunächst nicht konsequent in kleine Commits aufgeteilt. Im Verlauf des
Projekts habe ich begonnen, kleinere, zusammengehörige Änderungen zu committen.
Bei einem nächsten Projekt würde ich diese Arbeitsweise von Anfang an anwenden.

## Dokumentation

Start und Bedienung sind im README beschrieben. Architektur, Deployment,
Monitoring und Entscheidungen stehen in `docs/architektur.md`, `DEPLOYMENT.md`,
`MONITORING.md` und den ADRs unter `docs/adr/`. Die Selbsteinschätzung ist in
`BEWERTUNG.md`, die Nachweise und ihr Prüfstand in `abnahme-checkliste.md`
verlinkt. Diese Pfade beziehen sich auf das Repository am Release-Tag.
