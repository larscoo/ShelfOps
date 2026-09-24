# Woche 4: PostgreSQL und Compose

Lokal geprüft am 24.09.2026 auf macOS ARM64. Diese Prüfung bezieht sich auf den
Arbeitsstand des Branches `feature/postgres-compose`, noch nicht auf einen CI-Lauf.

## Automatisierte Prüfungen

| Prüfung | Tatsächliches Ergebnis |
|---|---|
| `make cov` | 209 bestanden, 3 übersprungen; 98,37 % Gesamt-Coverage |
| `make lint` | Ruff und Formatprüfung erfolgreich |
| `make build` | Wheel und Quelldistribution erfolgreich |
| Paketinhalt | PostgreSQL-Modul im Wheel; Testskript und Compose-Dateien im sdist |

Die fachlichen Tests werden gegen In-Memory und PostgreSQL 16 ausgeführt.
Die drei übersprungenen Fälle sind PostgreSQL-spezifische Prüfungen in der
In-Memory-Parametrisierung; die PostgreSQL-Varianten wurden erfolgreich ausgeführt.
Geprüft wurden auch konkurrierende Ausleihen, wiederholte Rückgaben,
Fälligkeitsgrenzen, Fremdschlüssel und der eindeutige Index gegen doppelte aktive
Ausleihen. Der Teststack verwendet ein eigenes Projekt, einen freien lokalen
Port und `tmpfs`; er wird nach dem Test entfernt.

## Compose-Prüfung mit persistentem Volume

Ein isoliertes Prüfprojekt verhinderte Konflikte mit dem vorhandenen Einzelcontainer:

```sh
WEB_PORT=18000 docker compose --env-file .env.example -p shelfops-compose-check up -d --build --wait
```

- `db` wurde gesund, bevor `web` startete.
- Die Anwendung lief mit zwei Gunicorn-Workern und gemeinsamem Datenbestand.
- Über HTTP wurden Buch, Mitglied, Exemplar, Ausleihe, Rückgabe und erneute
  Ausleihe angelegt. Ein Doppel-Ausleihversuch lieferte HTTP 409.
- Die vollständigen Antworten von `/books`, `/members`, `/copies` und `/loans`
  wurden als Vergleichsstand gespeichert.

```sh
WEB_PORT=18000 docker compose --env-file .env.example -p shelfops-compose-check down
WEB_PORT=18000 docker compose --env-file .env.example -p shelfops-compose-check up -d --wait
```

Danach stimmten alle vier Listen einschliesslich IDs, Zeitstempeln und Historie
mit dem Vergleichsstand überein, bei fünf wiederholten Abfragen jeder Liste.
Das Volume `shelfops-compose-check_db-data` blieb beim regulären `down` erhalten.

## Ausfall und Wiederherstellung

```sh
WEB_PORT=18000 docker compose --env-file .env.example -p shelfops-compose-check stop db
```

| HTTP-Anfrage | Datenbank gestoppt |
|---|---|
| `GET /health` | 200, `{"status":"ok"}` |
| `GET /ready` | 503, `{"status":"not_ready"}` |
| `GET /books` | 503, generische Fehlermeldung ohne Zugangsdaten |

Nach `up -d --wait db` lieferte `/ready` wieder 200. Ohne Neustart der
Web-Anwendung entsprachen alle vier Listen weiterhin dem gespeicherten Stand.

Zur eigenen Wiederholung mit eigenen Demodaten stehen die Schritte im
[README](../../README.md#schnellstart-mit-compose-woche-4). Die manuelle Sichtprüfung
der GUI übernimmt der Projektverantwortliche vor dem Merge.
