# Rollback-Übung vom 04.10.2026

Zielservice: `srv-db19pnid0e5s73ep7isg`, Blueprint `exs-db19pf942hec73emj8rg`,
öffentliche URL https://shelfops.onrender.com.

Vorbereitung: Der neue Hook wurde mit
[CD-Lauf 37225622868](https://github.com/larscoo/ShelfOps/actions/runs/37225622868)
geprüft. Deploy `dep-db19tcnavr4c73aunf80` war im selben Service Live.
Die GitHub-CD-Automatik wurde für die Übung vorübergehend deaktiviert.
Es liefen keine weiteren CD-Jobs. Git-Historie und Branch-Schutz blieben unverändert.

## Rückkehr zum früheren Code

- Ausgangscommit: `8f81b7c98e92d8de3b7c7e31a3bc80e3780fca2a`.
- Zielcommit: `107598c28ac795c652b2ec18282c9ee83524d80f`.
- Dessen [CI-Lauf](https://github.com/larscoo/ShelfOps/actions/runs/37218296386) war erfolgreich.
- Methode: **Manual Deploy → Deploy a specific commit**, nicht Artefakt-Rollback.
  Im neu angelegten Service gab es noch kein Build-Artefakt des älteren Commits.
- Render-Deploy: `dep-db19uqmgekts73csh2ug`, am 04.10.2026 um 20:48 Uhr CEST
  gestartet, um 20:48:38 laut Render-Log Live.
- [Screenshot des erfolgreichen Deploys](rollback-render.png).
- [Health-Antwort](rollback-health.txt): `{"status":"ok"}`.
- [Vollständiger Smoke-Test](rollback-smoke.txt): `SMOKE TEST PASSED`.

Diese ältere Anwendung meldet noch keine Commit-/Versionsfelder. Deshalb wurde
ohne `EXPECTED_COMMIT` getestet; die Codeidentität wurde über die Render-Quelle
`107598c` bestätigt. Die Übung prüft einen Code-Rollback durch Neubau, keine
Datenbankwiederherstellung und nicht die Wiederverwendung eines alten Artefakts.
Die In-Memory-Demodaten wurden durch den Neustart verworfen.

## Wiederherstellung

Der ursprüngliche Commit `8f81b7c98e92d8de3b7c7e31a3bc80e3780fca2a` wurde über
**Deploy a specific commit** erneut ausgerollt:

- Deploy `dep-db19vpk9v7es73ekf0l0`, laut Render-Log um 20:50:51 CEST Live.
- [Screenshot der Wiederherstellung](restore-render.png).
- [Smoke-Test mit erwarteter Commit-SHA](restore-smoke.txt):
  `SMOKE TEST PASSED`, `/health` meldet Version `1.0.0` und die ursprüngliche SHA.
- GitHub-CD-Workflow anschliessend wieder aktiviert; API meldet `state: active`.

Die Anwendung ist wieder auf dem ursprünglichen Stand. Die Übung erzeugte
Demodaten, aber keine Commits und keine Änderungen an Branch-Schutz oder Secrets.
