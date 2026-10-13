# ADR 0001 – PostgreSQL hinter einer Repository-Schnittstelle

## Status

accepted – dokumentiert am 13.10.2026.
Dieses ADR hält die bereits implementierte Entscheidung nachträglich fest.

## Kontext

ShelfOps verwaltet zusammenhängende Bücher, Exemplare, Mitglieder und
Ausleihen. Ein Exemplar darf auch bei parallelen Anfragen nur einmal aktiv
ausgeliehen sein. Der lokale Compose-Betrieb benötigt dauerhafte Daten und
mehrere Worker; ein schneller Start und fachliche Tests sollen zugleich
ohne laufende Datenbank möglich bleiben.

Nur In-Memory-Speicher wäre einfach, verliert aber Daten bei Neustarts und
teilt sie nicht zwischen Prozessen. Eine SQLite-Datei wäre für eine einzelne
Instanz eine kleinere Alternative, erfüllt aber nicht unser gewähltes
Client-Server-Modell mit einem gemeinsamen Datenbankdienst für mehrere
App-Instanzen. Speicherzugriffe unmittelbar in den HTTP-Routen würden
Fachtests und Wechsel des Backends stärker aneinander koppeln.

## Entscheidung

Wir verwenden die Schnittstelle `LibraryRepository` mit zwei Implementierungen:
`InMemoryLibraryRepository` und `PostgresLibraryRepository`. Die Application
Factory wählt bei gesetzter, nicht leerer `DATABASE_URL` PostgreSQL, sonst
In-Memory. Ein Datenbankfehler führt zu einem Fehlerzustand und nicht zu einem
stillen Wechsel auf einen leeren In-Memory-Speicher.

Im persistenten lokalen Betrieb verwenden wir PostgreSQL 16 in Compose mit
benanntem Volume. Die Datenbank sichert Beziehungen und konkurrierende
Ausleihen über Constraints und Transaktionen. Jede Repository-Operation
verwendet eine kurze psycopg-Verbindung. Dieselben fachlichen Tests prüfen
beide Implementierungen; CI stellt dafür eine eigene Testdatenbank bereit.

In-Memory bleibt für den einfachen Start und die aktuelle Render-Demo
erhalten. Dabei ist ein Worker erforderlich. Die Kubernetes-Labor-Pods
verwenden ebenfalls In-Memory und teilen ihren Zustand ausdrücklich nicht.
Dieses ADR behauptet keine bereits eingerichtete PostgreSQL-Datenbank auf
Render oder in Kubernetes.

## Konsequenzen

Positiv:

- HTTP-Routen bleiben weitgehend unabhängig von der Speichertechnik.
- PostgreSQL erhält Daten über App-Neustarts hinweg und koordiniert
  Schreibzugriffe verschiedener Worker.
- Schnelle Tests und lokaler Start funktionieren weiterhin ohne DB;
  Datenbanktests prüfen zusätzlich die tatsächliche SQL-Implementierung.
- `/health` bleibt von DB-Ausfällen unabhängig; `/ready` prüft den
  konfigurierten Speicher und kann dessen Ausfall anzeigen.

Negativ und Grenzen:

- Zwei Implementierungen müssen fachlich gleich bleiben und getestet werden.
- PostgreSQL benötigt Konfiguration, Zugangsdaten und ein eigenes
  Betriebs-, Backup- und Wiederherstellungskonzept.
- Kurze Verbindungen vereinfachen Fehlerbehandlung, kosten aber zusätzlichen
  Verbindungsaufbau; ein Pool ist derzeit nicht implementiert.
- Die initiale Schema-Erstellung ist kein Migrationssystem.
- Die Demos ohne DB verlieren Daten; mehrere Kubernetes-Pods ergeben ohne
  gemeinsame DB keinen konsistenten Bibliotheksbetrieb.

Belege: [Application Factory](../../app/__init__.py),
[Repository-Schnittstelle](../../app/repository.py),
[PostgreSQL-Implementierung](../../app/postgres.py),
[Compose](../../docker-compose.yml),
[Architekturübersicht](../architektur.md).
