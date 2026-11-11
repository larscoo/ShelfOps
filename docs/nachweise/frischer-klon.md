# Startprüfung aus einem frischen Klon

Datum: 11.11.2026. Ausgeführt durch Codex im Auftrag des Projektverantwortlichen.
Geprüfter Quellstand: `cbe0cbbc44d967ff75b703254aee1d6ac7753a43` auf `main`.

## Ziel und Testumgebung

Praktische Prüfung des [Compose-Schnellstarts im README](../../README.md#schnellstart-mit-compose-woche-4)
und der dort beschriebenen Persistenz. Das öffentliche Repository wurde neu nach
`/private/tmp/shelfops-freshclone.NGvSmy/ShelfOps` geklont. Eine bestehende lokale
`.env`, virtuelle Python-Umgebung oder Anwendungsdatenbank wurde nicht übernommen.
Die neue `.env` entstand ausschliesslich aus der versionierten `.env.example`.

Werkzeuge: Git 2.54.0, Docker Engine 29.9.2, Docker Compose v5.6.1,
Docker Desktop auf macOS; App-Image für `linux/arm64`.
Docker Desktop wurde vor dem Test gestartet. Der Rechner und der Docker-Cache
waren nicht neu eingerichtet. Dies ist ein Test eines frischen Arbeitsklons
mit neuer Datenbank, kein Test der Installation sämtlicher Werkzeuge auf einem
leeren Rechner und kein unabhängiger Test durch eine kursfremde Person.

## Durchführung

Der Klon wurde von GitHub bezogen, nicht aus dem bestehenden lokalen Checkout:

```sh
git clone https://github.com/larscoo/ShelfOps.git /private/tmp/shelfops-freshclone.NGvSmy/ShelfOps
cd /private/tmp/shelfops-freshclone.NGvSmy/ShelfOps
cp .env.example .env
docker compose config --quiet
docker compose -p shelfops-freshclone-ngvsmy up --build -d --wait
```

Einzige Anpassung gegenüber dem normalen README-Start: der explizite
Compose-Projektname `shelfops-freshclone-ngvsmy`. Damit wurden eigene
Container, Netzwerk und ein neues Volume angelegt, ohne vorhandene Daten
anderer ShelfOps-Stacks wiederzuverwenden. Die veröffentlichte Adresse blieb
`http://localhost:8000`; Anwendungscode und Compose-Konfiguration blieben
unverändert. Vor dem Start liefen keine Docker-Container.

Der Build und das Warten auf die Healthchecks endeten mit Exit-Code 0.
Das Build-Log meldete 20 aktualisierte Debian-Pakete, darunter `zlib1g` in
Version `1:1.3.dfsg+really1.3.1-1+deb13u1`.
Image-ID des erzeugten App-Images:
`sha256:a35692a7257499f1b42feb6af71528608e84679ccd0a9e265eb90d8f7dd97a07`.

## Ergebnisse des Erststarts

| Prüfung | Tatsächliches Ergebnis |
| --- | --- |
| Compose-Konfiguration | `config --quiet` erfolgreich |
| Build und Start | `up --build -d --wait` erfolgreich |
| Dienste | `web` und `db` laufen und sind healthy |
| Benutzer im Webcontainer | `appuser` |
| `GET /health` | HTTP 200, siehe JSON unten |
| `GET /ready` | HTTP 200, `{"status":"ready"}` |
| `GET /` | HTTP 200, Antwort nicht leer |
| JavaScript `/static/catalog.js` | HTTP 200, Antwort nicht leer |
| CSS `/static/style.css` | HTTP 200, Antwort nicht leer |
| `GET /metrics` | HTTP 200, Antwort nicht leer |
| Fachlicher Smoke-Test | `SMOKE TEST PASSED`, Exit-Code 0 |

Health-Antwort:

```json
{"commit":"unknown","status":"ok","version":"0.1.0"}
```

`0.1.0` und `unknown` sind die erwarteten App-Standardwerte im normalen
Compose-Stack ohne gesetzte Versions-/Commit-Variablen. Der separate
Monitoring-Stack und Render setzen andere Werte.

Fachtest mit dem versionierten Skript:

```sh
bash scripts/smoke-test.sh http://localhost:8000
```

Der Test prüfte Health und Readiness, legte Buch, Exemplar und Mitglied an,
las diese über die API, lieh das Exemplar aus und gab es wieder zurück.
Die neu erzeugten IDs waren jeweils 1. Am Ende meldete das Skript:

```text
returned loan=1; copy=1 is available again.
SMOKE TEST PASSED
```

## Persistenzprüfung

Nach dem erfolgreichen Smoke-Test wurde die Buchliste als Vergleich gesichert.
Anschliessend wurden die Container entfernt und neu erstellt, das Volume
aber beibehalten:

```sh
docker compose -p shelfops-freshclone-ngvsmy down
docker compose -p shelfops-freshclone-ngvsmy up -d --wait
```

Beide Befehle waren erfolgreich. Nach dem Neustart entsprach die Buchliste
exakt der zuvor gesicherten Antwort. Ausserdem waren das eine Exemplar,
das eine Mitglied und die eine Ausleihe vorhanden. Das Exemplar hatte den
Status `available`, die Ausleihe einen gesetzten Rückgabezeitpunkt.
`/ready` meldete erneut `ready`. Damit ist die Datenhaltung über das
benannte Volume für diesen Testlauf bestätigt.

## Aufräumen und Grenzen

Nach Abschluss ausschliesslich das isolierte Testprojekt entfernen:

```sh
docker compose -p shelfops-freshclone-ngvsmy down -v --rmi local
```

Container, Netzwerk, Testdaten-Volume und das erzeugte App-Image wurden
entfernt. Die anschliessenden projektbezogenen Abfragen zeigten keine
verbliebenen Container, Volumes oder Netzwerke. Der temporäre Klon blieb
als Arbeitskopie erhalten. Docker Desktop wurde nicht wieder beendet.

Es waren keine Korrekturen an Code oder Startkonfiguration nötig.
Geprüft wurden der lokale Compose-Pfad, API-Funktionen und Persistenz.
Eine manuelle Browserbedienung, der vollständige Monitoring-Stack sowie
Render- und Kubernetes-Neuaufbau waren nicht Teil dieses Tests.
