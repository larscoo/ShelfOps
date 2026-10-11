# Zusatzaufgabe: Automatische Skalierung mit HPA

## Aufbau

Der HorizontalPodAutoscaler steuert das Deployment `shelfops`. Er erlaubt zwei bis fünf Replikate und strebt eine durchschnittliche CPU-Auslastung von 70 % der CPU-Requests an. 
Bei `requests.cpu: 100m` entspricht dies ungefähr 70m CPU pro Pod.

Der metrics-server liefert die Messwerte. Für den lokalen kind-Cluster wurde gemäss Kursvorlage `--kubelet-insecure-tls` ergänzt.

## Durchführung

Ein separater Pod mit `busybox:1.37` rief `/health` fortlaufend über den internen Service auf. Währenddessen wurden HPA-Status und CPU-Verbrauch alle fünf Sekunden aufgezeichnet.

Nach dem Hochskalieren wurde der Lastgenerator gelöscht. Die Aufzeichnung lief weiter, bis wieder zwei bereite App-Pods vorhanden waren.

## Ergebnis

Die Replikatzahl stieg unter Last von drei über vier auf fünf. Nach Lastende sank die CPU-Auslastung auf ungefähr 1 %. Der HPA reduzierte die Anzahl zeitverzögert auf zwei Pods.
Die Verzögerung verhindert ein zu schnelles Hin- und Herskalieren.

## Nachweise

- [HPA-Konfiguration](manifeste/hpa.yaml)
- [Messverlauf und Endzustand](protokoll-hpa.txt)
- [Zeitpunkt des Lastendes](protokoll-hpa-lastende.txt)

## Einschränkung

Die App-Pods verwenden getrennte In-Memory-Speicher. Der Versuch zeigt die automatische Skalierung, aber keinen gemeinsamen Datenbestand zwischen den Replikaten.
