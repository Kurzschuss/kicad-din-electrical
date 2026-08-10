# Z_Cockpit – Berechtigungen und Whitelists

Die Z_Cockpit-Seite `Berechtigungen` führt vorhandene ProjectOS-Berechtigungszuweisungen und die Repository-Entwickler-Whitelist sichtbar zusammen, ohne beide Sicherheitskonzepte zu vermischen.

## Grundsatz

Es gibt zwei strikt getrennte Quellen:

1. **ProjectOS-Benutzerberechtigungen** aus `ProjectOSUserManagementState`;
2. **Repository-Entwickler-Whitelist** aus `config/authorized_developers.json`.

Die Repository-Datei wird nicht in ProjectOS importiert. ProjectOS-Berechtigungen werden umgekehrt nicht in die Repository-Whitelist geschrieben.

## ProjectOS-Berechtigungen

Die Seite wertet die vorhandenen `ProjectOSPermissionAssignment`-Objekte aus. Sichtbar sind unter anderem:

- Benutzer und technische Benutzer-ID;
- Berechtigung;
- Zuweisungs-ID;
- Quelle;
- Wirkung `allow` oder `deny`;
- Scope;
- Risikoklasse;
- Gültigkeitszeitraum;
- Quellenreferenz;
- aktueller Zuweisungsstatus;
- effektive Autorisierungsentscheidung;
- effektive Rechteherkunft.

Unterstützte Quellen des bestehenden ProjectOS-Modells sind:

- Rolle;
- direkte Zuweisung;
- Delegation;
- DENY;
- Ausnahme;
- Whitelist;
- Blacklist.

Die Zuweisungszustände werden read-only als `Aktiv`, `Geplant`, `Abgelaufen` oder `Widerrufen` dargestellt.

## Prioritätsregel

Die ProjectOS-Autorisierung bleibt maßgeblich. Ein wirksames DENY beziehungsweise eine Blacklist-Zuweisung hat Vorrang vor erlaubenden Quellen. Eine vorhandene Whitelist bedeutet deshalb nicht automatisch, dass ein Recht effektiv erlaubt ist.

Die Cockpit-Seite verwendet für die effektive Entscheidung den bestehenden `ProjectOSAuthorizationEvaluator` und implementiert keine zweite Rechteauswertung.

## Repository-Entwickler-Whitelist

Die Datei

```text
config/authorized_developers.json
```

bleibt die einzige Repository-Quelle für freigegebene GitHub-Benutzer.

Die Cockpit-Seite zeigt:

- Vorhandensein der Datei;
- Schema-Version;
- Anzahl der Einträge;
- eingetragene GitHub-Benutzernamen;
- den festen Repositorypfad.

Diese Liste ist ausdrücklich nicht die ProjectOS-Benutzer-Whitelist.

## Filter und Bedienung

Die Berechtigungsansicht folgt dem bestehenden Z_Cockpit-Arbeitsmuster:

- kompakter Seitenkopf mit Erklärung in Klammern;
- Filter und Tabelle links;
- fester Eigenschaftenbereich rechts;
- Filter nach Benutzer, Quelle, Wirkung und Status;
- Freitextsuche nach Benutzername, Benutzer-ID und Berechtigung;
- Auswahl per Maus sowie Enter/Leertaste;
- technische IDs bleiben sichtbar.

## Schreibende Änderungen

Die statische HTML-Seite ist bewusst read-only.

ProjectOS-Berechtigungsänderungen dürfen nicht direkt im Browser in eine lokale Schattenkopie geschrieben werden. Für echte Änderungen sind die bestehenden ProjectOS-Pfade vorgesehen:

- `ProjectOSUserManagementChangeService.command_assign_permission(...)`;
- `ProjectOSUserManagementChangeService.command_revoke_permission(...)`;
- `ProjectOSUserManagementCommandAuthorization` für die fail-closed Autorisierungsprüfung;
- vorhandene Command-/Audit-/Persistenzmechanismen.

Damit bleiben Berechtigungsprüfung, Änderungsverfolgung und Persistenz an einer Stelle.

Änderungen an der Repository-Entwickler-Whitelist erfolgen als normale versionierte Repository-Änderung an `config/authorized_developers.json`. Danach müssen Repository-Validatoren und CI erfolgreich durchlaufen.

## ProjectOS-Projektbundle anbinden

Wie bei der Benutzerseite kann ein echtes ProjectOS-v4-Projektbundle beim Erzeugen des Cockpits angegeben werden:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

Benutzer- und Berechtigungsseite verwenden dabei denselben Bundle-Datenpfad. Ohne Projektbundle werden keine Beispielberechtigungen erfunden. Die Repository-Entwickler-Whitelist bleibt trotzdem sichtbar, weil sie eine eigene Repository-Quelle besitzt.

## Abgrenzung zum nächsten Arbeitspaket

Mit dieser Seite ist die Whitelist- und Berechtigungsverwaltung auf Sicht-, Prüf- und Architektur-Ebene integriert. Der nächste geplante Z_Cockpit-Ausbau ist der Issue- und Fehlermeldungsworkflow.

Nicht Teil dieser Seite sind:

- direktes Schreiben von Berechtigungen aus statischem HTML;
- GitHub-Issue-Erstellung;
- GitHub-Ruleset-Aktivierung;
- Speicherung von Zugangstokens im Cockpit.
