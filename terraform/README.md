# ShelfOps mit Terraform

Die Konfiguration verwaltet einen lokalen ShelfOps-Container, sein Image,
ein Docker-Netzwerk und ein benanntes Volume mit `kreuzwerker/docker`.
Voraussetzungen: Terraform >= 1.5 und ein laufender Docker-Daemon.

## Start

Im Repository-Wurzelverzeichnis das Image bauen, anschliessend Terraform starten:

```bash
docker build -t shelfops:local .
cd terraform
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
```

Den Plan prüfen und `apply` mit `yes` bestätigen. Terraform baut das Image
nicht selbst; `shelfops:local` muss bereits lokal vorhanden sein.

```bash
terraform output
curl http://localhost:8001/health
terraform state list
terraform plan
```

Die Oberfläche ist unter http://localhost:8001 erreichbar. Der zweite Plan
soll ohne Konfigurationsänderung `No changes` melden (Idempotenz).
Der Docker-Healthcheck wird aus dem App-Image übernommen.

## Variablen und Outputs

| Variable | Standard | Bedeutung |
| --- | --- | --- |
| `container_name` | `shelfops` | Containername; Präfix für Netzwerk und Volume |
| `image_tag` | `local` | Tag des zuvor gebauten `shelfops`-Images |
| `app_version` | `1.0.0-iac` | `APP_VERSION`, sichtbar unter `/health` |
| `host_port` | `8001` | Host-Port, validierter Bereich 1025–65535 |

Der interne Port bleibt 8000. Beispiel für einen anderen Host-Port:

```bash
terraform plan -var="host_port=8081"
terraform apply -var="host_port=8081"
```

Bei späteren Aufrufen dieselben Variablen verwenden, wenn die Abweichung
beibehalten werden soll. `terraform plan -var="host_port=80"` muss bewusst
mit einem Validierungsfehler abbrechen.

Outputs: `app_url`, `container_id` und `container_name`.

## Speicher und Aufräumen

Ohne `DATABASE_URL` verwendet ShelfOps In-Memory-Speicher. Das Übungsvolume
ist unter `/data` eingehängt, wird von der App aber nicht genutzt. Es macht
Bibliotheksdaten deshalb nicht persistent. Beim Ersetzen oder Entfernen des
Containers gehen diese Daten verloren. Render wird hier nicht verwaltet.

```bash
terraform destroy
terraform state list
docker images shelfops:local
```

`destroy` mit `yes` bestätigen. Danach ist der State leer; Container, Netzwerk
und Volume sind entfernt. Das Image bleibt dank `keep_locally = true` lokal
erhalten, obwohl seine Terraform-Ressource aus dem State entfernt wird.

## Git und Labornachweis

Die `.tf`-Dateien, `.gitignore`, diese Anleitung und `.terraform.lock.hcl`
versionieren. Die Lock-Datei hält die ausgewählte Provider-Version fest.
`.terraform/`, State-Dateien und echte `.tfvars` bleiben ausgeschlossen.
Keine Secrets in versionierte Dateien eintragen.

Labordurchlauf vom 08.10.2026: `init`, `apply`, Health-Prüfung, Variablenprüfung,
Netzwerk/Volume, Outputs und `destroy` wurden vom Projektverantwortlichen
durchgeführt und im Arbeitsdialog bestätigt. Die gepostete Ausgabe belegt die
Drift-Erkennung nach `docker rm -f shelfops`, die Wiederherstellung durch
`apply`, eine erfolgreiche Health-Antwort und anschliessend `No changes`.
Bei der Abschlussprüfung waren `fmt -check` und `validate` erfolgreich,
der State leer und die Git-Ausnahmen wirksam.

Dies dokumentiert das auf ShelfOps übertragene Labor. Die separate
[Woche-7-Hausaufgabe mit nginx und eigener HTML-Seite](nginx/README.md) liegt
im Unterverzeichnis `nginx/` und verwendet einen eigenen Terraform-State.
