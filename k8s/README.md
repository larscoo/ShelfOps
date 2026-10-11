# ShelfOps im lokalen kind-Cluster

Voraussetzungen: laufendes Docker, kind und kubectl. Die Manifeste bilden den
Laborstand nach Skalierung und Rollback ab: drei Replikate, Image `k8s-v2`,
Versionsanzeige `2.0.0`. Im Labor wurden die beiden Image-Tags aus demselben
Anwendungscode gebaut; die sichtbare Version stammt aus der ConfigMap.

## Start

Vom Repository-Wurzelverzeichnis:

```bash
kind create cluster --config k8s/kind-config.yaml
docker build -t shelfops:k8s-v2 .
kind load docker-image shelfops:k8s-v2 --name shelfops
kubectl --context kind-shelfops apply -f k8s/namespace.yaml
kubectl --context kind-shelfops apply -f k8s/configmap.yaml
kubectl --context kind-shelfops apply -f k8s/deployment.yaml
kubectl --context kind-shelfops apply -f k8s/service.yaml
kubectl --context kind-shelfops apply -f k8s/service-nodeport.yaml
kubectl --context kind-shelfops -n shelfops rollout status deployment/shelfops --timeout=180s
kubectl --context kind-shelfops -n shelfops get pods -o wide
curl --fail http://localhost:30080/health
curl --fail http://localhost:30080/ready
```

Die NodePort-Weiterleitung kann nach Erstellung kurz Zeit benötigen. Die App
ist danach auch im Browser unter http://localhost:30080 erreichbar.

## Grenzen des Labors

Jeder Pod hat seinen eigenen In-Memory-Speicher. Bibliotheksdaten werden nicht
zwischen Replikaten geteilt und gehen beim Austausch der Pods verloren. Der
vollständige Projektbetrieb mit mehreren Replikaten benötigt eine gemeinsame
Datenbank; diese ist hier noch nicht eingerichtet.

`secret.example.yaml` enthält ausschliesslich einen Beispielwert und dient zur
Demonstration von Kubernetes-Secrets. Eine lokale Kopie `secret.yaml` wird
ignoriert. Das Deployment bindet dieses Secret nicht ein. Die Base64-Darstellung
eines Secret-Werts ist keine Verschlüsselung.

## Rolling Update und Rollback

`maxUnavailable: 0` und Readiness-Probes erhalten die Anzahl bereiter Pods.
Der `preStop`-Hook wartet zusätzlich zehn Sekunden vor SIGTERM, während die App
noch antwortet. Die gesamte Beendigungsfrist ist 45 Sekunden. Dies gibt den
Netzwerkregeln Zeit, den beendenden Pod aus der Weiterleitung zu nehmen; es ist
keine allgemeine Garantie gegen Anfragefehler.

Im ersten Labortest am 08.10.2026 traten drei Anfragefehler auf. Nach Ergänzen
des Hooks enthielten die vom Projektverantwortlichen geposteten Tests nur
HTTP-200-Antworten, auch beim Wechsel von v2 auf v1. Ein vollständiges,
gespeichertes Rollout-Protokoll für die Hausaufgabe steht noch aus.

`rollout undo` stellt eine frühere Pod-Vorlage wieder her. Eine referenzierte
ConfigMap wird dabei nicht zurückgesetzt und muss separat angepasst werden.
Vor einem Rollback immer die Zielrevision mit `rollout history` prüfen.
Die lokale ConfigMap und das Deployment sind auf den wiederhergestellten
v2-Stand abgestimmt. Die beim Undo ausgegebene Warnung zur
`last-applied-configuration` betrifft die von `kubectl apply` gespeicherte
Konfiguration; ein Undo aktualisiert diese Annotation nicht.

## Aufräumen

```bash
kind delete cluster --name shelfops
kind get clusters
```

Das entfernt ausschliesslich den lokalen Labor-Cluster inklusive seiner Pods
und Secrets. Die lokale Datei `k8s/secret.yaml`, falls angelegt, danach ebenfalls
entfernen. Die versionierte Beispiel-Datei behalten. Render bleibt unberührt.
