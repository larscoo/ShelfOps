# Deployment-Runbook – ShelfOps

Stand: 04.10.2026. ShelfOps verwaltet Bücher, Exemplare, Mitglieder und Ausleihen.
Dieses Dokument erklärt Einrichtung, Prüfung, laufende Deployments und Rollback.
Die öffentliche Kursinstanz verwendet flüchtigen In-Memory-Speicher und einen
Gunicorn-Worker. Jeder Neustart kann ihre Daten löschen. Nur Demodaten verwenden.

**Verbindliches Ziel:** https://shelfops.onrender.com,
Service `srv-db19pnid0e5s73ep7isg`, Blueprint `exs-db19pf942hec73emj8rg`.
Hook und `APP_URL` sind für diesen neuen Dienst abgeglichen. Bei einer Neuanlage ändern sich Service-ID und Hook, auch wenn die URL gleich bleibt. 
Deshalb das GitHub-Secret immer neu zuordnen.

## A. Voraussetzungen

- GitHub-Konto: zum Lesen genügt Zugriff auf das öffentliche Repository
  https://github.com/larscoo/ShelfOps. Für Änderungen braucht es Schreibrechte,
  für Actions-Secrets und Einstellungen entsprechende Verwaltungsrechte.
- Render-Konto mit Zugriff auf den Zielservice und Berechtigung zum Deployen.
  Für einen eigenen Nachbau zuerst einen GitHub-Fork erstellen und diesen mit
  Render verbinden. Die bestehende Kursinstanz nicht nochmals anlegen.
- macOS oder Linux mit Terminal: Python **3.12**, Git 2.x, Bash ab 3.2 und curl.
  Für PostgreSQL-Tests und lokale Container zusätzlich Docker mit Compose.
  GitHub CLI ist für die Anleitung optional; das Dashboard genügt.

Versionen prüfen (Ausgaben des Entwicklungsrechners in Klammern):

```sh
git --version             # 2.54.0
python3.12 --version      # 3.12.x; Projektumgebung: 3.12.14
bash --version            # 3.2.57
curl --version            # 8.7.1
make --version            # GNU Make 3.81
docker --version          # 29.8.0, nur für lokale Container nötig
docker compose version    # 5.5.1
docker info               # muss einen laufenden Server erreichen
```

Fehlende Werkzeuge vor Abschnitt B installieren: Python 3.12 über
[python.org](https://www.python.org/downloads/), Git über
[git-scm.com](https://git-scm.com/downloads), Docker Desktop über
[docker.com](https://www.docker.com/products/docker-desktop/).
Unter macOS bringt `xcode-select --install` Git und Make mit; für Python 3.12
die passende Version auswählen. Docker Desktop nach der Installation starten.

Render bietet Free-Web-Services an, mit Inaktivitätsabschaltung und begrenztem
Kontingent. Für diesen Ablauf ausschliesslich **Free** wählen, falls nicht
angeboten, Einrichtung abbrechen und mit dem Service-Owner klären. Eine
Cloud-Datenbank oder ein kostenpflichtiger Plan gehört nicht zu dieser Anleitung.
[Aktuelle Free-Tier-Grenzen](https://render.com/docs/free).

## B. Lokale Installation

In einem neuen Arbeitsverzeichnis ausführen. Bei einem Fork dessen HTTPS-URL
aus GitHub → Code verwenden. Der Klon benötigt keine SSH-Key-Konfiguration.

```sh
git clone https://github.com/larscoo/ShelfOps.git
cd ShelfOps
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install '.[dev]'
unset DATABASE_URL APP_VERSION RENDER_GIT_COMMIT
python -m flask --app wsgi run --host 127.0.0.1 --port 8000
```

Das Terminal bleibt offen. Erwartet: `Running on http://127.0.0.1:8000`.
Im Browser dieselbe Adresse öffnen. In einem zweiten Terminal:

```sh
curl --fail --silent --show-error http://127.0.0.1:8000/health
curl --fail --silent --show-error http://127.0.0.1:8000/ready
```

Erwartete JSON-Inhalte (Schlüsselreihenfolge unerheblich):

```json
{"status":"ok","version":"0.1.0","commit":"unknown"}
{"status":"ready"}
```

Der Entwicklungsserver wird mit Ctrl+C beendet. Er wird nicht für Render
verwendet; dort startet das Dockerfile Gunicorn. Für den lokalen Fachtest in
einem zweiten Terminal in das geklonte Verzeichnis wechseln:

```sh
source .venv/bin/activate
bash scripts/smoke-test.sh http://127.0.0.1:8000
```

Erwartet: fünf erfolgreiche Schritte und `SMOKE TEST PASSED`.
Für Codeänderungen zusätzlich `make lint` und, bei laufendem Docker, `make cov`.
Letzteres erzeugt eine separate temporäre PostgreSQL-16-Testdatenbank.

Optional lokal mit persistenter Datenbank: Server vorher beenden, bei der ersten
Einrichtung `cp .env.example .env`, dann `docker compose up --build -d`.
Die vorhandene `.env` niemals unbesehen überschreiben. Erwartet sind die Dienste
`web` und `db`; `docker compose ps` zeigt nach dem Start gesunde Container.
Mit `docker compose down` beenden. **Ohne `-v` bleiben die Daten erhalten.**

## C. Konfigurationsvariablen

### Anwendung und Plattform

| Name | Standardwert | Geheim | Wirkung / Ablage |
|---|---|---|---|
| `DATABASE_URL` | nicht gesetzt | ja | PostgreSQL-Verbindungsstring. Ohne Wert: In-Memory. Render: Environment; lokal nur geschützte Umgebung, nicht Git. Keine Verbindung führt zu 503, nicht zu stiller In-Memory-Nutzung. |
| `APP_VERSION` | `0.1.0` | nein | Versionslabel in `/health`; auf Render `1.0.0`. Kein verlässlicher Commit-Nachweis allein. |
| `RENDER_GIT_COMMIT` | lokal nicht gesetzt; Anzeige `unknown` | nein | Von Render gesetzte Commit-SHA; wird als `commit` in `/health` ausgegeben. Nicht manuell überschreiben. |
| `LOG_LEVEL` | nicht ausgewertet | nein | Variable aus der Kursvorlage, in ShelfOps ohne Wirkung. Gunicorn verwendet seine Standard-Logstufe; Access-/Error-Logs gehen auf stdout/stderr. |
| `PORT` | Anwendung fest `8000`; Render üblicherweise `10000` | nein | Auf Render auf `8000` setzen. Die App liest die Variable nicht dynamisch; der Docker-Start bindet fest an 8000. |
| `GUNICORN_WORKERS` | Docker: `1`; Compose: `2` | nein | Anzahl Gunicorn-Prozesse. Ohne gemeinsame Datenbank zwingend `1`; der Flask-Entwicklungsserver nutzt diese Einstellung nicht. |
| `PYTHONDONTWRITEBYTECODE` | Docker: `1` | nein | Verhindert Python-Bytecode-Dateien im Container. |
| `PYTHONUNBUFFERED` | Docker: `1` | nein | Python-Ausgaben ohne Pufferung. |

### Lokales Compose, Prüfskripte und GitHub Actions

| Name | Standardwert | Geheim | Wirkung / Ablage |
|---|---|---|---|
| `POSTGRES_USER` | `shelfops` | nein | Lokaler Compose-Datenbankbenutzer. |
| `POSTGRES_DB` | `shelfops` | nein | Lokaler Compose-Datenbankname. |
| `POSTGRES_PASSWORD` | kein Compose-Standard; lokales Beispiel in `.env.example` | ja, bei echten Zugangsdaten | Für Compose erforderlich, lokal in `.env`; das Beispiel ist kein Produktionspasswort. |
| `WEB_PORT` | `8000` | nein | Nur der lokale veröffentlichte Compose-Port. |
| `TEST_DATABASE_URL` | nicht gesetzt | ja bei externer DB | Testskript setzt eine temporäre Test-DSN selbst. Ohne Variable werden PostgreSQL-Tests übersprungen; deshalb `make cov` verwenden. |
| `PYTHON` | Make: `.venv/bin/python`; Smoke-Test: `python3` | nein | Python-Interpreter; bei Bedarf als Pfad überschreiben. |
| `HEALTH_RETRIES` | manuell `12`; CD `18` | nein | Anzahl Health-/Commit-Prüfungen im Smoke-Test. |
| `BACKOFF_SECONDS` | manuell `5`; CD `3` | nein | Linear wachsende Wartezeit zwischen Versuchen. |
| `EXPECTED_COMMIT` | leer | nein | Vollständige SHA für den Smoke-Test; CD setzt den geprüften Commit. |
| `APP_URL` | keiner | nein | GitHub Actions **Variable**, öffentliche Basis-URL ohne `/health`, Query oder Anmeldedaten. |
| `RENDER_DEPLOY_HOOK` | keiner | ja | GitHub Actions **Secret**, vollständige Hook-URL aus genau dem Zielservice. |
| `DEPLOY_SHA` | im CD-Workflow aus dem Ereignis | nein | Zu deployender, durch CI geprüfter Commit. Nicht als Repository-Variable pflegen. |
| `GH_TOKEN` | im Workflow aus `github.token` | ja | Kurzlebiger GitHub-Token für lesende CI-/Commit-Abfragen; kein eigener PAT erforderlich. |
| `GITHUB_REPOSITORY`, `RUNNER_TEMP` | von GitHub gesetzt | nein | Repositorykennung und temporärer Arbeitsordner im Workflow. |

`.env` ist ignoriert. Die Anwendung lädt diese Datei nicht automatisch;
Compose liest sie für seine Variablenersetzung. Echte Secrets ausschliesslich in
GitHub Secrets oder Render Environment hinterlegen. Keine Hook-URLs im PR,
Screenshot, Terminal-Log oder Runbook speichern; auch nicht mit `curl -v` ausgeben.

## D. Deployment – Blueprint als Hauptpfad

### Einmalige Einrichtung eines eigenen Dienstes

Wer nur den bestehenden ShelfOps-Service betreibt, überspringt die Neuanlage.
Der bestehende Blueprint-Service wird nicht parallel nochmals angelegt.

1. GitHub-Konto und bei Bedarf Fork erstellen. Im Fork unter **Actions** die
   Workflows aktivieren. Die drei CI-Jobs müssen erfolgreich laufen.
2. Auf https://render.com anmelden, **New + → Blueprint** wählen, GitHub
   verbinden und der Render-App Zugriff nur auf das gewünschte Repository geben.
3. Das Repository, Branch `main` und Blueprint-Datei `render.yaml` auswählen.
   Einen Blueprint-Namen vergeben (bei der Kursinstanz `Default`).
   Die Vorschau aus der versionierten Datei mit folgenden Werten vergleichen:

   | Feld | Wert |
   |---|---|
   | Name | `shelfops` (die öffentliche URL kann einen Zusatz erhalten) |
   | Runtime | Docker |
   | Branch | main |
   | Region | Frankfurt |
   | Root Directory | leer lassen: Repository-Wurzelverzeichnis |
   | Dockerfile Path | `./Dockerfile` |
   | Docker Build Context | `.` |
   | Instance Type | Free |
   | Health Check Path | `/health` |
   | Auto-Deploy | Off; spätere Deploys kommen aus GitHub Actions |

4. Die Datei setzt `PORT=8000`, `GUNICORN_WORKERS=1` und
   `APP_VERSION=1.0.0`. `DATABASE_URL` für diese Demo weglassen.
   Kein eigenes Startkommando setzen: Das Dockerfile startet Gunicorn.
5. Die Blueprint-Vorschau mit **Deploy Blueprint / Apply** bestätigen.
   Der erste Sync erstellt den Service. Unter Resources den Service öffnen,
   unter Events/Deploys auf **Live** warten.
   Die tatsächlich angezeigte öffentliche URL kopieren; nicht aus dem Namen
   ableiten. Abschnitt E ausführen.
6. Aus **Settings → Deploy Hook** genau dieses Service die Hook-URL kopieren.
   In GitHub **Settings → Secrets and variables → Actions → Secrets** als
   `RENDER_DEPLOY_HOOK` speichern. Im Tab **Variables** `APP_URL` auf die
   öffentliche URL desselben Service setzen. Ein abschliessendes `/` ist erlaubt.
7. Schutzregel für `main` mit PR-Pflicht und den Pflichtchecks
   `Lint gate (ruff)`, `Test (Python 3.12)` und `Build image` einrichten.
   Branch muss aktuell sein; keine direkten Pushes auf `main`.

Keinen zweiten Web-Service über **New + → Web Service** anlegen.
Dauerhafte Konfigurationsänderungen erfolgen über `render.yaml` und einen PR.
Ein Blueprint-Sync kann Konfigurationsänderungen selbst anwenden; während einer
Rollback-Übung deshalb auch keine Blueprint-Änderungen mergen oder syncen.

### Wiederkehrendes Deployment

1. Feature-Branch erstellen, Änderungen committen und pushen, PR öffnen.
2. Alle CI-Checks abwarten, Diff selbst prüfen, dann PR mergen.
3. Nach dem Push-CI-Lauf auf `main` startet automatisch **CD**.
4. CD prüft, dass der Commit noch `main` entspricht und dessen CI erfolgreich
   war. Der Hook erhält genau diese SHA. Danach folgt Abschnitt E.

Manueller Neustart der Auslieferung: **GitHub → Actions → CD → Run workflow**,
Branch **main** wählen. Auch dieser Weg verlangt grüne Push-CI für dieselbe SHA.
Er ist kein Rollback-Weg, weil ältere Commits bewusst abgelehnt werden.
Ein manueller erster Render-Deploy und spätere Deploys laufen nicht parallel.

## E. Verifikation

Die URL immer aus dem ausgewählten Service kopieren. Einmal interaktiv setzen:

```sh
printf 'Öffentliche Render-Basis-URL: '
read -r APP_URL
export APP_URL
curl --fail --silent --show-error --max-time 90 "$APP_URL/health"
curl --fail --silent --show-error --max-time 90 "$APP_URL/ready"
```

Erwartet: HTTP-Erfolg, `status: ok`, `version: 1.0.0` und die vollständige SHA
des Deploys; Readiness `{"status":"ready"}`. Nach einem Cold Start bei Timeout
den Aufruf wiederholen oder den Smoke-Test mit seinen Wiederholungen nutzen.
Mit curl `-i` werden die HTTP-Header einschliesslich Statuscode angezeigt.

```sh
printf 'Erwartete vollständige Commit-SHA aus Render/GitHub: '
read -r EXPECTED_COMMIT
export EXPECTED_COMMIT
bash scripts/smoke-test.sh "$APP_URL"
unset EXPECTED_COMMIT
```

Erwartet sind fünf erfolgreiche Schritte und **SMOKE TEST PASSED**. Der Test
legt ein Buch, Exemplar und Mitglied an, leiht aus und gibt zurück. Datensätze
bleiben bestehen; ein fehlgeschlagener Lauf kann eine offene Ausleihe hinterlassen.
Der Versionscheck prüft Codeidentität, nicht die Fertigstellung eines erneuten
Deploys desselben Commits. Deshalb zusätzlich unter Render **Events/Deploys**
prüfen: konkreter Deploy **Live**, passende SHA und **Triggered via Deploy Hook**.

Im GitHub-CD-Log: **Trigger Render deploy for the tested commit** muss HTTP 200
mit Deploy-ID oder HTTP 202 (eingereiht) melden. **Wait for expected commit and
smoke-test the service** endet mit `SMOKE TEST PASSED`. HTTP 202 allein ist kein
Abschlussnachweis. Der Job hat ein Zeitlimit von 25 Minuten.

Im Render-Log: Multi-Stage-Build erfolgreich, Gunicorn lauscht auf
`0.0.0.0:8000`, genau ein gestarteter Worker, Service wird Live; Health-Aufrufe
liefern 200. ShelfOps schreibt derzeit keine ausdrückliche In-Memory-Startmeldung.
Eine aktuelle Health-Antwort und sichtbare URL als Screenshot sichern.

## F. Rollback und Rückkehr zum aktuellen Stand

### Vorbereitung

1. Aktuelle URL, Service-ID, Live-Deploy-ID und vollständige Commit-SHA notieren.
   Die URL muss zu Hook und `APP_URL` passen. Aktuelle Daten sind nur Demo-Daten;
   ein Neustart verliert den In-Memory-Zustand. Mit PostgreSQL wäre ein Backup
   und eine Prüfung der Schema-Kompatibilität erforderlich.
2. **GitHub → Actions → CD → … → Disable workflow** wählen und laufende
   Deployments vollständig abwarten. Während des Tests keine PRs mergen.
   Render Auto-Deploy bleibt Off. Das allein stoppt GitHub-Deploy-Hooks nicht.
3. Im richtigen Render-Service **Deploys** (oder Events) einen früheren
   erfolgreichen Deploy eines **anderen** Commits auswählen. SHA und Erfolg
   notieren. Kein Rollback auf denselben Commit als Code-Rückrolltest ausgeben.

### Ausführen und prüfen

4. Beim Zieldeploy **Rollback** wählen, die Vorschau mit der notierten SHA
   vergleichen und **Rollback to this deploy** bestätigen. Render startet einen
   neuen Deploy mit dem früheren Build-Artefakt. Auf **Live** warten.
5. `/health`, `/ready` und Smoke-Test wie in E prüfen, mit der Ziel-SHA als
   `EXPECTED_COMMIT`. Zusätzlich muss Render den Zielcommit als Live anzeigen.
6. **Ausnahme für alte ShelfOps-Versionen:** Vor Commit `8f81b7c` enthält
   `/health` noch keine Commit-/Versionsfelder. Bei einem solchen Ziel liefert
   Health nur `{"status":"ok"}`. Dann `unset EXPECTED_COMMIT`, normalen
   Smoke-Test ausführen und die Codeversion anhand des Live-Deploys in Render
   bestätigen. Diese geringere Prüftiefe ausdrücklich im Protokoll festhalten.

Ist **Rollback** nicht verfügbar, kann das alte Artefakt abgelaufen sein.
Alternativ **Manual Deploy → Deploy a specific commit**, bekannte frühere SHA
eintragen und **Deploy Commit** wählen. Das baut neu und kann wegen veränderter
Abhängigkeiten anders ausfallen als das damalige Artefakt. Danach dieselben
Prüfungen ausführen. [Render: Rollbacks](https://render.com/docs/rollbacks),
[Deploy eines bestimmten Commits](https://render.com/docs/deploys#deploying-a-specific-commit).

### Aktuellen Stand wiederherstellen

7. Bei einer Übung die vorher notierte aktuelle SHA über **Manual Deploy →
   Deploy a specific commit** wieder ausliefern. Live-Status, SHA, Health und
   Smoke-Test mit `EXPECTED_COMMIT` bestätigen. Bei einer echten Störung zuerst
   den Fehler über einen PR beheben, bevor der defekte Stand wieder deployt wird.
8. **Actions → CD → Enable workflow**. Render Auto-Deploy bleibt **Off**, weil
   die Pipeline den Hook bedient. Falls während der Pause neue Commits gemergt
   wurden, deren grüne CI prüfen und CD bewusst für das aktuelle `main` starten.
9. Zeit, alter/neuer Commit, Deploy-IDs, Testergebnisse, Screenshots und
   Wiederaktivierung dokumentieren. Keine Secrets in den Nachweis kopieren.

Ein Rollback ändert weder Git-Historie noch Datenbankinhalte zurück.
Service-Umgebung und Teile der Konfiguration können aus dem Zieldeploy stammen;
deshalb nach dem Rollback Port, Worker und Speicher prüfen. Disks und
Datenbankschema werden nicht automatisch rückgesetzt. Der CD-Workflow kann den
Rollback sonst beim nächsten grünen `main` wieder überschreiben.

**Prüfstatus:** Am 04.10.2026 Rückkehr zu `107598c` durch **Deploy a specific
commit** und anschliessende Wiederherstellung von `8f81b7c` erfolgreich erprobt.
Beide Versionen bestanden den Smoke-Test; CD danach wieder aktiv.
Das Wiederverwenden eines früheren Build-Artefakts über den Rollback-Button
wurde nicht getestet. [Vollständiger Nachweis](abgabe/rollback-nachweis.md).

## G. Troubleshooting

| Symptom | Ursache | Lösung |
|---|---|---|
| `Permission denied (publickey)` beim Push | GitHub-Schlüssel nicht geladen/zugeordnet | Unter macOS `/usr/bin/ssh-add --apple-use-keychain ~/.ssh/github`, falls dies der eingerichtete Schlüssel ist. In `~/.ssh/config` GitHub `IdentityFile`, `AddKeysToAgent yes` und `UseKeychain yes` zuordnen. `ssh -T git@github.com` muss den richtigen Benutzer bestätigen. |
| `GH006`, direkter Push auf main abgelehnt | Branch-Schutz arbeitet korrekt | Feature-Branch pushen, PR öffnen, CI abwarten. Schutz nicht abschalten. Bei lokal abweichender main-Historie zuerst Änderungen sichern und Service-Owner beiziehen. |
| `No open ports detected` / Start hängt | Docker lauscht auf 8000, Konfiguration weicht ab | `PORT=8000`, Docker-Runtime und Startkommando prüfen; keinen abweichenden Startbefehl setzen. |
| Erster Aufruf dauert lange oder Timeout | Free-Service war inaktiv | Smoke-Test mit Wiederholungen nutzen; bei weiterem Fehler Logs/Render-Status prüfen. Nicht jeden Timeout pauschal als Cold Start abtun. |
| Angelegte Datensätze verschwinden zwischen Anfragen | Mehrere Worker bei In-Memory | `GUNICORN_WORKERS=1`; mit mehreren Prozessen gemeinsame PostgreSQL-Datenbank notwendig. |
| `/health` 200, `/ready` 503 | Konfigurierte Datenbank nicht verfügbar | DSN in Render Environment und DB-Verfügbarkeit prüfen; keine Zugangsdaten posten. Ohne DATABASE_URL liefert ShelfOps `/ready` 200. Healthcheck bleibt `/health`. |
| Grüner CD-Lauf, aber falscher Dienst aktualisiert | Hook und APP_URL gehören zu verschiedenen Diensten | Service-ID, tatsächliche URL und Hook im Dashboard abgleichen; APP_URL und Secret gemeinsam korrigieren. Gleiche SHA allein unterscheidet zwei Dienste nicht. |
| CD meldet fehlende/rote CI oder veralteten Commit | Lauf gehört nicht zum aktuellen main oder CI ist unvollständig | Aktuellen Push-CI-Lauf abwarten bzw. reparieren; danach CD auf main erneut starten. |
| Hook HTTP 401 | Secret fehlt, ist falsch oder wurde rotiert | Hook des richtigen Service neu in GitHub Secrets speichern. Wert nie im Chat/Log prüfen. |
| Smoke-Test wartet auf Commit | Alte Version noch aktiv, Deploy fehlgeschlagen oder falsche APP_URL | Deploy-ID/Status/SHA in Render prüfen, URL abgleichen; bei Fehler Logs auswerten. Nicht bloss Timeout erhöhen. |
| Testbücher `smoke-test-…` in der Oberfläche | Erwartete Smoke-Test-Daten; keine Lösch-API | Ausleihen werden bei Erfolg zurückgegeben. Testdaten dokumentieren; kein ungeplanter Neustart zum Aufräumen. |
| Hook-URL im Log veröffentlicht | Secret versehentlich ausgegeben | Im Render-Service Hook regenerieren, GitHub Secret ersetzen, zugängliche Logs prüfen/entfernen und Service-Owner sofort informieren. |

## H. Kontakt und Eskalation

- **Service-Owner und erste Anlaufstelle:** Projektverantwortlicher Lars,
  GitHub `larscoo`. Technische, nicht vertrauliche Probleme als
  [Issue im Projekt](https://github.com/larscoo/ShelfOps/issues) erfassen:
  Uhrzeit mit Zeitzone, URL, Commit, Deploy-/Run-Link, Symptom, bereits geprüfte
  Schritte. Keine Secrets oder personenbezogenen Mitgliederdaten anhängen.
- **Kurs-/Bewertungsfragen:** Kursleitung Norman Süsstrunk über den im Kurs
  vereinbarten FHGR-Kommunikationskanal. Nach 30 Minuten ohne Fortschritt oder
  bei einem Abgabehindernis den Service-Owner und anschliessend die Kursleitung
  beiziehen. Kein garantierter 24/7-Betrieb für dieses Semesterprojekt.
- **Secret-Verlust, unberechtigter Zugriff oder Datenverlust:** sofort privat
  an den Service-Owner, keine öffentliche Issue-Beschreibung mit sensiblen Daten.
  Automatische Deployments bis zur Klärung pausieren.
- **Plattformstörung:** https://status.render.com prüfen; wenn auch andere
  Dienste betroffen sind, Service-Owner informieren und Render-Support über
  den authentifizierten Dashboard-Hilfekanal kontaktieren.
