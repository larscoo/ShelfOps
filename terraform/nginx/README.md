# Woche 7 – nginx mit Terraform

Eigene Umsetzung der Pflicht- und Bonus-Hausaufgabe: Zwei Instanzen von
`nginx:alpine` liefern die lokale
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
drei Ressourcen und `Plan: 3 to add, 0 to change, 0 to destroy.` erkennbar sind.
Der vorhandene Screenshot `terraform/plan-screenshot.png` belegt die frühere
Pflichtaufgabe mit einer Instanz. Ein ergänzender Bonus-Screenshot kann unter
`terraform/plan-bonus-screenshot.png` abgelegt werden.

```bash
terraform apply
terraform output
curl --fail http://localhost:8082/
curl --fail http://localhost:8083/
terraform plan
```

Bei `apply` den Plan prüfen und mit `yes` bestätigen. Die eigene Seite mit
„ShelfOps – Woche 7“ und „Lars“ muss erscheinen. Der zweite Plan sollte
`No changes` melden. `app_urls` gibt beide vollständigen URLs aus.

## Zwei Instanzen mit for_each

Ein einziger `docker_container`-Block verarbeitet diese Map:

```hcl
for_each = {
  eins = var.host_port
  zwei = var.second_host_port
}
```

`each.key` ist der Name (`eins` oder `zwei`) und wird Teil des Containernamens.
`each.value` ist der jeweilige Host-Port. So entstehen
`docker_container.web["eins"]` und `docker_container.web["zwei"]`, ohne den
Ressourcenblock zu kopieren. Beide teilen dasselbe Image und lesen dieselbe
HTML-Datei. Im Container können beide Port 80 nutzen; auf dem Mac brauchen sie
unterschiedliche Ports. Eine Vorbedingung lehnt gleiche Host-Ports ab.

Der Output iteriert über beide Container und liest deren externe Ports:

```text
app_urls = {
  "eins" = "http://localhost:8082"
  "zwei" = "http://localhost:8083"
}
```

## Port-Variable

`host_port` (Standard 8082) und `second_host_port` (Standard 8083) akzeptieren
nur ganze Zahlen von 1025 bis 65535. Die Bindung an `127.0.0.1` beschränkt den Zugriff auf den
lokalen Rechner. Der interne nginx-Port ist 80.

```bash
terraform plan -var="host_port=80"
terraform plan -var="second_host_port=80"
terraform plan -var="second_host_port=8082"
```

Diese absichtlichen Negativtests müssen mit einer verständlichen Meldung
abbrechen. Andere gültige Ports können zum Beispiel so gewählt werden:

```bash
terraform apply -var="host_port=8084" -var="second_host_port=8085"
```

Dieselben Werte bei späteren Aufrufen erneut angeben.

## Aufräumen und Git

```bash
terraform destroy
terraform state list
```

Mit `yes` bestätigen. Beide Container werden entfernt und der State ist leer.
Das Image bleibt wegen `keep_locally = true` im lokalen Docker-Cache.

Die `.tf`-Dateien, HTML-Seite, Anleitung, `.gitignore` und erzeugte
`.terraform.lock.hcl` versionieren. State, `.terraform/` und echte `.tfvars`
bleiben ignoriert. Keine Secrets eintragen.

Dieses Verzeichnis ist eine eigene Terraform-Konfiguration mit eigenem State.
Die ShelfOps-Konfiguration im Elternverzeichnis bleibt unabhängig. Terraform
liest `.tf`-Dateien im jeweiligen Arbeitsverzeichnis, nicht rekursiv in
Unterverzeichnissen.

## Nachweis der Pflichtaufgabe vom 08.10.2026 (eine Instanz)

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

## Nachweis der Zusatzaufgabe vom 08.10.2026 (zwei Instanzen)

- `fmt -check` und `validate` erfolgreich.
- Plan und Apply: 3 Ressourcen (zwei Container, ein gemeinsames Image).
- Beide URLs ausgegeben; HTTP-Abrufe auf 8082 und 8083 liefern die eigene Seite.
- Erneuter Plan: `No changes`, Exit-Code 0.
- `second_host_port=80` wird durch Variablenvalidierung abgelehnt.
- `second_host_port=8082` wird wegen gleicher Ports abgelehnt.
- Beide Negativtests enden mit Exit-Code 1 und verändern keine Container.

Der Bonus-Erstellungsplan ist lokal als ignorierte Datei `bonus.tfplan` vorhanden.
Mit `terraform show -no-color bonus.tfplan` lässt sich dieser Plan erneut anzeigen.
Nach der eigenen Browser-Prüfung beide Übungscontainer mit `terraform destroy`
entfernen. Der ältere Screenshot bleibt als Nachweis des ersten Durchlaufs erhalten.
