# Arbeitsweise

ShelfOps ist eine Einzelarbeit im Modul CDS212.

## GitHub Flow

1. Von einem aktuellen `main` einen kurzen, thematisch passenden Branch erstellen.
2. Kleine, zusammengehörige Änderungen entwickeln und lokal prüfen.
3. Den Branch pushen und einen Pull Request mit Was, Warum und Selbstprüfung öffnen.
4. Den eigenen Diff auf GitHub nochmals lesen und die Prüfergebnisse festhalten.
5. Erst nach grünen erforderlichen CI-Prüfungen mergen, danach den Branch löschen.

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

Sobald Anwendung und Werkzeuge eingerichtet sind, gehören diese Prüfungen vor jeden Code-PR (aktuell noch nicht ausführbar):

```sh
ruff check .
ruff format --check .
pytest --cov=app --cov-report=term-missing
```

Die vollständige CI muss zusätzlich das Coverage-Gate von mindestens 80 % und den Docker-Build enthalten, später auch Trivy. 
Nachweise verlinken den konkreten Workflow-Lauf oder dokumentieren Befehl, Datum und tatsächliches Ergebnis.
Nicht ausgeführte Prüfungen werden ausdrücklich als offen bezeichnet.

## GitHub-Einrichtung und erster PR

Der lokale Grundgerüst-Branch ist `docs/project-foundation`.
Branch-Schutz ist eingerichtet, CI-Pflichtprüfungen folgen nach dem ersten Workflow-Lauf.

Zielkonfiguration für `main`: Pull Requests erforderlich, direkte Pushes und Force-Pushes verhindern, Regeln auch für Administratoren anwenden und nach dem
ersten CI-Lauf die tatsächlichen Check-Namen als Pflichtprüfungen hinterlegen.
Für diese Einzelarbeit ist keine fremde Review-Freigabe erforderlich, die schriftliche Selbstprüfung bleibt Pflicht.

Solange die CI fehlt, bleibt der erste PR ein Entwurf. Der Projektstart wird
nicht als vollständig CI-geprüft ausgegeben. Vor dem ersten Merge ist eine
passende CI einzurichten; mindestens fünf spätere PRs müssen die vollständige
Kurs-CI durchlaufen. Konkrete Umsetzung und Nachweise folgen in der CI-Etappe.

## Umfang und Eigenleistung

Neue Funktionen ausserhalb von [docs/umfang.md](docs/umfang.md) zunächst als Vorschlag dokumentieren. 
Entscheidungen mit Alternativen und Konsequenzen in ADRs festhalten, sobald die entsprechenden Architekturentscheidungen getroffen werden. 
Übernahmen aus dem Kurs kennzeichnen und KI-Nutzung fortlaufend dokumentieren.
