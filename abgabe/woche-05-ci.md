# Woche 05: Lint-Gate und Rot-Grün-Nachweis

## Stand

Die Pipeline ist auf GitHub erfolgreich gelaufen und die Pflichtchecks sind
aktiv. Im Demo-PR ist der rote Lint-Check samt Merge-Sperre nachgewiesen.
Nach Entfernen des absichtlichen Imports sind im selben PR alle drei Checks
erfolgreich; der Merge ist freigegeben. Beide Zustände sind per Screenshot belegt.
Die Hausaufgabe wird auf ShelfOps im Repository-Wurzelverzeichnis übertragen.
Wir testen Python 3.12 entsprechend `requires-python`; die Python-3.11-Matrix aus
dem separaten Labor ist damit noch nicht erledigt.

- [x] Workflow mit getrennten Schritten für Ruff-Lint und Formatprüfung erstellt.
- [x] `build` hängt über `needs: [lint, test]` von beiden Prüfungen ab.
- [x] Tests für In-Memory und PostgreSQL mit Coverage-Gate konfiguriert.
- [x] CI-Badge im README verlinkt.
- [x] Erster vollständiger GitHub-Lauf erfolgreich.
- [x] Pflichtchecks für `main` eingerichtet und geprüft.
- [x] Demo-PR mit rotem Lint-Check und gesperrtem Merge dokumentiert.
- [x] Derselbe PR nach Reparatur grün und mergebar dokumentiert.
- [ ] Screenshots im Repository und im PR verlinkt.
- [ ] PR bei grüner CI gemergt; anschliessender Lauf auf `main` grün.

## 1. Pipeline veröffentlichen

Lokale Vorprüfung dieses Stands:

- Ruff-Lint und Formatprüfung erfolgreich.
- YAML eingelesen; Shell-Syntax und `git diff --check` ohne Fehler.
- CI-Testbefehl: 213 bestanden, 3 übersprungen, Coverage 98,41 %;
  `coverage.xml` erzeugt. Die drei übersprungenen Fälle betreffen
  PostgreSQL-spezifische Tests in der In-Memory-Parametrisierung.
- `docker build -t shelfops:ci .` erfolgreich.
- `sh scripts/smoke-test-image.sh shelfops:ci` erfolgreich: Nicht-root-Benutzer
  und `/health` erreichbar; der temporäre Container wurde entfernt.

Die Action-Versionen wurden anhand der offiziellen Dokumentation und
veröffentlichten GitHub-Tags geprüft:
[checkout](https://github.com/actions/checkout),
[setup-python](https://github.com/actions/setup-python),
[upload-artifact](https://github.com/actions/upload-artifact).

Branch `feature/ci-pipeline` committen, pushen und einen PR gegen `main` öffnen.
Der Push auf den Feature-Branch allein löst bei dieser Konfiguration keinen
Lauf aus; das Öffnen und Aktualisieren des PRs schon. Erst bei erfolgreichen
Checks weitermachen.

## 2. Bestehenden Schutz ergänzen

Unter GitHub **Settings → Branches** die vorhandene Regel für `main` bearbeiten.
Die PR-Pflicht und vorhandenen Schutzoptionen beibehalten. Zusätzlich
**Require status checks to pass before merging** aktivieren und auswählen:

- `Lint gate (ruff)`
- `Test (Python 3.12)`
- `Build image`

**Require branches to be up to date before merging** aktivieren.
Checks sind erst nach einem Lauf auswählbar. Keine Bypass-Ausnahme für den
eigenen Benutzer verwenden. Den Pipeline-PR nach erfolgreicher Prüfung mergen.

## 3. Rot-Grün-PR

Vom aktuellen `main` den Branch `demo/lint-gate` erstellen. In `app/routes.py`
absichtlich einen ungenutzten Import `import os` ergänzen. Mit einer klaren
Demo-Commit-Message committen, pushen und einen PR öffnen. Den Fehler erst
beheben, wenn der rote Lauf und die blockierte Merge-Möglichkeit gesichert sind.

Screenshot `abgabe/cools-ci-rot.png`: fehlgeschlagener Pflichtcheck und gesperrter
Merge sichtbar. Der Build-Job muss wegen des roten Lint-Jobs übersprungen werden.

Den Import wieder entfernen, lokal `make lint` ausführen, Fix committen und auf
denselben PR-Branch pushen. `make fmt` allein entfernt bei ShelfOps keine
ungenutzten Imports. Nach allen grünen Checks Screenshot
`abgabe/cools-ci-gruen.png` mit freigegebener Merge-Möglichkeit aufnehmen.

Beide Screenshots und die Lauf-Links im Repository dokumentieren und im PR
verlinken. Ein zusätzlicher Commit für die Nachweise löst erneut CI aus;
vor dem Merge auch dessen vollständigen grünen Lauf abwarten.

## Belege (nach Durchführung ergänzen)

- Pipeline-PR: [#9](https://github.com/larscoo/ShelfOps/pull/9), grün gemergt.
- Erster grüner Lauf auf `main`: [36026595602](https://github.com/larscoo/ShelfOps/actions/runs/36026595602).
- Demo-PR: [#10](https://github.com/larscoo/ShelfOps/pull/10).
- Roter Lauf: [36027305862](https://github.com/larscoo/ShelfOps/actions/runs/36027305862),
  Commit `72cffeac5ae958aa1f905e3f3b7575f1c8f8764d`.
  Lint fehlgeschlagen, Tests erfolgreich, Build übersprungen;
  GitHub meldet `mergeStateStatus: BLOCKED`.
- [Screenshot: roter Pflichtcheck und gesperrter Merge](cools-ci-rot.png), visuell geprüft.
- Grüner Lauf: [36027887756](https://github.com/larscoo/ShelfOps/actions/runs/36027887756),
  Commit `1365b1b6aec95872aeae5f8ed785598e20a8c83a`.
  Alle drei Pflichtchecks erfolgreich; GitHub meldet `mergeStateStatus: CLEAN`.
- [Screenshot: grüne Pflichtchecks und freigegebener Merge](cools-ci-gruen.png), visuell geprüft.
- Grüner Lauf auf `main`: ausstehend

Die Quellen-/KI-Datei wird wie vereinbart manuell vom Projektverantwortlichen gepflegt.
