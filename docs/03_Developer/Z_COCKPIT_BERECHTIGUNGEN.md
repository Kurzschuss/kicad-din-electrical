# Z_Cockpit – Berechtigungen und Whitelists

Die Z_Cockpit-Seite `Berechtigungen` führt vorhandene ProjectOS-Berechtigungszuweisungen und die Repository-Entwickler-Whitelist sichtbar zusammen, ohne Sicherheitskonzepte zu vermischen.

## Grundsatz

Es gibt weiterhin getrennte Schutzebenen:

1. **ProjectOS-Benutzerberechtigungen** aus `ProjectOSUserManagementState`;
2. **Repository-Entwickler-Whitelist** aus `config/authorized_developers.json`;
3. **Speicher-/Git-Zugriff** auf eine ProjectOS-Projektdatei.

Die Repository-Datei wird nicht in ProjectOS importiert. ProjectOS-Berechtigungen werden umgekehrt nicht in die Repository-Whitelist geschrieben. Die Dateisichtbarkeit eines Projektbundles kann nicht durch interne ProjectOS-Rechte ersetzt werden.

## ProjectOS-Berechtigungen

Die Seite wertet vorhandene `ProjectOSPermissionAssignment`-Objekte aus. Sichtbar sind unter anderem Benutzer, technische ID, Berechtigung, Zuweisungs-ID, Quelle, Wirkung, Scope, Risikoklasse, Gültigkeit, Widerrufsstatus und effektive Rechteherkunft.

Unterstützte Quellen bleiben Rolle, direkte Zuweisung, Delegation, DENY, Ausnahme, Whitelist und Blacklist. Die ProjectOS-Autorisierung ist maßgeblich; ein wirksames DENY hat Vorrang vor erlaubenden Quellen.

Die Cockpit-Seite verwendet den bestehenden `ProjectOSAuthorizationEvaluator` und implementiert keine zweite Rechteauswertung.

## Reservierte Projektdateirechte

Für den ProjectOS-Projektdatei-Workflow sind folgende Berechtigungs-IDs verbindlich vorgesehen:

```text
project.file.read
project.file.write
project.file.share
project.file.admin
```

Bedeutung:

- `project.file.read`: Projektdatei in einer vertrauenswürdigen ProjectOS-Laufzeit öffnen/lesen;
- `project.file.write`: fachliche Änderungen speichern;
- `project.file.share`: Freigaben beziehungsweise Weitergabe verwalten;
- `project.file.admin`: Dateirechte und Schutzkontext verwalten.

Die Seite `Projekt` zeigt diese vier Entscheidungen je Benutzer als eigene Zugriffsmatrix an. Nicht vorhandene Grants werden als `Nicht erteilt` dargestellt. Ein deaktivierter Benutzer wird fail-closed behandelt.

Diese Rechte wirken **innerhalb ProjectOS**. Sie können eine Datei nicht vor einem Benutzer verbergen, der bereits auf Dateisystem- oder GitHub-Ebene Zugriff darauf hat.

## Dateisichtbarkeit und GitHub

GitHub besitzt innerhalb eines einzelnen Repositories keine vertraulichen Leserechte nur für ausgewählte Dateien. Deshalb gilt:

- vertrauliche ProjectOS-Teamdateien werden in einem **separaten privaten Projekt-Repository** gespeichert;
- die GitHub-Mitglieder-/Teamrechte dieses Projekt-Repositories bestimmen, wer die Datei herunterladen kann;
- Benutzer mit reinem Lesebedarf erhalten dort nur Leserechte;
- Benutzer, die Änderungen hochladen dürfen, benötigen eine Schreibrolle;
- verpflichtende Review-/PR-Regeln benötigen zusätzlich serverseitigen Branch-/Ruleset-Schutz.

`CODEOWNERS` oder ProjectOS-Rechte allein machen eine Datei im selben Repository nicht unsichtbar.

## Repository-Entwickler-Whitelist

Die Datei

```text
config/authorized_developers.json
```

bleibt die einzige Repository-Quelle für freigegebene GitHub-Entwickler des allgemeinen Quell-Repositories. Diese Liste ist ausdrücklich nicht die ProjectOS-Benutzer-Whitelist und nicht die Zugriffsliste eines separaten privaten Projekt-Repositories.

## Schreibende Änderungen

Die statische HTML-Seite ist bewusst read-only. ProjectOS-Berechtigungsänderungen dürfen nicht direkt aus JavaScript in eine Schattenkopie geschrieben werden.

Für echte Änderungen sind die bestehenden ProjectOS-Pfade vorgesehen:

- `ProjectOSUserManagementChangeService.command_assign_permission(...)`;
- `ProjectOSUserManagementChangeService.command_revoke_permission(...)`;
- `ProjectOSUserManagementCommandAuthorization` für fail-closed Autorisierung;
- vorhandene Command-, Audit- und Persistenzmechanismen.

Die lokale Cockpit-Identitätsauswahl und der Simulationsmodus sind keine Authentifizierung und dürfen deshalb keine echten Datei- oder Berechtigungsänderungen freischalten.

## ProjectOS-Projektbundle anbinden

Ein echtes ProjectOS-v4-Projektbundle kann beim Erzeugen des Cockpits angegeben werden:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

Benutzer-, Berechtigungs- und Projektseite verwenden denselben Bundle-Datenpfad. Ohne Projektbundle werden keine Beispielbenutzer oder Beispielberechtigungen erfunden.

## Nicht Teil der statischen Oberfläche

Nicht durch das statische Cockpit selbst durchgeführt werden:

- Authentifizierung eines Benutzers;
- Umgehung von GitHub-/Dateisystemrechten;
- direktes Schreiben von Berechtigungen aus JavaScript;
- serverseitige GitHub-Ruleset-Aktivierung;
- Speicherung von Zugangstokens im Cockpit.
