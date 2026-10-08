# Woche 7 – nginx mit Terraform

Eigene Umsetzung der Pflicht-Hausaufgabe: `nginx:alpine` liefert die lokale
`index.html` über einen schreibgeschützten Bind-Mount aus. Der absolute Mount-Pfad
wird aus `abspath(path.module)` gebildet. Voraussetzung: Terraform >= 1.5,
laufendes Docker Desktop und Docker-Dateifreigabe für dieses Repository.

## Start und Prüfung

Vom Repository-Wurzelverzeichnis:

```bash
cd terraform/nginx
terraform init
terraform fmt -check
terraform validate
terraform plan -no-color
```

Vor dem ersten Apply einen Screenshot der Plan-Ausgabe erstellen, auf dem die
beiden Ressourcen und `Plan: 2 to add, 0 to change, 0 to destroy.` erkennbar sind.
Den Screenshot als `terraform/plan-screenshot.png` im Repository ablegen.

```bash
terraform apply
terraform output
curl --fail http://localhost:8082/
terraform plan
```

Bei `apply` den Plan prüfen und mit `yes` bestätigen. Die eigene Seite mit
„ShelfOps – Woche 7“ und „Lars“ muss erscheinen. Der zweite Plan sollte
`No changes` melden. `app_url` gibt die vollständige URL aus.

## Port-Variable

`host_port` ist eine Zahl mit Standardwert 8082 und akzeptiert nur ganze Zahlen
von 1025 bis 65535. Die Bindung an `127.0.0.1` beschränkt den Zugriff auf den
lokalen Rechner. Der interne nginx-Port ist 80.

```bash
terraform plan -var="host_port=80"
```

Dieser absichtliche Negativtest muss mit unserer Validierungsmeldung abbrechen.
Ein anderer gültiger Port kann mit `terraform apply -var="host_port=8083"`
gewählt werden; denselben Wert bei späteren Aufrufen erneut angeben.

## Aufräumen und Git

```bash
terraform destroy
terraform state list
```

Mit `yes` bestätigen. Der Container wird entfernt und der State ist leer.
Das Image bleibt wegen `keep_locally = true` im lokalen Docker-Cache.

Die `.tf`-Dateien, HTML-Seite, Anleitung, `.gitignore` und erzeugte
`.terraform.lock.hcl` versionieren. State, `.terraform/` und echte `.tfvars`
bleiben ignoriert. Keine Secrets eintragen.

Dieses Verzeichnis ist eine eigene Terraform-Konfiguration mit eigenem State.
Die ShelfOps-Konfiguration im Elternverzeichnis bleibt unabhängig. Terraform
liest `.tf`-Dateien im jeweiligen Arbeitsverzeichnis, nicht rekursiv in
Unterverzeichnissen. Die optionale Bonusaufgabe mit `for_each` ist nicht enthalten.

## Prüfstand vom 08.10.2026

- `init`, `fmt -check` und `validate` erfolgreich; Provider 3.9.0.
- Erstellungsplan: 2 Ressourcen, keine Änderungen oder Löschungen.
- `apply` erfolgreich; Output `http://localhost:8082`.
- HTTP-Abruf liefert die eigene HTML-Seite mit „ShelfOps – Woche 7“ und „Lars“.
- Port 80 wird mit der eigenen Validierungsmeldung abgelehnt (Exit-Code 1).
- Erneuter Plan nach Apply: `No changes` (Exit-Code 0).
- [Screenshot des gespeicherten Erstellungsplans](../plan-screenshot.png)
  geprüft: Port-Mapping, Bind-Mount, nginx-Image und `Plan: 2 to add` sichtbar.
- `terraform destroy` vom Projektverantwortlichen bestätigt; anschliessend
  mit `terraform state list` geprüft, dass der State leer ist.

Der Erstellungsplan wurde lokal als ignorierte Datei `preview.tfplan` gespeichert.
Solange diese Datei vorhanden ist, lässt sich genau dieser Plan für den Screenshot
mit `terraform show -no-color preview.tfplan` erneut anzeigen. Das ist der
Erstellungsplan vor dem Apply, nicht der aktuelle Zustand des laufenden Containers.
