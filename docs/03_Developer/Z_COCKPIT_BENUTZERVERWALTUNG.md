# Z_Cockpit – Benutzerverwaltung

Stand: 10. August 2026

Die Benutzerverwaltung stellt vorhandene ProjectOS-Benutzer-, Lifecycle-, Rollen- und Berechtigungsdaten nachvollziehbar dar, ohne eine zweite Benutzer- oder Rechtequelle einzuführen. Zusätzlich besitzt das Cockpit einen rein lokalen Identitäts- und Simulationsmodus für Testzwecke.

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

In diesem Fall zeigt die Benutzerseite korrekt an, dass keine ProjectOS-Benutzerquelle angebunden ist. Es werden keine fachlichen Ersatzbenutzer in ProjectOS erzeugt. Der lokale `Testuser` der Simulation ist davon getrennt und wird niemals persistiert.

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

Die Benutzerliste enthält Anzeigename und technische `user_id`, Status `Aktiv` oder `Deaktiviert`, Profil- und aktive Projektrollen, Anzahl erlaubter und verweigerter Rechte sowie Lifecycle-Ereignisse.

Filter stehen für Freitextsuche, Benutzerstatus, Rolle und Berechtigungszustand zur Verfügung.

## Aktive ProjectOS-Identität im oberen Bereich

Im Kopfbereich des Z_Cockpits wird dauerhaft der lokale Benutzerkontext angezeigt. Sichtbar sind:

- **Aktive ProjectOS-Identität**;
- **Modus** (`Lokale Identität`, `Nicht gewählt` oder `SIMULATION`);
- **Bearbeitungsstatus** aus dem ProjectOS-Benutzer-Lifecycle;
- **Gewichtung** des Benutzerprofils;
- **Rollen**;
- **effektive Rechte** mit Zusammenfassung und aufklappbarer Rechte-Liste.

Wichtig: Das statische Z_Cockpit besitzt derzeit keinen Authentifizierungsserver. Die Auswahl `Eigene Cockpit-Identität` ist deshalb eine **lokale Oberflächenwahl und keine echte Anmeldung**. Sie dient dazu, den persönlichen ProjectOS-Kontext im Cockpit sichtbar zu halten, ohne eine nicht vorhandene Authentifizierung vorzutäuschen.

Die lokale Auswahl wird unter folgendem Browser-Schlüssel gespeichert:

```text
z-cockpit.identity.v1
```

Sie verändert keine Repository- oder ProjectOS-Datei.

## Testuser

Die Benutzerverwaltung enthält einen festen lokalen Testbenutzer für Simulationen:

```text
Name:        Testuser
ID:          00000000-0000-0000-0000-000000000001
Status:      Aktiv
Gewichtung:  100
Rolle:       Testbenutzer
Rechte:      keine persistierten Rechte
```

Die Gewichtung des Testusers kann im Browser zwischen `0` und `1000` verändert werden. Sie bleibt rein lokal und wird nicht persistiert.

ProjectOS trennt Gewichtung und Autorisierung ausdrücklich. Eine veränderte Gewichtung darf daher nicht automatisch Rechte erteilen oder entziehen.

## Simulationsmodus

Der Simulationsmodus wird direkt in der Benutzerverwaltung ein- und ausgeschaltet. Er ist vollständig read-only und besitzt zwei Anwendungsfälle:

1. **Testuser** als neutrale Identität ohne persistierte Rechte;
2. **vorhandenen ProjectOS-Benutzer simulieren**, um dessen bereits durch die echte Domainlogik ausgewerteten Status, Gewichtung, Rollen und effektiven Rechte im oberen Cockpit-Kontext zu sehen.

Der Simulationsmodus kopiert oder verändert keine `ProjectOSUserManagementState`-Objekte. Die Rechte vorhandener Benutzer stammen weiterhin aus dem bestehenden `ProjectOSAuthorizationEvaluator`; DENY, Widerrufe und Benutzer-Lifecycle werden nicht in JavaScript nachgebaut.

Damit ist die Simulation eine Sichtumschaltung und keine parallele Autorisierungsengine.

## Sicherheitsgrenze der Simulation

Solange der Simulationsmodus aktiv ist:

- werden keine ProjectOS-Benutzer-, Rollen- oder Rechtdaten geschrieben;
- bleibt der Testuser rein lokal;
- werden lokale `kicad-z:`-Editoraufrufe im Browser blockiert;
- wird der Modus im oberen Bereich deutlich als `SIMULATION` gekennzeichnet.

Dadurch kann eine simulierte Benutzeridentität nicht versehentlich einen lokalen KiCad-Editoraufruf als reale Aktion auslösen.

## Eigenschaften und Rechte

Nach Auswahl eines realen Benutzers werden rechts Benutzername, technische Benutzer-ID, Lifecycle-Status, Rollen, vorhandene Gewichtung sowie Anzahl und Entscheidung der ausgewerteten Rechte angezeigt.

Für jedes vorhandene Recht werden technische Berechtigung, effektive Entscheidung, wirksame Herkunft, Risikoklasse, aktive Quellen und Widerrufe dargestellt.

Die Herkunft verwendet die bestehenden ProjectOS-Typen Rolle, direkte Zuweisung, Delegation, DENY, Ausnahme, Whitelist und Blacklist.

DENY- und Benutzer-Lifecycle-Regeln werden nicht im Cockpit neu implementiert, sondern durch den bestehenden `ProjectOSAuthorizationEvaluator` ausgewertet.

## Lifecycle

Deaktivierung und Reaktivierung bleiben historische Ereignisse derselben Benutzeridentität. Die Seite zeigt die chronologische Ereigniskette und den daraus resultierenden aktuellen Status.

Eine Deaktivierung löscht den Benutzer nicht. Rollen- und Rechtebezüge bleiben in den ProjectOS-Daten nachvollziehbar erhalten; ihre Wirksamkeit wird durch die vorhandenen Evaluatoren bestimmt.

## Schreibende Aktionen

Die Benutzerseite bleibt absichtlich **read-only**.

Anlegen, Bearbeiten, Deaktivieren, Reaktivieren, Rollenzuweisungen oder Berechtigungsänderungen dürfen nicht als unabhängige JavaScript- oder HTML-Logik implementiert werden. Diese Aktionen müssen über die vorhandenen ProjectOS-Change-/Command-Services laufen und dabei Autorisierung, Audit-Historie, Freigaben und Persistenz einhalten.

Der Testuser und der Simulationsmodus sind davon ausdrücklich ausgenommen, weil sie ausschließlich lokale Browserzustände darstellen und keine fachliche ProjectOS-Entität erzeugen.
