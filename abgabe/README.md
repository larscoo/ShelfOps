# Woche 04: Nachweise für ShelfOps

Diese Abgabe überträgt die Hausaufgabe auf die Bibliotheksverwaltung.
Die Kursaufgabe verlangt wörtlich Taskboard, `/api/tasks/stats` und die Tags
`taskboard:local` / `taskboard:naiv`. Hier verwenden wir ausdrücklich
`/copies/stats` und `shelfops:local` / `shelfops:naiv`.
Die Anerkennung dieser Übertragung durch die Kursleitung ist noch nicht bestätigt;
dies ist kein Nachweis für die unveränderte Taskboard-Aufgabe.

## Ergebnisse vom 24.09.2026

- Beide Dockerfiles erfolgreich gebaut, Plattform linux/arm64.
- [Image-Grössen und IDs](docker-images.txt): 187 MB optimiert, 1,17 GB naiv.
- [Begründung](BEGRUENDUNG.md): Optimierungen und gemessene Grössen.
- [Echte HTTP-Antwort](stats-nachweis.txt): HTTP 200; zwei Exemplare,
  eines verfügbar, eines ausgeliehen, keines überfällig.
- Separater Compose-Stack `shelfops-week04-proof` mit PostgreSQL 16 und
  Host-Port 18001; beide Dienste healthy, Web-Benutzer `appuser`.
  Der bestehende Stack auf Port 8000 wurde nicht verändert.
- `make cov`: 213 bestanden, 3 übersprungen, Coverage 98,41 %.
  Die drei PostgreSQL-spezifischen Tests werden nur für die In-Memory-Variante
  übersprungen. Die PostgreSQL-Variante wurde ausgeführt.
- `make lint`: erfolgreich, 21 Dateien korrekt formatiert.

## Statistik reproduzieren

Die folgenden Befehle setzen einen **neuen, leeren** Nachweis-Stack voraus
(IDs beginnen bei 1). Port 18001 muss frei sein. Die Beispielumgebung enthält
ausschliesslich lokale Demowerte.

```sh
WEB_PORT=18001 docker compose --env-file .env.example -p shelfops-week04-proof up --build --wait
curl --fail -sS http://127.0.0.1:18001/books -H 'Content-Type: application/json' -d '{"title":"Docker-Nachweis","author":"ShelfOps"}'
curl --fail -sS http://127.0.0.1:18001/copies -H 'Content-Type: application/json' -d '{"book_id":1}'
curl --fail -sS http://127.0.0.1:18001/copies -H 'Content-Type: application/json' -d '{"book_id":1}'
curl --fail -sS http://127.0.0.1:18001/members -H 'Content-Type: application/json' -d '{"name":"Testmitglied"}'
curl --fail -sS http://127.0.0.1:18001/loans -H 'Content-Type: application/json' -d '{"copy_id":1,"member_id":1}'
curl --fail -sS -i http://127.0.0.1:18001/copies/stats
```

Erwarteter Body: `{"available":1,"on_loan":1,"overdue":0,"total":2}`.
`on_loan` zählt nur noch nicht überfällige Ausleihen; überfällige Exemplare stehen
separat in `overdue`. Die drei Kategorien ergeben zusammen `total`.

Nach dem Nachweis ausschliesslich diesen Teststack samt Testdaten entfernen:

```sh
WEB_PORT=18001 docker compose --env-file .env.example -p shelfops-week04-proof down -v
```

## Grössenvergleich und Screenshot

```sh
docker build -t shelfops:local .
docker build -f Dockerfile.naiv -t shelfops:naiv .
docker image ls shelfops
```

Der [Screenshot](docker-images.png) wurde am 24.09.2026 um 15:55 Uhr manuell
aufgenommen und geprüft. Beide Tags, Image-IDs und Grössen sind sichtbar und
stimmen mit `docker-images.txt` überein. Spätere Builds können wegen
veränderlicher Basisimages und Abhängigkeiten andere Grössen ergeben.
