# Selbsteinschätzung – ShelfOps

Grundlage: CDS212, Woche 10, Bewertungsschema Abschlussprojekt, Abschnitt «Selbsteinschätzung vor der Abgabe».

| Kriterium | Maximalpunkte | Selbsteinschätzung | Beleg (Datei, Link, Commit) |
| --- | ---: | ---: | --- |
| Git und Arbeitsweise | 12 | 9 | [GitHub Flow und Commit-Regeln](CONTRIBUTING.md); [PR #19](https://github.com/larscoo/ShelfOps/pull/19) bis [PR #23](https://github.com/larscoo/ShelfOps/pull/23) mit Beschreibung und erfolgreicher CI vor dem Merge; [Abgleich von Branch-Schutz und Historie](abnahme-checkliste.md#git-und-zusammenarbeit) |
| Containerisierung | 12 | 12 | [Multi-Stage-Dockerfile mit appuser und Healthcheck](Dockerfile); [Compose mit PostgreSQL und Volume](docker-compose.yml); [Persistenz- und Ausfallnachweis](docs/nachweise/compose.md); [Imagevergleich und Begründung](abgabe/BEGRUENDUNG.md) |
| CI-Pipeline | 14 | 14 | [Workflow mit Lint, Tests, Cache und Build](.github/workflows/ci.yml); [Coverage-Gate mit fail_under = 80](pyproject.toml); [Rot-Grün-Nachweis mit Merge-Sperre und Screenshots](abgabe/woche-05-ci.md); [erfolgreicher main-Lauf vom 13.10.2026](https://github.com/larscoo/ShelfOps/actions/runs/38411801620) |
| CD und Deployment | 12 | 12 | [Render-Blueprint](render.yaml); [CI-gesteuerter CD-Workflow](.github/workflows/cd.yml); [Deployment- und Störungsrunbook](DEPLOYMENT.md); [erprobter Code-Rollback mit Wiederherstellung und Smoke-Tests](abgabe/rollback-nachweis.md); [erfolgreicher CD-Lauf vom 13.10.2026](https://github.com/larscoo/ShelfOps/actions/runs/38411945331) |
| Infrastructure as Code | 10 | 10 | [Docker-Ressourcen in Terraform](terraform/main.tf); [Variablen und Port-Validierung](terraform/variables.tf); [Outputs](terraform/outputs.tf); [dokumentierte init-/validate-/apply-/destroy-Prüfung, Drift und Idempotenz](terraform/README.md#git-und-labornachweis); [nginx-Zusatzaufgabe mit for_each](terraform/nginx/README.md) |
| Kubernetes | 14 | 14 | [Drei Replikate, Probes, Ressourcenlimits und Update-Strategie](k8s/deployment.yaml); [Service Port 80 auf 8000](k8s/service.yaml); [drei laufende Pods auf beiden Workern](woche08/protokoll-scale.txt); [Anfrageprotokoll ohne beobachteten Fehler](woche08/protokoll-rollout.txt) und [erfolgreicher Rollout](woche08/protokoll-rollout-status.txt); [Rollback](woche08/protokoll-rollback.txt); [HPA-Bonus](woche08/hpa.md) |
| Monitoring und Sicherheit | 14 | 13 | [Prometheus-Scrape-Konfiguration](monitoring/prometheus/prometheus.yml); [Dashboard mit Daten](docs/woche-09/dashboard.png) und [exportiertes JSON](monitoring/grafana/dashboards/shelfops-overview.json); [Firing-Alarm](docs/woche-09/alert-firing.png); [Alarmregeln](monitoring/prometheus/alert.rules.yml); [Trivy-Auswertung und dokumentierte Gate-Schwelle](MONITORING.md); [CI-Integration in PR #22](https://github.com/larscoo/ShelfOps/pull/22) |
| Dokumentation | 12 | 10 | [README mit Startbefehlen](README.md); [C4-Kontext und Containerdiagramm](docs/architektur.md); [Deployment-Runbook](DEPLOYMENT.md); [Monitoring mit SLOs, Error Budgets und Runbook](MONITORING.md); [ADR 0001 mit Alternativen und Konsequenzen](docs/adr/0001-speicherstrategie.md) und [ADR 0002](docs/adr/0002-ci-gesteuertes-render-deployment.md) |
| **Summe** | **100** | 94 | |

Ich denke alles in allem ein solides Projekt.
Am Anfang war die Git-Arbeitsweise neu und es wurde nicht für jede einzelne Änderung einen Commit erstellt. 
Als mir dies bewusst wurde, habe ich angefangen kleinere Commits zu machen.

Ebenfalls bin ich mir nicht sicher, wie die Projektstruktur ist.
- Ist es normal, dass ein Projekt so gross wird?
- Sind so viele Ordner normal?
- Gibt es Files die irrelevant sind?

Hierzu wäre auch Ihr Feedback spannend, um daraus zu lernen.

Ausserdem finde ich eine Selbsteinschätzung eher schwierig.
Ich habe natürlich nichts extra 'unvollständig' gelassen.
Trotzdem denke ich, dass man als Erfahrender DevOps-ler einige Änderungen machen würde.
