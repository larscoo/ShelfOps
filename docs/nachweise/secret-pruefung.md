# Secret-Prüfung vor der Abschlussabgabe

Prüfdatum: **15.11.2026**. Ausgeführt durch Codex im Auftrag des
Projektverantwortlichen. Geprüfter `main`-Stand:
`e120d224b66fb20ccc532efe8e1572ebd2602def`.
`git ls-remote origin refs/heads/main` bestätigte dieselbe SHA auf GitHub.
Der Arbeitsordner war zu Beginn unverändert; das Repository ist kein
Shallow-Klon.

## Umfang und Verfahren

| Gegenstand | Umfang |
| --- | ---: |
| Dateien im geprüften `HEAD` | 123 |
| Über lokale Branches und Remote-Tracking-Refs erreichbare Commits | 80 |
| Unterschiedliche versionierte Dateiinhalte über diese Historie | 214 |
| Davon Text-Dateiversionen | 203 |
| Davon Screenshot-Dateiversionen | 11 |

Alle mit `git rev-list --all` erreichbaren Commits wurden über
`git ls-tree -r -z` ausgewertet. Die zugehörigen Blob-Inhalte wurden mit
`git cat-file blob` in einen geschützten temporären Auditordner exportiert.
Identische Inhalte wurden nur einmal gescannt; die Zuordnung zu ihren
Dateipfaden blieb erhalten. Dadurch wurden auch frühere Inhalte geprüft,
die im aktuellen Stand geändert oder gelöscht sind. Die lokale, ignorierte
`.env` wurde nicht als veröffentlichter Repository-Inhalt behandelt.

Die 203 Textversionen wurden mit **Trivy 0.75.0**, Scanner `secret`, geprüft.
Zusätzlich wurden Commit-Nachrichten, historische Dateinamen und Ref-Namen
separat mit demselben Scanner untersucht. Die Scans liefen mit explizit
leeren `--config`, `--ignorefile` und `--secret-config`, damit keine lokalen
Ignore-Dateien die Prüfung beeinflussen. Der Vulnerability-Scanner wurde
für diese Prüfung nicht benötigt.

Die elf Screenshots wurden mit **Tesseract 5.5.3** jeweils in den Modi
`--psm 3` und `--psm 11` in Text überführt. Sowohl OCR-Text als auch
TSV-Ausgaben wurden mit Trivy gescannt. Ergänzend wurden gezielt Muster für
private Schlüssel, GitHub-/GitLab-Tokens, AWS-Zugriffsschlüssel,
Render-API-Keys und Deploy-Hook-Keys, Bearer-Tokens, JWTs,
Zugangsdaten in URLs sowie verdächtige Zuweisungen geprüft.

Ein nichttrivialer Zugangswert aus der lokalen `.env` wurde zusätzlich
mit den historischen Dateiinhalten verglichen, ohne seinen Wert auszugeben.

Verwendetes Trivy-Aufrufmuster, jeweils mit getrenntem JSON-Ergebnis:

```sh
trivy fs --scanners secret --format json --output REPORT.json \
  --exit-code 0 --skip-version-check \
  --config '' --ignorefile '' --secret-config '' \
  --cache-dir AUDIT_CACHE EXPORT_VERZEICHNIS
```

Die JSON-Berichte wurden nach dem Scan ausdrücklich auf ihre Findings
geprüft. Exit-Code 0 allein gilt hier nicht als Nachweis fehlender Funde,
da die Aufrufe für die Auswertung mit `--exit-code 0` liefen.

## Ergebnis

**Keine bestätigten versehentlich veröffentlichten Zugangsdaten gefunden.**

| Prüfung | Ergebnis |
| --- | --- |
| Trivy: historische Dateiversionen | 0 Secret-Funde |
| Trivy: OCR-Texte und TSV-Ausgaben | 0 Secret-Funde |
| Trivy: Commit-Nachrichten, Dateinamen und Refs | 0 Secret-Funde |
| Ergänzende Textmuster | 13 Kandidaten; sämtlich Beispiele, Testwerte oder Variablenreferenzen |
| Ergänzende OCR-Muster | Kein Token oder Hook-Key; ein auffälliger gemischter Wert als öffentliche Render-Deploy-ID eingeordnet |
| Abgleich des lokalen Zugangswerts | Kein Treffer in den historischen Dateiinhalten |
| Historisch versionierte `.env`, `secret.yaml`, private `.pem`-/`.key`-Dateien und Terraform-State-Dateien | Keine gefunden |
| Git-Ignore für `.env`, `k8s/secret.yaml`, State und `.terraform/` | Wirksam |

Die Kandidaten stammen insbesondere aus `.env.example`, der isolierten
Testdatenbank, der Kubernetes-Secret-Vorlage und Referenzen auf
Umgebungsvariablen bzw. GitHub Secrets. Diese sind als Demo-/Testkonfiguration
oder Platzhalter einzuordnen und dürfen nicht als echte Produktionszugänge
wiederverwendet werden. Öffentliche Service-/Deploy-IDs, Image-Digests,
Commit-SHAs und die Render-Basis-URL sind für sich keine Zugangsdaten.

## Screenshot-Abdeckung

- `abgabe/cd-erfolgreich.png`
- `abgabe/cools-ci-gruen.png`
- `abgabe/cools-ci-rot.png`
- `abgabe/docker-images.png`
- `abgabe/render-deploy-hook.png`
- `abgabe/render-health.png`
- `abgabe/restore-render.png`
- `abgabe/rollback-render.png`
- `docs/woche-09/alert-firing.png`
- `docs/woche-09/dashboard.png`
- `terraform/plan-screenshot.png`

Die Screenshot-Prüfung beruht auf OCR und der Einordnung auffälliger
Textstellen, nicht auf einer garantierten vollständigen Erkennung jedes
Bilddetails. Die zwei OCR-Modi dienen dazu, unterschiedliche Textanordnungen
abzudecken.

## Grenzen und Folgerung

Die Abschlussprüfung wurde für den genannten Git-Stand durchgeführt und
kann in der Abnahme-Checkliste als erledigte Prüfung geführt werden.
Aus dem Ergebnis ergibt sich kein bestätigter Fund, der eine Rotation oder
Bereinigung der Git-Historie erfordert.

Mustererkennung und OCR können Geheimnisse übersehen, etwa bei unbekannten
Formaten, Verschleierung, beliebiger Kodierung oder schlecht lesbaren Bildern.
Die Prüfung ist keine Garantie völliger Secret-Freiheit. Zugangsdaten wurden
nicht gegen externe Dienste ausprobiert. GitHub-Actions-Logs, Artefakte,
Issues, PR-Kommentare und accountseitige Secret-Einstellungen waren nicht
Teil dieses Dateisystem- und Historientests. Nicht mehr über lokale Refs
erreichbare Git-Objekte und nicht separat abgerufene PR-Refs sind ebenfalls
nicht abgedeckt. Änderungen nach der geprüften SHA erfordern eine erneute
Prüfung der betroffenen Inhalte.

Die [wertfreie Ergebniszusammenfassung](secret-pruefung-2026-11-15.json)
enthält Zählwerte, Dateipfade und SHA256-Prüfsummen der drei temporären
Trivy-Rohberichte. Die Rohberichte, exportierten Inhalte und OCR-Texte
bleiben ausserhalb des Repositorys im geschützten temporären Auditordner;
sie werden nicht als dauerhafte Abgabe vorausgesetzt.

Verfahrensreferenz:
[Trivy 0.75 – Secret Scanning](https://trivy.dev/docs/v0.75/guide/scanner/secret/).
