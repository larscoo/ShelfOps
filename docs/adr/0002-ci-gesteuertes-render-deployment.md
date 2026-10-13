# ADR 0002 – Render-Deployment nach erfolgreicher GitHub-Actions-CI

## Status

accepted – dokumentiert am 13.10.2026.
Dieses ADR beschreibt den bereits implementierten Deployment-Pfad,
einschliesslich des in Woche 10 ergänzten Trivy-Gates.

## Kontext

Die öffentliche ShelfOps-Demo soll nach einem Merge automatisch den geprüften
Quellstand ausführen. Fehler in Lint, Tests, Coverage, Build oder Sicherheits-Gate
sollen die Auslieferung stoppen. Ein erfolgreicher PR-Lauf allein genügt nicht:
Nach dem Merge muss auch der tatsächliche `main`-Commit geprüft sein.

Direktes Render-Auto-Deploy bei jedem Push wäre einfacher, würde aber einen
zweiten Deployment-Auslöser neben unserer CI-Kontrolle schaffen. Manuelle
Deployments würden regelmässige Bedienung erfordern. Eine Registry mit
Auslieferung genau desselben geprüften Image-Digests wäre stärker
reproduzierbar, erweitert aber den hier gewählten Build- und Deployment-Ablauf.

## Entscheidung

Wir verwenden getrennte GitHub-Actions-Workflows für CI und CD.
`render.yaml` beschreibt den Docker-Web-Service und schaltet mit
`autoDeployTrigger: off` das automatische Deployment durch Render ab.
GitHub Actions löst den Deploy Hook nach einer erfolgreichen Push-CI auf
`main` aus. PR-Läufe lösen kein Deployment aus.

CD prüft vor dem Hook-Aufruf, ob die SHA noch dem aktuellen `main` entspricht
und der letzte Push-CI-Lauf für genau diese SHA erfolgreich war. Dieselben
Prüfungen gelten bei einem manuellen CD-Start. Deployments werden über eine
Concurrency-Gruppe serialisiert. Die SHA wird als `ref` an Render übergeben.
Danach wartet der Smoke-Test auf diesen Commit in `/health` und prüft den
Bibliotheksablauf. Der geheime Hook liegt in GitHub Secrets; die öffentliche
Ziel-URL liegt als GitHub-Variable vor.

Der bestehende Pflichtcheck `Build image` umfasst den Trivy-Scan. Behebbare
HIGH-/CRITICAL-Funde lassen die CI fehlschlagen und verhindern damit diesen
CD-Pfad. Render baut aus dem getesteten Commit selbst ein Image;
eine Registry-Übergabe des CI-Images erfolgt derzeit nicht.

## Konsequenzen

Positiv:

- Der reguläre Weg von Merge über Prüfungen bis Deployment ist automatisiert
  und anhand der GitHub-Läufe nachvollziehbar.
- Auch manuelle CD-Starts umgehen die Prüfung des aktuellen Commits nicht.
- Der Smoke-Test erkennt eine noch laufende alte Codeversion und prüft mehr
  als die reine HTTP-Erreichbarkeit.
- Blueprint und Workflows sind versioniert; der Hook selbst bleibt geheim.

Negativ und Grenzen:

- Die Auslieferung hängt von GitHub Actions, Render und einem gültigen Hook ab.
- Der erneute Build auf Render kann wegen beweglicher Basisimages und
  Paketversionen vom CI-Image abweichen. Der Trivy-Bericht beschreibt das
  CI-Image, nicht zwingend das später ausgelieferte Binärartefakt.
- Der erfolgreiche Scan toleriert ungefixte HIGH-/CRITICAL-Funde sowie
  niedrigere Schweregrade; diese benötigen weiterhin eine eigene Bewertung.
- Render-Konfigurationsänderungen und manuelle Dashboard-Aktionen sind
  zusätzliche Betriebswege; der Workflow verhindert sie nicht technisch.
- Ein Rollback ist ein eigener, dokumentierter Vorgang. Automatische
  Deployments müssen während einer Rollback-Übung koordiniert werden.
- Die aktuelle Render-Demo verwendet In-Memory; ein Deployment kann ihre
  Daten verlieren. Der Smoke-Test erzeugt zudem eigene Demo-Datensätze.

Belege: [CI](../../.github/workflows/ci.yml),
[CD](../../.github/workflows/cd.yml), [Blueprint](../../render.yaml),
[Deployment-Runbook](../../DEPLOYMENT.md),
[Scan-Schwelle und Grenzen](../../MONITORING.md),
[Architekturübersicht](../architektur.md).
