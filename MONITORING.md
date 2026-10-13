# Monitoring – ShelfOps

## 1. Dashboard-Dokumentation

Grundlage ist der lokale Laborlauf vom 12.10.2026 mit App-Version
1.0.0, PostgreSQL und einem Gunicorn-Worker.

Die Normalbereiche stammen aus diesem Laborlauf. Sie sind keine
Aussage über die Leistungsgrenzen oder den späteren Produktionsbetrieb.
Die Eingriffsschwellen sind vorgeschlagene Betriebsregeln.

Nachweise:

- [Dashboard-Screenshot](docs/woche-09/dashboard.png)
- [Exportiertes Dashboard](monitoring/grafana/dashboards/shelfops-overview.json)

### Panel: Request-Rate (req/s)

| Feld | Inhalt |
| --- | --- |
| Metrik | `flask_http_request_total` |
| PromQL | `sum(rate(flask_http_request_total{job="shelfops"}[5m]))` |
| Frage | Wie viele HTTP-Anfragen verarbeitet ShelfOps pro Sekunde? |
| Normalbereich | Im Screenshot etwa 2,2–2,3 Requests/s während der Lastphasen; dazwischen nahe 0. Die Abfrage glättet die kurzen Lastphasen über fünf Minuten. |
| Eingriffsschwelle | Bei fortlaufendem, unverändertem Lasttest weniger als 1 Request/s über fünf Minuten untersuchen. Das wäre ein deutlicher Rückgang gegenüber der Beobachtung. Ohne erwarteten Verkehr ist ein Wert nahe 0 allein kein Störungszeichen. |

### Panel: Fehlerrate 5xx (Anteil)

| Feld | Inhalt |
| --- | --- |
| Metrik | `flask_http_request_total` mit dem Label `status` |
| PromQL | `(sum(rate(flask_http_request_total{job="shelfops",status=~"5.."}[5m])) or vector(0)) / sum(rate(flask_http_request_total{job="shelfops"}[5m]))` |
| Frage | Welcher Anteil der verarbeiteten Anfragen endet mit einem Serverfehler? |
| Normalbereich | Im Laborlauf 0 %. Die absichtlich erzeugten HTTP-404-Antworten zählen nicht als 5xx-Fehler. |
| Eingriffsschwelle | Mehr als 5 % über fünf Minuten, entsprechend der vorhandenen Regel `HighErrorRate`. Ein anhaltender Serverfehleranteil beeinträchtigt die Nutzung und erfordert eine Untersuchung. |

### Panel: p95-Latenz (s)

| Feld | Inhalt |
| --- | --- |
| Metrik | `flask_http_request_duration_seconds_bucket` |
| PromQL | `histogram_quantile(0.95, sum by (le) (rate(flask_http_request_duration_seconds_bucket{job="shelfops"}[5m])))` |
| Frage | Unter welcher Antwortzeit liegen ungefähr 95 % der gemessenen Anfragen? |
| Normalbereich | Im Screenshot etwa 5–23 ms, während der Lastphasen ungefähr 23 ms. Die Werte sind aus Histogramm-Buckets geschätzte Quantile. |
| Eingriffsschwelle | p95 über einer Sekunde für fünf Minuten, entsprechend `HighLatencyP95`. Das liegt deutlich über dem beobachteten Bereich und bedeutet spürbar langsamere Antworten. |

### Panel: Version (shelfops_info)

| Feld | Inhalt |
| --- | --- |
| Metrik | `shelfops_info` mit dem Label `version` |
| PromQL | `shelfops_info{job="shelfops"}` |
| Frage | Welche App-Version meldet die überwachte ShelfOps-Instanz? |
| Normalbereich | Im Labor `version="1.0.0"` mit dem Metrikwert 1. Das Panel zeigt das Versionslabel an. |
| Eingriffsschwelle | Bei einer unerwarteten Version nach einem Deployment sofort prüfen, ob das vorgesehene Image läuft. Fehlende Daten nach mehreren Scrape-Intervallen ebenfalls untersuchen. Eine numerische Grössenschwelle ist für dieses Panel nicht sinnvoll. |

### Panel: p95-Latenz – eigenes Panel

| Feld | Inhalt |
| --- | --- |
| Metrik | `flask_http_request_duration_seconds_bucket` |
| PromQL | `histogram_quantile(0.95, sum by (le) (rate(flask_http_request_duration_seconds_bucket{job="shelfops"}[5m])))` |
| Frage | Wie verändert sich die geschätzte p95-Antwortzeit im Verlauf des Lasttests? |
| Normalbereich | Wie im bestehenden p95-Panel etwa 5–23 ms. Das selbst hinzugefügte Panel verwendet dieselbe Abfrage und zeigt daher dieselbe Messgrösse. |
| Eingriffsschwelle | Wie beim bestehenden p95-Panel: über einer Sekunde für fünf Minuten. Eine zusätzliche Alarmierung derselben Messgrösse ist nicht erforderlich. |

Bei fehlendem Verkehr ist die 5xx-Quote wegen eines möglichen Nenners
von 0 nicht aussagekräftig. Fehlende Messdaten dürfen nicht als
Fehlerfreiheit interpretiert werden.

## 2. SLOs mit Error Budget

Die folgenden Ziele sind Vorschläge für ShelfOps über jeweils rollierende
30 Tage. Der kurze Laborlauf belegt noch keine Einhaltung dieser Ziele.
Beide SLOs beziehen sich auf die vom Flask-Exporter erfassten Anfragen
des Jobs `shelfops`, einschliesslich erfasster Healthchecks und Testanfragen.
Sie beschreiben damit den instrumentierten App-Verkehr, nicht ausschliesslich
echte Benutzervorgänge.

### SLO 1 – Anteil der Antworten ohne Serverfehler

- **SLI:** Anteil der erfassten HTTP-Anfragen ohne Statuscode 5xx,
  gemessen mit `flask_http_request_total` und dessen Label `status`.
  4xx-Antworten zählen für dieses ausdrücklich auf Serverfehler begrenzte
  Ziel nicht als Fehler; sie belegen aber auch keinen erfolgreichen
  Geschäftsvorgang.
- **SLO:** Mindestens **99,9 %** der erfassten Anfragen enden innerhalb
  von 30 Tagen ohne 5xx-Antwort.
- **Error Budget:** Höchstens **0,1 %** der erfassten Anfragen dürfen
  mit einem Serverfehler enden.

Berechnung mit `N` als Anzahl erfasster Anfragen im Zeitraum:

```text
Erlaubter Fehleranteil = 1 − 0,999 = 0,001
Error Budget          = 0,001 × N

Rechenbeispiel bei angenommenen 100 000 Anfragen in 30 Tagen:
0,001 × 100 000 = 100 erlaubte 5xx-Antworten
```

Die 100 000 Anfragen sind eine Beispielannahme, kein Messergebnis.
Das tatsächliche Budget richtet sich nach dem gemessenen Gesamtverkehr;
angebrochene erlaubte Fehl-Requests werden abgerundet.

PromQL für den SLI als Anteil zwischen 0 und 1:

```promql
1 - (
  (sum(increase(flask_http_request_total{job="shelfops",status=~"5.."}[30d])) or vector(0))
  /
  sum(increase(flask_http_request_total{job="shelfops"}[30d]))
)
```

**Begründung:** Ausleihen und Bestandsabfragen sollen zuverlässig funktionieren.
99,9 % begrenzt Serverfehler deutlich und lässt dennoch ein kleines Budget
für Störungen; ein Ziel von 100 % würde keinerlei Fehler tolerieren.

**Messgrenze:** Anfragen, die die App wegen eines vollständigen Ausfalls
gar nicht erreichen, fehlen im Zähler. Dieses Fehlerraten-SLO ist daher
kein Nachweis einer zeitlichen Verfügbarkeit von 99,9 %. Der vorhandene
Alarm `ShelfOpsDown` ergänzt die Überwachung der Erreichbarkeit.
Das Request-Budget wird nicht in Ausfallminuten umgerechnet.

### SLO 2 – Anteil ausreichend schneller Antworten

- **SLI:** Anteil der im Request-Histogramm erfassten Anfragen mit einer
  serverseitig gemessenen Dauer von **höchstens 500 ms**. Verwendet werden
  `flask_http_request_duration_seconds_bucket{le="0.5"}` und
  `flask_http_request_duration_seconds_count`.
- **SLO:** Mindestens **95 %** dieser Anfragen werden über 30 Tage
  innerhalb von 500 ms verarbeitet.
- **Error Budget:** Höchstens **5 %** dürfen länger als 500 ms dauern.

Berechnung mit `N` als Anzahl der im Histogramm erfassten Anfragen:

```text
Erlaubter langsamer Anteil = 1 − 0,95 = 0,05
Error Budget              = 0,05 × N

Rechenbeispiel bei angenommenen 100 000 Anfragen in 30 Tagen:
0,05 × 100 000 = 5 000 erlaubte Anfragen über 500 ms
```

Auch diese Verkehrsmenge ist eine Beispielannahme. Das reale Budget
wird aus der tatsächlichen Anzahl der Histogramm-Beobachtungen berechnet.

PromQL für den SLI als Anteil zwischen 0 und 1:

```promql
sum(increase(flask_http_request_duration_seconds_bucket{job="shelfops",le="0.5"}[30d]))
/
sum(increase(flask_http_request_duration_seconds_count{job="shelfops"}[30d]))
```

Der Wert 0,5 Sekunden ist eine Grenze der verwendeten Standard-Buckets.
Der SLI zählt den Anteil bis zu dieser Grenze, statt die p95-Werte der
einzelnen Fünf-Minuten-Fenster zu mitteln. Das Verfahren entspricht der
[Prometheus-Dokumentation zu Histogrammen](https://prometheus.io/docs/practices/histograms/).

**Begründung:** Eine halbe Sekunde ist ein vorgeschlagenes Ziel für
reaktionsfähige Bestands- und Ausleihvorgänge. Es lässt gegenüber den
im lokalen Lasttest beobachteten rund 23 ms p95 Spielraum für höhere
Last und langsamere Datenbankzugriffe. Die erlaubten 5 % berücksichtigen
vereinzelte langsame Antworten, ohne ein unerreichbares 100-%-Ziel zu setzen.

**Messgrenze:** Gemessen wird die serverseitige Dauer, nicht die gesamte
Wartezeit im Browser einschliesslich Netzwerk. Auch schnelle Fehlerantworten
können das Latenzziel erfüllen; deshalb wird es zusammen mit SLO 1 bewertet.
Die vorhandene Alarmgrenze von einer Sekunde p95 über fünf Minuten ist eine
separate kurzfristige Eingriffsschwelle und keine vollständige Überwachung
dieses 30-Tage-Budgets.

### Voraussetzungen für die Auswertung

Eine belastbare 30-Tage-Auswertung benötigt einen durchgängigen Messbetrieb
und mindestens 30 Tage Datenaufbewahrung. Diese Voraussetzungen sind mit dem
Laborlauf noch nicht nachgewiesen; im Compose-Stack ist keine explizite
30-Tage-Retention konfiguriert. Ein `[30d]`-Selektor allein garantiert keine
vollständige Datenbasis. Fehlender Verkehr oder Messlücken werden nicht als
erfülltes SLO gewertet. `increase()` liefert aus den Scrapes geschätzte
Zählerzuwächse, keine revisionssichere Einzelanfragen-Abrechnung.

## 3. Eigene Alarmregel – HighClientErrorRate

Die zusätzliche Regel erkennt einen anhaltend hohen Anteil abgewiesener
HTTP-Anfragen. Für Nutzer äussert sich dies beispielsweise darin, dass
Links ins Leere führen oder Formulare und API-Anfragen wiederholt scheitern.
Die bestehenden Regeln überwachen Erreichbarkeit, 5xx-Antworten und Latenz;
diese Regel ergänzt die Sicht auf 4xx-Antworten.

### YAML-Regel

Die Regel ist in [alert.rules.yml](monitoring/prometheus/alert.rules.yml)
unter der bestehenden Gruppe `shelfops` hinterlegt. Als eigenständige
Regeldatei entspricht sie folgendem Format:

```yaml
groups:
  - name: shelfops
    rules:
      - alert: HighClientErrorRate
        expr: |
          (
            sum(rate(flask_http_request_total{job="shelfops",status=~"4.."}[5m]))
            /
            sum(rate(flask_http_request_total{job="shelfops"}[5m]))
          ) > 0.20
          and
          sum(increase(flask_http_request_total{job="shelfops"}[5m])) >= 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Viele ShelfOps-Anfragen werden mit 4xx abgewiesen"
          description: "Seit fünf Minuten liegt der 4xx-Anteil über 20 %, bei mindestens 100 erfassten Anfragen im jeweiligen Fünf-Minuten-Fenster."
```

### Begründung

- **Symptom:** Mehr als 20 % der erfassten Anfragen werden mit 4xx
  beantwortet. Das ist ein Signal für häufig scheiternde Nutzung,
  aber noch kein Beweis für einen App-Defekt.
- **Schwelle:** Das Labor-Lastskript erzeugt bei 200 Durchläufen
  600 erfolgreiche Anfragen und 40 absichtliche 404-Antworten.
  Sein erzeugter 4xx-Anteil beträgt damit `40 / 640 = 6,25 %`.
  Die vorgeschlagenen 20 % liegen deutlich darüber. Zusätzliche
  erfolgreiche Healthchecks können den gemessenen Anteil weiter senken.
- **Mindestverkehr:** Im jeweiligen Fünf-Minuten-Fenster müssen mindestens
  100 Anfragen erfasst worden sein. Einzelne Fehleingaben bei sehr wenig
  Verkehr sollen keinen Alarm auslösen. Bei geringerem Verkehr bleibt
  die Regel bewusst stumm, auch wenn der Fehleranteil hoch ist.
- **Wartezeit:** `for: 5m` verlangt, dass beide Bedingungen bei jeder
  Regelauswertung fünf Minuten lang bestehen. Das reduziert Alarme durch
  kurze Spitzen. Die Abfrage betrachtet dabei jeweils die letzten fünf
  Minuten; `for` ist die zusätzliche Zeit im Zustand Pending.
- **Severity:** `warning`, weil 4xx-Antworten auch erwartetes Verhalten
  sein können. ShelfOps liefert beispielsweise 400 bei ungültigen Eingaben,
  404 bei fehlenden Ressourcen, 409 bei nicht verfügbaren Exemplaren und
  415 bei einem ungeeigneten Content-Type. Die Ursache muss zuerst geprüft
  werden.

Die Regel bewertet alle erfassten Anfragen gemeinsam. Automatisierte
Zugriffe können sie auslösen und erfolgreiche technische Prüfungen den
Anteil verdünnen. Die Schwelle ist deshalb ein Startwert für den lokalen
Betrieb und muss anhand realer Nutzung überprüft werden.

### Runbook

1. **Alarm einordnen:** In Prometheus unter Alerts `HighClientErrorRate`
   öffnen. Zeitpunkt, 4xx-Anteil und Mindestverkehr prüfen. Ein hohes
   Verhältnis allein reicht für diese Regel nicht aus.
2. **Echtheit prüfen:** In Grafana Fehlerrate, Request-Rate und Version
   vergleichen. Mit der folgenden Abfrage die betroffenen Statuscodes
   ermitteln; insbesondere geplante Tests oder automatisierte Zugriffe
   als Erklärung berücksichtigen.
3. **Betroffene Anfragen finden:** Mit
   `docker compose -f docker-compose.observability.yml logs --since 15m web`
   die Access-Logs prüfen. Pfade, Methoden und Statuscodes auf Häufungen
   untersuchen; keine vertraulichen Request-Inhalte weitergeben.
4. **Nutzerwirkung nachvollziehen:** Den auffälligen Lesezugriff oder
   Eingabefehler kontrolliert reproduzieren. Prüfen, ob etwa ein falscher
   Link, ein ungültiges JSON-Format, ein falscher Content-Type oder ein
   erwarteter Ausleihkonflikt vorliegt.
5. **Ursache beheben:** Fehlerhafte Links oder Client-Anfragen korrigieren.
   Bei einem nachgewiesenen Zusammenhang mit einem Deployment die
   betroffene Änderung korrigieren oder einen geprüften Rollback
   durchführen. Erwartete 4xx-Antworten nicht pauschal in 2xx umwandeln.
6. **Erholung kontrollieren:** Prüfen, ob die betroffenen Nutzeraktionen
   wieder funktionieren und der Anteil sinkt. Abwarten, bis das
   Fünf-Minuten-Fenster alte Fehler nicht mehr enthält und der Alarm
   inaktiv wird; Ursache und Massnahme dokumentieren.

Abfrage zur Aufteilung nach Statuscode:

```promql
sum by (status) (
  rate(flask_http_request_total{job="shelfops",status=~"4.."}[5m])
)
```

### Validierung und Aktivierung

Die Regel wurde am 13.10.2026 in Prometheus unter Alerts mit
`HighClientErrorRate (0 active)` angezeigt. Damit ist das Laden der Regel
belegt; zu diesem Zeitpunkt erfüllte keine Zeitreihe die Alarmbedingung.
Ein beobachteter Firing-Zustand ist für diese zusätzliche Regel nicht belegt.

Für künftige Änderungen vor dem Neustart prüfen:

```bash
docker compose -f docker-compose.observability.yml exec -T prometheus \
  promtool check rules /etc/prometheus/alert.rules.yml
```

Nur bei erfolgreicher Prüfung neu laden und kontrollieren:

```bash
docker compose -f docker-compose.observability.yml restart prometheus
```

Unter Prometheus → Alerts muss anschliessend `HighClientErrorRate`
erscheinen. Ein erfolgreicher Syntaxcheck oder der Zustand Inactive
belegt noch keinen vollständigen Auslösetest. Für diese zusätzliche Regel
wird hier noch kein beobachteter Firing-Zustand behauptet.

## 4. Trivy-Auswertung

### Scan-Grundlage und Auswahl

Bewertet werden die drei CRITICAL-Funde des ursprünglichen Image-Scans
vom **12.10.2026**. Dies sind die drei schwersten Funde dieses gespeicherten
Scans. Im anschliessend aktualisierten Image werden sie nicht mehr gemeldet.
Die Bewertung dokumentiert damit Ausgangsrisiko und durchgeführte Behebung.

- Scanner: **Trivy 0.75.0**, ausschliesslich Scanner `vuln`.
- Ziel: `shelfops:monitoring`, Plattform **linux/arm64**.
- Ausgangsimage: Debian **13.6**, Image-ID
  `sha256:65d367e055c7e7c6ae38cf383789999e3964a42912af9b6341bc03445da53c81`.
- Aktualisiertes Image: Debian **13.7**, Image-ID
  `sha256:6a76b3aaca4eeaa9b993903c1278fc5d20240041a21d6a4f530123d1441d69ee`.
- In beiden Metadaten-Dateien dokumentierter Git-Stand:
  `1bb72eb39948ea0fb5516f93b287a0d36869ede6`.
- Beide Scans verwendeten laut Metadaten die Datenbank mit
  `UpdatedAt: 2026-10-12 13:18:23.1639207 +0000 UTC`.

Der vollständige Ausgangsscan wurde mit folgendem Befehl gespeichert:

```bash
trivy image --scanners vuln --format table \
  --output docs/woche-09/trivy-image.txt shelfops:monitoring
```

Die Angaben zu Severity und installierter Version unten stammen aus diesem
Scan. `fixed` bedeutet dort, dass eine korrigierte Version verfügbar war,
nicht dass das gescannte Image bereits korrigiert war. Die technischen
Voraussetzungen und Debian-Fix-Versionen wurden am 13.10.2026 anhand des
Debian Security Trackers geprüft; andere Quellen können den Schweregrad
anders einstufen.

### Fund 1 – CVE-2026-13221

| Merkmal | Ausgangsscan |
| --- | --- |
| CVE | CVE-2026-13221 |
| Betroffenes Paket laut Scan | `perl-base` |
| Installierte Version | `5.40.1-6` |
| Severity laut Scan | CRITICAL |
| Fixed Version für Debian 13 | `5.40.1-6+deb13u1` |

**Schwachstelle:** Sehr grosse Perl-Regulärausdrücke mit mehr als 65 535
festen Alternativen können falsche Trefferentscheidungen erzeugen.
Wenn solche Ausdrücke Zugriffe oder Filter steuern, können dadurch falsche
Sicherheitsentscheidungen entstehen. Der Debian-Eintrag bestätigt den Fix
für Trixie in `5.40.1-6+deb13u1`.
Quelle: [Debian Security Tracker – CVE-2026-13221](https://security-tracker.debian.org/tracker/CVE-2026-13221).

**Kontext in ShelfOps:** Die Endpunkte `/books` und `/members` nehmen
JSON-Felder entgegen, deren Textwerte in `app/models.py` auf 1–200 Zeichen
begrenzt werden. Sie werden nicht als Perl-Regulärausdrücke ausgeführt.
Die vorhandenen Routen und Repository-Implementierungen enthalten keinen
Aufruf des Perl-Interpreters. Daher ist im geprüften Anwendungscode kein
Angriffspfad von einer HTTP-Eingabe zu dieser verwundbaren Funktion erkennbar.
Die Längenprüfung ist dabei nur ergänzender Kontext; entscheidend ist der
fehlende Perl-Aufruf. `USER appuser` begrenzt die Prozessrechte, würde eine
fehlerhafte Filterentscheidung aber nicht grundsätzlich verhindern.

**Empfehlung und Ergebnis:** Verfügbares Basisimage-Update zeitnah einspielen,
statt den Fund auszublenden. Dies wurde im Labor durchgeführt; der Fund
fehlt im vollständigen Nachher-Scan. Eine `.trivyignore`-Ausnahme wurde
für diesen Fund nicht benötigt.

### Fund 2 – CVE-2026-42496

| Merkmal | Ausgangsscan |
| --- | --- |
| CVE | CVE-2026-42496 |
| Betroffenes Paket laut Scan | `perl-base` (Schwachstelle in Perl `Archive::Tar`) |
| Installierte Version | `5.40.1-6` |
| Severity laut Scan | CRITICAL |
| Fixed Version für Debian 13 | `5.40.1-6+deb13u1` |

**Schwachstelle:** `Archive::Tar` vor Version 3.08 kann beim Entpacken
manipulierte symbolische Links mit Zielen ausserhalb des vorgesehenen
Verzeichnisses erzeugen. Spätere Zugriffe über diese Links können fremde
Dateien lesen oder verändern. Debian stellt die Korrektur für das
Perl-Quellpaket in Trixie ab `5.40.1-6+deb13u1` bereit.
Quelle: [Debian Security Tracker – CVE-2026-42496](https://security-tracker.debian.org/tracker/CVE-2026-42496).

**Kontext in ShelfOps:** Die App verarbeitet Buch-, Mitglieder-, Exemplar-
und Ausleihdaten über JSON. Es gibt in den geprüften Routen keinen
Archiv-Upload und keine Funktion zum Entpacken von Tar-Dateien.
Der Anwendungscode ruft `Archive::Tar` nicht auf. Deshalb ist kein
Angriffspfad über die bestehenden HTTP-Endpunkte erkennbar.
Die Zuordnung zum installierten Paket allein beweist nicht, dass das
betroffene Perl-Modul im konkreten Runtime-Image vorhanden und erreichbar
ist; seine tatsächliche Installation wurde nicht separat geprüft.
Der Betrieb als `appuser` begrenzt Dateirechte, würde aber Dateien,
auf die dieser Benutzer zugreifen darf, bei einer Ausnutzung nicht schützen.

**Empfehlung und Ergebnis:** Den verfügbaren Fix über das Basisimage
übernehmen. Das Update wurde durchgeführt und der Fund wird danach
nicht mehr gemeldet. Für zukünftige Archiv-Importfunktionen müsste die
Erreichbarkeit neu bewertet werden; eine pauschale Ignore-Regel ist hier
nicht erforderlich.

### Fund 3 – CVE-2026-8376

| Merkmal | Ausgangsscan |
| --- | --- |
| CVE | CVE-2026-8376 |
| Betroffenes Paket laut Scan | `perl-base` |
| Installierte Version | `5.40.1-6` |
| Severity laut Scan | CRITICAL |
| Fixed Version für Debian 13 | `5.40.1-6+deb13u1` |

**Schwachstelle:** Beim Kompilieren bestimmter regulärer Ausdrücke kann
ein Integer-Überlauf zu einem Heap-Pufferüberlauf führen. Der beschriebene
Angriff setzt einen **32-Bit-Perl-Build** und einen vom Angreifer beeinflussten
Regulärausdruck voraus. Debian nennt für Trixie ebenfalls
`5.40.1-6+deb13u1` als korrigierte Version.
Quelle: [Debian Security Tracker – CVE-2026-8376](https://security-tracker.debian.org/tracker/CVE-2026-8376).

**Kontext in ShelfOps:** Die Image-Metadaten weisen `linux/arm64` aus.
Das spricht bei nativen Debian-Paketen gegen die beschriebene
32-Bit-Voraussetzung; die Build-Eigenschaften des Perl-Binaries wurden
jedoch nicht separat abgefragt. Unabhängig davon kompiliert ShelfOps
keine vom Benutzer gelieferten Perl-Regulärausdrücke und startet keinen
Perl-Interpreter über seine Endpunkte. Ein entsprechender HTTP-Angriffspfad
ist daher im geprüften Code nicht erkennbar. Der Benutzer `appuser` ist
eine zusätzliche Rechtebegrenzung, verhindert aber keinen Speicherfehler
in einem tatsächlich aufgerufenen verwundbaren Programm.

**Empfehlung und Ergebnis:** Trotz der geringen erkennbaren Relevanz für
diesen Betrieb den verfügbaren Fix übernehmen. Das Basisimage-Update
hat den Treffer im Nachher-Scan beseitigt. Bei späteren Plattformwechseln
oder neuen Perl-Aufrufen wäre die Kontextbewertung erneut vorzunehmen.

### Durchgeführte Behebung und Nachkontrolle

Das Image wurde mit aktueller Basis und ohne Build-Cache neu gebaut:

```bash
docker compose -f docker-compose.observability.yml build --pull --no-cache web
```

Anschliessend wurden vollständiger Scan und Gate erneut ausgeführt,
der Webcontainer mit dem neuen Image gestartet und `/health`, `/ready`
sowie `shelfops_info{version="1.0.0"} 1.0` erfolgreich geprüft.
Die Behebung erfolgte durch das neue Basisimage, nicht durch eine
Reparaturfunktion von Trivy oder eine Änderung des Anwendungscodes.

| Befundgruppe | Vorher | Nachher |
| --- | ---: | ---: |
| Debian: alle Schweregrade | 235 | 166 |
| Debian: HIGH | 58 | 44 |
| Debian: CRITICAL | 3 | 0 |
| Python-Pakete | 6 | 6 |
| HIGH/CRITICAL mit verfügbarem Fix | 17 | 0 |
| Exit-Code des Gates mit `--ignore-unfixed` | 1 | 0 |

Die Zahlen zählen Paket-Schwachstellen-Treffer, nicht zwingend unterschiedliche
CVE-IDs. Das strenge Gate **ohne** `--ignore-unfixed` lieferte nach dem Update
weiterhin Exit-Code **1**, weil 44 HIGH-Treffer ohne verfügbaren Fix
verblieben. Die sechs Python-Funde betreffen `pip` und umfassen fünf
MEDIUM- sowie einen LOW-Treffer. Ein bestandenes gefiltertes Gate bedeutet
deshalb nicht, dass das gesamte Image frei von Sicherheitsbefunden ist.

Die Kontextbewertungen beruhen auf einer Prüfung des Anwendungscodes und
der beschriebenen Ausnutzungsvoraussetzungen. Sie sind kein Penetrationstest
und kein pauschaler Nachweis, dass das Image nicht ausnutzbar ist.

### Nachweise

- [Vollständiger Ausgangsscan](docs/woche-09/trivy-image.txt)
- [Metadaten des Ausgangsimages](docs/woche-09/trivy-image-metadata.txt)
- [Gate vor dem Update](docs/woche-09/trivy-gate-before.txt)
- [Vollständiger Nachher-Scan](docs/woche-09/trivy-image-after.txt)
- [Metadaten des aktualisierten Images](docs/woche-09/trivy-image-metadata-after.txt)
- [Gate nach dem Update, nur behebbare HIGH/CRITICAL](docs/woche-09/trivy-gate-after.txt)
- [Strenges Gate nach dem Update](docs/woche-09/trivy-gate-all.txt)
- [Python-Abhängigkeiten als Scan-Eingabe](docs/woche-09/sca/requirements.txt)
- [Dateisystem-Scan der Python-Abhängigkeiten](docs/woche-09/trivy-fs.txt)
- [Firing-Screenshot des Laboralarms](docs/woche-09/alert-firing.png)

Die Anwendungspfade sind in [app/routes.py](app/routes.py), die
Eingabeprüfungen in [app/models.py](app/models.py) und der Runtime-Benutzer
im [Dockerfile](Dockerfile) nachvollziehbar.

