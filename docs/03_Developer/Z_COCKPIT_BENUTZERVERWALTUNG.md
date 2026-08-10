# Z_Cockpit – Benutzerverwaltung

Stand: 10. August 2026

Die Benutzerverwaltung verwendet weiterhin ausschließlich `ProjectOSUserManagementState` als fachliche Quelle. Neu ist ein vertrauenswürdiger lokaler Verwaltungspfad für Benutzerprofile und Zugriffsregeln; die statische HTML-Seite selbst bleibt ausdrücklich **keine Authentifizierungs- oder Sicherheitsinstanz**.

## Benutzerprofil

Ein ProjectOS-Benutzer besitzt insbesondere:

- stabile `user_id`;
- Bezeichnung/Anzeigename;
- Gewichtung `0..1000`;
- Profil- und Projektrollen;
- optional eindeutigen `github_login`;
- Lifecycle `Aktiv`/`Deaktiviert`;
- Berechtigungszuweisungen, Widerrufe, White-/Blacklist und Ausnahmen.

Die Benutzerverwaltungs-Persistenz hat Version `5`; ältere Stände `1..4` bleiben lesbar. Das äußere ProjectOS-Projektbundle bleibt Version `4`.

Die Gewichtung bleibt von der Autorisierungsentscheidung getrennt. Eine höhere Gewichtung erteilt keine Rechte.

## GitHub-Zuordnung

Der optionale `github_login` verbindet einen ProjectOS-Benutzer mit dem tatsächlich über GitHub CLI (`gh`) authentifizierten GitHub-Konto. Ein GitHub-Login darf innerhalb eines Projekts nur einem Benutzer zugeordnet sein.

Diese Zuordnung wird für vertrauenswürdige schreibende Verwaltungsaktionen und automatische GitHub-Fehlermeldungen verwendet. Die im Browser gewählte `Aktive ProjectOS-Identität` wird dafür **nicht** als Authentifizierung akzeptiert.

## Aktive Identität und Simulation

Der obere Cockpit-Bereich zeigt weiterhin lokale Identität, Bearbeitungsstatus, Gewichtung, Rollen und effektive Rechte. Der feste Testuser

```text
00000000-0000-0000-0000-000000000001
```

bleibt ausschließlich Simulation und wird nicht in ProjectOS gespeichert. Im Simulationsmodus werden weder Governance-Änderungen noch automatische GitHub-Meldungen freigeschaltet.

## Vertrauenswürdiger Verwaltungspfad

Schreibende Aktionen laufen über:

```text
Z_Cockpit
  -> projectos-z://governance
  -> tools/windows/open_projectos_from_cockpit.ps1
  -> tools/projectos_governance_cli.py
  -> tools/projectos_governance.py
  -> DinEditorProjectManager / ProjectOSUserManagementChangeService
  -> ProjectOS-v4-Projektdatei
```

Vor einer normalen Änderung wird der Repositoryzustand erneut geprüft und der mit `gh` authentifizierte Benutzer einem eindeutigen ProjectOS-Profil zugeordnet. Danach muss das für die Aktion erforderliche ProjectOS-Recht effektiv erlaubt sein. DENY/Blacklist und deaktivierte Benutzer wirken fail-closed.

Aktuell verwaltbar sind:

- Benutzer anlegen;
- Bezeichnung ändern;
- Gewichtung ändern;
- GitHub-Login zuordnen/ändern;
- White-/Blacklist-Regeln mit Recht, Scope und Risikoklasse anlegen;
- bestehende Rechtezuweisungen nachvollziehbar widerrufen.

## Erstadministrator

Ein leeres Projekt besitzt bewusst noch keinen automatisch erfundenen Administrator. Der Bootstrap `Erstadministrator einrichten` ist nur zulässig, wenn:

- die Benutzerverwaltung leer ist;
- der Repositoryprüfer einen aktuellen offiziellen Stand bestätigt;
- `gh` einen authentifizierten Benutzer liefert;
- dieser Benutzer in `config/authorized_developers.json` freigegeben ist.

Der Bootstrap verknüpft dieses GitHub-Konto mit dem ersten ProjectOS-Benutzer und vergibt die initialen Administrationsrechte. Danach gelten für weitere Änderungen die normalen ProjectOS-Rechte.

## Sicht- und Bearbeitungsbereiche

Für die Cockpit-Policy sind die Rechte

```text
cockpit.view
cockpit.edit
```

mit Scopes wie `page:projekt`, `page:diagnose`, `page:benutzer`, `page:berechtigungen` oder `page:fehlerbericht` vorgesehen. Die Benutzerseite zeigt diese Entscheidungen als Matrix `Sehen / Bearbeiten`.

Wichtig: Das aktuell statisch erzeugte HTML kann bereits geladene Daten nicht sicher vor einem Benutzer verbergen, der die Datei und das Projektbundle auf Dateisystem-/GitHub-Ebene bereits besitzt. `cockpit.view/edit` bilden deshalb die fachliche Zugriffspolicy und sind für vertrauenswürdige Laufzeitaktionen maßgeblich; echte Vertraulichkeit der Projektdatei wird zusätzlich durch den in `Z_COCKPIT_PROJEKTDATEI.md` beschriebenen Datei-/Repositoryzugriff erzwungen.

## Projekt- und Verwaltungsrechte

Der zentrale Rechtekatalog umfasst unter anderem:

```text
project.file.read
project.file.write
project.file.share
project.file.admin
project.user.manage
project.permission.manage
github.issue.prepare
github.issue.auto_submit
```

Nicht vorhandene Grants werden nicht erfunden. Ein wirksames DENY beziehungsweise eine Blacklist bleibt vorrangig.

## Datenquelle und Cockpit-Erzeugung

Mit Projektbundle:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

Ohne Bundle werden keine realen Benutzer oder Berechtigungen erfunden. Der lokale Testuser bleibt davon getrennt.

## Sicherheitsgrenzen

- Browser-`localStorage` ist keine Authentifizierung.
- Die Simulation kann keine echten Rechte erteilen.
- Schreibende Governance-Aktionen vertrauen nur der neu geprüften lokalen Laufzeit, `gh`-Identität und ProjectOS-Autorisierung.
- GitHub- oder Dateisystem-Leserechte können nicht durch das Cockpit aufgehoben werden.
- Zugangstokens werden nicht in die ProjectOS-Projektdatei oder Cockpit-Seite geschrieben.
