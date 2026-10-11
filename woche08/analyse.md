# Analyse: Warum kein Ausfall von ShelfOps?

1. **readinessProbe auf /ready: Wann gilt ein neuer Pod als „bereit“?**

   Die Readiness-Probe ruft `/ready` auf. Erst nach erfolgreicher Prüfung erhält der Pod regulär Anfragen über den Service. Ein gestarteter Container allein genügt nicht: Die Anwendung könnte noch initialisieren.

2. **Was täte der Service ohne diese Probe während des Starts eines Pods?**

   Er könnte bereits Anfragen an einen gestarteten Pod weiterleiten, obwohl die Anwendung noch nicht antworten kann. Diese Anfragen könnten fehlschlagen.

3. **maxUnavailable: 0: Was garantiert dieser Wert zusammen mit der Readiness-Probe?**

   Kubernetes darf beim Update die gewünschte Anzahl verfügbarer Pods nicht unterschreiten. `maxSurge: 1` erlaubt einen zusätzlichen Pod. Bei drei Replikaten startet zuerst ein vierter. Sobald dieser bereit ist, kann ein alter ersetzt werden.

4. **Warum wäre maxUnavailable: 0 ohne Readiness-Probe wirkungslos?**

   Für die tatsächliche Erreichbarkeit reicht die Einstellung allein nicht: Kubernetes könnte einen neuen Pod vorzeitig als verfügbar zählen und einen alten entfernen. Die Pod-Anzahl wäre eingehalten, obwohl noch nicht alle Anfragen bearbeiten können.

**Health-Endpunkte:** `/health` prüft die Anwendung ohne Datenbankabhängigkeit. `/ready` bezieht eine konfigurierte Datenbank ein; im aktuellen In-Memory-Betrieb entfällt diese Prüfung. Eine Datenbankprüfung in der Liveness-Probe könnte bei einem Datenbankausfall unnötige App-Neustarts auslösen. Readiness nimmt betroffene Pods stattdessen aus der Anfrageverteilung.

**Beobachtung:** Nach Ergänzen einer zehnsekündigen `preStop`-Wartezeit lieferten alle protokollierten Testanfragen während des Updates HTTP 200. Das belegt diesen Testlauf, garantiert aber keine allgemeine Fehlerfreiheit.
