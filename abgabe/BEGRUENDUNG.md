# Begründung der Docker-Optimierungen

Der lokale Vergleich vom 24. September 2026 auf linux/arm64 ergibt für
`shelfops:local` 187 MB (187386001 Bytes), für `shelfops:naiv` 1,17 GB
(1173595659 Bytes). Das optimierte Image ist damit rund 84 Prozent kleiner.
Gemessen wurde die lokale Image-Grösse, nicht die komprimierte Downloadgrösse.
Die Image-IDs und exakten Werte stehen in `docker-images.txt`.

Den grössten Unterschied bewirkt `python:3.12-slim`: Das vollständige Python-Image
der naiven Variante enthält zusätzliche Systempakete und Entwicklungswerkzeuge,
die ShelfOps zur Laufzeit nicht benötigt. Der Multi-Stage-Build installiert die
Python-Abhängigkeiten in einer Builder-Stufe und übernimmt nur deren Installation
in die Runtime. Builder-Dateien wie die erzeugte Anforderungsliste bleiben zurück.
`--no-cache-dir` verhindert zusätzlich einen pip-Downloadcache im fertigen Image.
Multi-Stage allein garantiert jedoch noch keine bestimmte Grössenersparnis.

Die Abhängigkeiten werden vor dem Anwendungscode kopiert und installiert.
Änderungen an Routen oder Templates lassen dadurch den Installationslayer im
Build-Cache unverändert. Das beschleunigt erneute Builds. Die naive Variante
kopiert zuerst den gesamten erlaubten Kontext und verliert diesen Vorteil.

Die `.dockerignore` erlaubt nur benötigte Anwendungsdateien und schliesst unter
anderem Git-Daten, Tests, lokale Umgebungen und Secrets aus. Für einen sicheren
Vergleich gilt dieselbe Ausschlussliste auch beim naiven Build.

Im optimierten Container läuft Gunicorn als `appuser` mit UID 10001 statt als
root. Das reduziert die Rechte des Prozesses. Ein Healthcheck prüft `/health`.
Die naive Variante startet lediglich den Flask-Entwicklungsserver und dient
ausschliesslich dem Vergleich, nicht dem Deployment.
