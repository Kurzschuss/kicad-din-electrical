# Z_Cockpit – Benutzerverwaltung

Stand: 10. August 2026

Die Benutzerverwaltung ist die erste Ausbaustufe nach den bisherigen Z_Cockpit-Kernseiten. Sie stellt vorhandene ProjectOS-Benutzer-, Lifecycle-, Rollen- und Berechtigungsdaten nachvollziehbar dar, ohne eine zweite Benutzer- oder Rechtequelle einzuführen.

## Datenquelle

Die fachliche Quelle bleibt `ProjectOSUserManagementState` aus:

```text
distributions/projectos_user_management_persistence.py
```

Darin liegen unter anderem:

- Benutzerprofile;
- Benutzer-Deaktivierungen und -Reaktivierungen;
- Berechtigungszuweisungen und Widerrufe;
- Projektrollen und Beendigungen von Rollenzuweisungen;
- Freigabe- und Nachprüfungsdaten.

Die Cockpit-Seite erzeugt daraus ausschließlich eine read-only Sicht. Die Auswertung verwendet die bereits vorhandenen ProjectOS-Komponenten für Lifecycle, Projektrollen und Autorisierung.

## Z_Cockpit erzeugen

Ohne explizite ProjectOS-Projektdatei:

```text
python -m tools.generate_z_cockpit
```

In diesem Fall zeigt die Benutzerseite korrekt an, dass keine ProjectOS-Benutzerquelle angebunden ist. Es werden keine Beispiel- oder Ersatzbenutzer erzeugt.

Mit einem vorhandenen ProjectOS-v4-Projektbundle:

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

Der Generator lädt dabei ausschließlich das angegebene Bundle über den bestehenden ProjectOS-v4-Lader. Benutzerverwaltungsdaten werden nicht in eine separate Cockpit-Datei kopiert oder zurückgeschrieben.

## Benutzeransicht

Die Seite `Benutzer` folgt dem freigegebenen Cockpit-Muster:

- kompakter Seitentitel mit Erklärung in Klammern;
- Arbeitsliste links;
- fester Eigenschaftenbereich rechts;
- nur Listen-/Detailbereiche scrollen;
- technische IDs bleiben sichtbar.

Die Benutzerliste enthält:

- Anzeigename und technische `user_id`;
- Status `Aktiv` oder `Deaktiviert`;
- Profil- und aktive Projektrollen;
- Anzahl erlaubter Rechte;
- Anzahl verweigerter Rechte;
- Anzahl der Lifecycle-Ereignisse.

Filter stehen für:

- Freitextsuche nach Name oder technischer Benutzer-ID;
- Benutzerstatus;
- Rolle;
- Berechtigungszustand.

## Eigenschaften und Rechte

Nach Auswahl eines Benutzers werden rechts angezeigt:

- Benutzername;
- technische Benutzer-ID;
- Lifecycle-Status;
- Rollen;
- vorhandene Gewichtung;
- Anzahl und Entscheidung der ausgewerteten Rechte.

Für jedes vorhandene Recht werden dargestellt:

- technische Berechtigung;
- effektive Entscheidung;
- wirksame Herkunft;
- Risikoklasse;
- Anzahl aktiver Quellen;
- Anzahl wirksamer Widerrufe.

Die Herkunft verwendet die bestehenden ProjectOS-Typen:

- Rolle;
- direkte Zuweisung;
- Delegation;
- DENY;
- Ausnahme;
- Whitelist;
- Blacklist.

DENY- und Benutzer-Lifecycle-Regeln werden nicht im Cockpit neu implementiert, sondern durch den bestehenden `ProjectOSAuthorizationEvaluator` ausgewertet.

## Lifecycle

Deaktivierung und Reaktivierung bleiben historische Ereignisse derselben Benutzeridentität. Die Seite zeigt die chronologische Ereigniskette und den daraus resultierenden aktuellen Status.

Eine Deaktivierung löscht den Benutzer nicht. Rollen- und Rechtebezüge bleiben in den ProjectOS-Daten nachvollziehbar erhalten; ihre Wirksamkeit wird durch die vorhandenen Evaluatoren bestimmt.

## Schreibende Aktionen

Die aktuelle Benutzerseite ist absichtlich **read-only**.

Anlegen, Bearbeiten, Deaktivieren, Reaktivieren, Rollenzuweisungen oder Berechtigungsänderungen dürfen nicht als unabhängige JavaScript- oder HTML-Logik implementiert werden. Diese Aktionen müssen später über die vorhandenen ProjectOS-Change-/Command-Services laufen und dabei Autorisierung, Audit-Historie, Freigaben und Persistenz einhalten.

Damit ist die Benutzeransicht bereits vollständig auf die vorhandene Domainlogik ausgerichtet, ohne die Sicherheitsregeln zu umgehen.

## Nächste Ausbaustufe

Als nächster geplanter Schritt folgt die **Whitelist- und Berechtigungsverwaltung**.

Dabei müssen weiterhin zwei unterschiedliche Konzepte strikt getrennt werden:

1. ProjectOS-Benutzer-Whitelist/Blacklist/Ausnahmerechte;
2. Repository-Entwickler-Whitelist aus `config/authorized_developers.json`.

Die Detailplanung steht in:

```text
docs/projectos/Z_COCKPIT_AUSBAU_BENUTZER_WHITELIST_ISSUES.md
```
