# Arbeitsweise

ShelfOps ist eine Einzelarbeit im Modul CDS212.

## GitHub Flow

1. Von einem aktuellen `main` einen kurzen, thematisch passenden Branch erstellen.
2. Kleine, zusammengehörige Änderungen entwickeln und lokal prüfen.
3. Den Branch pushen und einen Pull Request mit Was, Warum und Selbstprüfung öffnen.
4. Den eigenen Diff auf GitHub nochmals lesen und die Prüfergebnisse festhalten.
5. Ab Einführung der CI nur nach grünen Pflichtprüfungen mergen; für den
   Projektstart in Woche 2 gilt die unten dokumentierte Ausnahme. Danach den
   Branch löschen.

`main` soll jederzeit deploybar bleiben. Keine direkten Pushes oder Force-Pushes
auf `main`, keine künstlichen oder rückdatierten Commits. Mindestens fünf
thematisch sinnvolle PRs müssen mit grüner CI zum Merge-Zeitpunkt nachweisbar sein.

Branch-Namen: `feature/…`, `fix/…`, `docs/…`, `chore/…` oder `ci/…`, jeweils mit
englischer Kurzbeschreibung in Kleinbuchstaben und Bindestrichen.

```sh
git switch main
git pull --ff-only
git switch -c feature/book-catalog
```

## Commits

Conventional Commits in Englisch, Imperativ und ohne Schlusspunkt:

```text
docs: define library scope and contribution rules
feat(loans): prevent duplicate active loans
test(loans): cover overdue returns
```

Weitere Typen: `fix`, `refactor`, `chore`, `ci`. Commit-Nachrichten beschreiben
die tatsächliche Änderung. Keine Secrets, lokalen Umgebungen oder IDE-Dateien einchecken.

## Prüfung und Nachweise

Für Dokumentationsänderungen: Inhalte, relative Links und `git diff --check` prüfen.
Tests sind bei reiner Dokumentation nicht nötig, im PR begründen.

Vor jedem Code-PR die lokale Umgebung installieren und diese Prüfungen
ausführen. `make cov` benötigt Docker und prüft beide Speicher mit einer
eigenen kurzlebigen PostgreSQL-Testdatenbank:

```sh
make lint
make cov
```

Die CI führt Lint, Formatprüfung, Tests beider Speicher, das Coverage-Gate
von mindestens 80 %, Docker-Build und Container-Smoke-Test aus. Trivy blockiert
HIGH-/CRITICAL-Funde mit verfügbarem Fix im bestehenden Check `Build image`.
Die [Scan-Schwelle und ihre Grenzen](MONITORING.md) sind dokumentiert.
Nachweise verlinken den konkreten Workflow-Lauf oder dokumentieren Befehl, Datum und tatsächliches Ergebnis.
Nicht ausgeführte Prüfungen werden ausdrücklich als offen bezeichnet.

## Aktueller Branch-Schutz

`main` verlangt Pull Requests und die erfolgreichen Pflichtchecks
`Lint gate (ruff)`, `Test (Python 3.12)` und `Build image`. Der PR-Branch muss
aktuell sein. Die Regeln gelten auch für Administratoren; Force-Pushes und
das Löschen von `main` sind nicht erlaubt. Offene Review-Unterhaltungen
müssen aufgelöst sein. Eine fremde Review-Freigabe ist für diese Einzelarbeit
nicht vorgeschrieben; die schriftliche Selbstprüfung bleibt Pflicht.

Die Konfiguration wurde bei der Abschlussprüfung am 13./14.10.2026
über die GitHub-API überprüft.

## Historischer Projektstart: Woche 2

Der Grundgerüst-Branch war `docs/project-foundation`. Zu diesem Zeitpunkt
war noch keine CI eingerichtet. Die folgende Ausnahme beschreibt nur
den damaligen Projektstart, nicht das aktuelle Merge-Verfahren.

Woche 2 verlangt einen ersten gemergten PR; CI ist Inhalt von Woche 5. Deshalb
kann der Dokumentations-PR nach lokaler Prüfung und persönlicher Selbstprüfung
auf GitHub gemergt werden. In seiner Beschreibung steht ausdrücklich:
„Keine CI vorhanden; Dokumentation lokal geprüft.“ Der PR zählt nicht zu den
mindestens fünf für die Abschlussabnahme benötigten PRs mit grüner CI.

Seit Woche 5 sind die tatsächlichen CI-Checks als Pflichtprüfungen hinterlegt.
Mindestens fünf PRs mit grüner CI vor dem Merge sind in der
[Abnahme-Checkliste](abnahme-checkliste.md) nachgewiesen.

Für den ersten PR verwenden wir „Create a merge commit“, damit die einzeln
geprüften Commits im Verlauf von `main` erhalten bleiben. Nach dem Merge lokal:

```sh
git switch main
git pull --ff-only
git log --oneline --graph --all
```

Ein Merge-Commit ersetzt keinen eigenen fachlichen Arbeits-Commit. Die Historie
wird nicht nachträglich aufgeteilt oder umgeschrieben, um eine Anzahl zu erreichen.

## Umfang und Eigenleistung

Neue Funktionen ausserhalb von [docs/umfang.md](docs/umfang.md) zunächst als Vorschlag dokumentieren.
Entscheidungen mit Alternativen und Konsequenzen in ADRs festhalten, sobald die entsprechenden Architekturentscheidungen getroffen werden.
Übernahmen aus dem Kurs kennzeichnen und KI-Nutzung fortlaufend dokumentieren.
