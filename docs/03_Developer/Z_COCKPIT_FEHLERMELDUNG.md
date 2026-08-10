# Z_Cockpit – Issue- und Fehlermeldungsworkflow

Stand: 10. August 2026

Der Bereich `Fehler melden` unterstützt weiterhin den lokalen/manuellen Bericht und zusätzlich eine **berechtigungsgesteuerte automatische GitHub-Meldung**. Die Automatik ist fail-closed und wird unmittelbar vor jedem GitHub-Schreibzugriff erneut geprüft.

## Lokaler und manueller Weg

Der bestehende Markdown-Bericht mit Kategorie, Kurztitel, technischer Referenz, Beschreibung, Reproduktionsschritten sowie Soll-/Ist-Verhalten bleibt erhalten. Projektstand, Diagnose, Sicherheitsstatus und Repositoryprüfung können gezielt eingebettet werden.

Der Bericht kann unabhängig von GitHub kopiert oder lokal gespeichert werden. `GitHub-Issue vorbereiten` bleibt der manuelle Weg und sendet nicht automatisch.

## Automatisches Senden

Die zusätzliche Aktion

```text
Nach Dublettenprüfung automatisch senden
```

ist nur verfügbar, wenn der beim Cockpit-Start berechnete Status alle Voraussetzungen erfüllt. Beim tatsächlichen Klick werden die Voraussetzungen **erneut lokal vertrauenswürdig geprüft**; die HTML-Anzeige allein entscheidet nicht.

Erforderlich sind:

- offizielles Repository `Kurzschuss/kicad-din-electrical`, also kein Fork/anderer Remote;
- Repositorystand nicht hinter `origin/main`;
- Repositoryprüfergebnis `current=true`;
- mit GitHub CLI (`gh`) authentifizierter Benutzer;
- eindeutige Zuordnung dieses GitHub-Logins zu einem aktiven ProjectOS-Benutzer;
- effektives ProjectOS-Recht `github.issue.auto_submit` im Scope `project`;
- bestätigte sichtbare Berichtsvorschau;
- kein Simulationsmodus.

Ein deaktivierter Benutzer, fehlender Grant, Blacklist/DENY, veraltete Version, Fork, nicht freigegebene lokale Änderung oder nicht sicher prüfbarer Zustand sperrt die Automatik.

Die lokale Cockpit-Identität aus `localStorage` wird **nicht** als Authentifizierung akzeptiert.

## Repositoryprüfung

`tools/check_repository_version.py` ermittelt unter anderem:

- lokalen und Remote-Commit;
- Branch;
- Ahead/Behind;
- Remote-URL und offizielles Repository;
- sauberen/abweichenden Arbeitsbaum;
- Entwicklerfreigabe;
- den tatsächlich mit `gh` authentifizierten GitHub-Login.

Der Login dient ausschließlich der lokalen Rechtezuordnung und wird weiterhin nicht automatisch in den normalen Fehlerbericht eingebettet.

## Dublettenprüfung

Vor einem neuen Issue berechnet ProjectOS einen stabilen SHA-256-Fingerprint aus:

```text
Kategorie + technische Referenz + normalisiertem Kurztitel
```

Danach wird zweistufig geprüft:

1. vorhandene ProjectOS-Issues mit exakt derselben Fingerprint-Markierung;
2. falls kein Marker existiert, bereits **manuell angelegte Issues** mit normalisiert exakt gleichem Titel und – sofern vorhanden – derselben technischen Referenz im Titel/Body.

Damit werden ältere manuelle Meldungen ebenfalls konservativ erkannt, ohne bloß ähnliche Fehler vorschnell zusammenzuführen.

Ist der Fehler bereits vorhanden, wird **kein zweites Issue erzeugt**. Stattdessen ergänzt ProjectOS am bestehenden Issue eine gekennzeichnete Wiederholungsmeldung. Gespeichert beziehungsweise rekonstruierbar sind:

- ursprüngliches Issue und dessen URL;
- ursprünglicher Reporter;
- weitere automatische Reporter;
- Gesamtzahl der erkannten Meldungen;
- Fingerprint;
- Zeitpunkt und ProjectOS-Benutzer-ID der Wiederholungsmeldung.

Das letzte lokale Automatikresultat liegt unter:

```text
build/Z_ISSUE_REPORTING_RESULT.json
```

und wird im Cockpit als letzter Melde-/Dublettenstatus angezeigt. `build/` bleibt nicht versioniert.

## Neues automatisches Issue

Gibt es keine belastbare Dublette, erzeugt der vertrauenswürdige lokale Prozess über `gh issue create` ein neues Issue im offiziellen Repository. Der Body erhält zusätzlich eine unsichtbare ProjectOS-Meldekennung mit Fingerprint und Reporter. Zugangstokens werden nicht in den Bericht geschrieben.

## Datenschutz und Secret-Scan

Die vorhandene sichtbare Vorschau bleibt verbindliche Übergabegrenze. Zusätzlich verweigert die automatische Pipeline Berichte mit typischen Geheimnis-/Token-Mustern, unter anderem GitHub Personal Access Tokens, Private-Key-Headern sowie offensichtlichen Passwort-/Token-/Secret-Zuweisungen.

Weiterhin nicht automatisch in den normalen Bericht übernommen werden:

- vollständige Benutzerverwaltung;
- Rollen-/Berechtigungsdump;
- authentifizierter GitHub-Benutzer;
- Passwörter, Tokens, private Schlüssel und Zugangsdaten;
- ungeprüfte lokale Dateien.

Der Heuristik-Scan ersetzt keine allgemeine Geheimniserkennung; deshalb bleibt die ausdrückliche Vorschauprüfung vor dem Senden erforderlich.

## Vertrauenswürdiger Ablauf

```text
Z_Cockpit-Berichtsvorschau
 -> projectos-z://report?mode=auto
 -> lokaler Windows-Handler
 -> temporäre Berichtdatei
 -> tools.projectos_issue_reporting_cli auto
 -> Repository-/Benutzer-/Rechteprüfung
 -> Secret-Scan
 -> GitHub-Dublettenprüfung
 -> vorhandenes Issue kommentieren ODER neues Issue anlegen
 -> build/Z_ISSUE_REPORTING_RESULT.json
```

Die temporäre Berichtdatei wird nach der Aktion entfernt.

## Sicherheitsgrenzen

- Das statische HTML sendet selbst kein GitHub-Issue.
- Der Browser darf kein GitHub-Token übergeben.
- Die lokale Simulationsidentität kann keine Automatik freischalten.
- Ein vorhandener Button ist kein Berechtigungsbeweis; der lokale vertrauenswürdige Prozess prüft erneut.
- Datei-/Repositoryzugriff und ProjectOS-Rechte bleiben getrennte Schutzebenen.
- Der GitHub-Ruleset wird nicht verändert oder aktiviert.

## Tests

Abgesichert werden insbesondere Repository-/Fork-/Versionsgate, ProjectOS-GitHub-Zuordnung, `github.issue.auto_submit`, Secret-Scan, stabile Fingerprints, ProjectOS-markierte Dubletten, manuell vorhandene Issues sowie die Regel, dass eine Dublette kommentiert und **nicht** als zweites Issue angelegt wird.
