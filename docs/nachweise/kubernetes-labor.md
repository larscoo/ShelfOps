# Woche 8 – Rollback und Aufräumen

Prüfung vom 11.10.2026 im lokalen Kontext `kind-shelfops`.

## Schritt 9

Ausgangszustand: Revision 6, Image `shelfops:k8s-v1`, APP_VERSION `1.0.0`.
Zielrevision 5 wurde vorab geprüft: Image `shelfops:k8s-v2`.

Ausgeführte Änderung:

```bash
kubectl --context kind-shelfops -n shelfops patch configmap shelfops-config --type merge -p '{"data":{"APP_VERSION":"2.0.0"}}'
kubectl --context kind-shelfops -n shelfops rollout undo deployment/shelfops --to-revision=5
kubectl --context kind-shelfops -n shelfops rollout status deployment/shelfops --timeout=180s
```

Ergebnis: `deployment "shelfops" successfully rolled out`.
Der Undo stellt Revision 5 als neue Revision 7 wieder her. Die ConfigMap wurde
separat zurückgesetzt; sie gehört nicht zur Deployment-Revisionshistorie.

Originalausgaben nach dem Rollback (`get pods -o wide`, Image-Abfrage und
`rollout history`):

```text
NAME                       READY   STATUS    RESTARTS   AGE   IP            NODE               NOMINATED NODE   READINESS GATES
shelfops-886cbb84d-57rgs   1/1     Running   0          49s   10.244.2.12   shelfops-worker2   <none>           <none>
shelfops-886cbb84d-ktm69   1/1     Running   0          36s   10.244.2.13   shelfops-worker2   <none>           <none>
shelfops-886cbb84d-ntllr   1/1     Running   0          42s   10.244.1.11   shelfops-worker    <none>           <none>
shelfops:k8s-v2
deployment.apps/shelfops 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
3         <none>
4         <none>
6         <none>
7         <none>

```

HTTP-Prüfungen mit `curl --fail`, beide erfolgreich (Exit-Code 0):

```text
{"commit":"unknown","status":"ok","version":"2.0.0"}
{"status":"ready"}
```

Während dieses Rollbacks wurde keine durchgehende Anfrageschleife aufgezeichnet.
Die Health-Prüfung nach Abschluss belegt keinen ausfallfreien Gesamtverlauf.

## Schritt 10

`kind delete cluster --name shelfops` erfolgreich:

```text
Deleted nodes: ["shelfops-control-plane" "shelfops-worker2" "shelfops-worker"]
```

Anschliessend `kind get clusters`:

```text
No kind clusters found.
```

Die lokale, ignorierte Datei `k8s/secret.yaml` wurde entfernt.
`secret.example.yaml` bleibt als sichere Vorlage erhalten. Der lokale
ConfigMap-Wert ist mit dem v2-Image in `deployment.yaml` abgestimmt.

