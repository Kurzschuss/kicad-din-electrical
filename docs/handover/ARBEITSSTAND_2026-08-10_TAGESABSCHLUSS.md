# Arbeitsstand / Tagesabschluss – 10. August 2026

Stand: 10. August 2026, Tagesabschluss  
Repository: `Kurzschuss/kicad-din-electrical`  
Maßgebliche Quelle: `main`  
`main`-Stand zu Beginn dieses Handovers: `2cdef6ffced74b0582b6c1cf7fe2797a2dc59afe` (Merge von PR #203)

## Zweck dieses Handovers

Dieses Dokument ist der **abschließende Gesamt-Handover für den lokalen Arbeitstag 10.08.2026**. Es fasst die heute erreichten fachlichen, visuellen, technischen und sicherheitsrelevanten Stände zusammen und dokumentiert, was noch offen ist.

Für die Fortsetzung gilt:

- `main` ist die Single Source of Truth.
- Dieses Dokument ist für den nächsten Arbeitsblock der maßgebliche Tagesabschluss.
- Frühere Handover vom 10.08.2026 bleiben als historische Zwischenstände erhalten, werden aber durch diesen Gesamtstand ergänzt beziehungsweise für die Fortsetzung überholt.
- Bereits ausdrücklich freigegebene Symbol- und Cockpit-Geometrien werden nicht ohne neuen ausdrücklichen Änderungswunsch erneut umgebaut.
- Der GitHub-Ruleset bleibt separat blockiert und wird nicht automatisch als nächster Arbeitspunkt behandelt.

---

# 1. Heute freigegebene und zu respektierende Baselines

## 1.1 MCB-Geometrie

Die MCB-Geometrie ist freigegeben und bleibt unverändert, solange keine neue ausdrückliche Anforderung gestellt wird.

Technische Referenzen:

- `Z_MCB:MCB`
- `Z_MCB:MCB_3P`

Wichtige Freigabepunkte:

- 1P- und 3P-Darstellung sind visuell abgenommen.
- 3P besitzt die freigegebenen Polabstände und Trennungsstriche.
- 3P-Varianten sind datengetrieben vorhanden.
- Keine spätere Arbeit des heutigen Tages hat die MCB-Geometrie verändert.

Der frühe Tagesstand ist detailliert dokumentiert in:

```text
docs/handover/ARBEITSSTAND_2026-08-10_MCB_Z_COCKPIT.md
```

## 1.2 RCD 2P

Der 2P-RCD ist freigegeben und darf ohne neue ausdrückliche Anforderung nicht geometrisch verändert werden.

Technische Symbol-ID:

```text
Z_RCD:RCD
```

Freigegebene wesentliche Merkmale:

- Anschlüsse `1`, `3/N`, `2`, `4/N`;
- Testzweig links mit `T` und langem Widerstand;
- drei Betätigungs-/Kontakthöhen auf gleicher Höhe;
- lange gestrichelte mechanische Kopplung durch die Kontaktzentren;
- Kreuzkasten rechts auf der freigegebenen Höhe;
- Summenstromwandler und Auslöseeinheit im unteren Bereich;
- schwarzer gefüllter Sensorkern;
- freigegebene untere horizontale Erfassungslinie;
- keine nachträgliche zusätzliche Absenkung dieser Linie.

Heute wurden für 2P insgesamt 64 herstellerneutrale Varianten aufgebaut und anschließend die Symbolgeometrie an die Referenzvorlage angeglichen und final freigegeben.

## 1.3 RCD 4P / 3+N

Der 4P-RCD ist ebenfalls freigegeben.

Technische Symbol-ID:

```text
Z_RCD:RCD_4P
```

Wichtige Merkmale:

- 8 Pins;
- oben `1`, `3`, `5`, `7/N`;
- unten `2`, `4`, `6`, `8/N`;
- 3+N-Funktionsdarstellung;
- Testschaltung, Summenstromwandler, mechanische Kopplung und rechte Auslöseeinheit folgen der freigegebenen 2P-Designsprache;
- 72 herstellerneutrale Varianten vorhanden.

## 1.4 Z_Cockpit – Bibliotheksansicht

Die Bibliotheksansicht ist visuell freigegeben und soll nicht grundlegend neu gestaltet werden.

Verbindliche Bedienlogik:

- kompakter Seitenkopf;
- Kennzahlen in den Filtern statt zusätzlicher Summary-Kacheln;
- Bibliotheken links als filterbare Liste/Tabelle;
- Detailbereich einer Bibliothek klappt direkt unter der Bibliothekszeile auf;
- immer nur eine Bibliothek gleichzeitig geöffnet;
- rechter Eigenschaftenbereich bleibt fest;
- Symbolvorschau bleibt im festen rechten Bereich;
- Geräte-IDs liegen darunter in einem **separaten vertikal scrollbareren Bereich**;
- lange Geräte-IDs werden umgebrochen;
- kein unnötiges horizontales Scrollen;
- linker Bibliotheksbereich und rechte Geräte-ID-Liste besitzen getrennte Scrolllogik.

## 1.5 Einheitliche Z_Cockpit-Seitenköpfe

Die Seitenköpfe folgen jetzt dem freigegebenen Bibliotheksmuster:

```text
Seitentitel (kurze Erklärung des Menüpunktes)
```

Die Erklärung steht in derselben ersten Zeile und nicht mehr als große zweite Unterzeile. Einstellungen und Sicherheit wurden ausdrücklich an dieses Muster angepasst; weitere geeignete Seiten werden beim Generieren entsprechend normalisiert.

---

# 2. Heute umgesetzte Arbeiten – Gesamtübersicht

## 2.1 Früher Tagesblock: MCB und Bibliotheksansicht

PR-Kette:

| PR | Inhalt | Ergebnis |
|---|---|---|
| #174 | MCB 3P Trennungsstriche feinabstimmen | gemergt |
| #175 | Bibliotheken als filterbare Tabellenansicht | gemergt |
| #176 | früher Zwischen-Handover | gemergt |
| #177 | Bibliothekskopf kompakter / Filterkennzahlen | gemergt |
| #178 | Bibliotheksdetails direkt in der Liste aufklappen | gemergt |
| #179 | Symbolvorschau und Geräte-IDs in rechten Inspektor | gemergt |
| #180 | Eigenschaften fixieren, nur Geräte-IDs scrollen | gemergt |
| #181 | Tageszwischenstand MCB/Z_Cockpit dokumentieren | gemergt |

Der Stand nach PR #180 wurde ausdrücklich als passend bestätigt und ist weiterhin die Layoutbasis.

## 2.2 RCD-Ausbau

### PR #182 – RCD 2P und 64 Varianten

Umgesetzt:

- funktionsgerechte 2P-FI/RCD-Darstellung;
- 64 Varianten;
- RCD-spezifische Kenngrößen im Gerätekatalog;
- Vorschau, Tests und Referenzdokumentation.

### PR #183 – Referenztreue 2P-Geometrie

Umgesetzt:

- Hauptkontakte, Testzweig, Summenstrom-/Auslösebereich neu proportioniert;
- sichtbare Anschlusskennzeichnungen;
- gestrichelte mechanische Kopplung und Sensorkern korrekt in Vorschau.

### PR #184 – final freigegebener 2P-Stand

Umgesetzt:

- ausdrücklich freigegebene Geometrie übernommen;
- verworfene spätere Linienabsenkung **nicht** übernommen.

### PR #185 – RCD 4P / 3+N und 72 Varianten

Umgesetzt:

- `Z_RCD:RCD_4P`;
- 72 Varianten;
- Vorschau, Katalogdaten, Tests und Referenzdokumentation.

---

# 3. Projektanalyse und vollständiger Z_Cockpit-Kernausbau

## 3.1 Projektvalidator – PR #186

Neu:

```text
tools/project_validator.py
```

Der Validator bündelt den globalen Projektzustand über stabile Prüfungen `PRJ-001` bis `PRJ-010`.

Geprüft werden unter anderem:

- Projektmodell;
- KiCad-Bibliotheken;
- Gerätekatalog;
- generierte Gerätevarianten;
- Bibliotheksreferenzen;
- Qualitätsbericht;
- Symbolvorschauen;
- HTML-Referenzen;
- Z_Cockpit-Seitenmodell.

Warnungen bleiben nicht blockierend; echte Konsistenzfehler und Generator-Drift blockieren.

## 3.2 Hersteller – PR #187

Neue Z_Cockpit-Seite:

- Hersteller;
- Serien;
- Gerätefamilien;
- Quellenstatus;
- Geräte-IDs;
- fester rechter Inspektor;
- separate Geräte-ID-Scrollliste.

`Generic` wird sichtbar als `Herstellerneutral` dargestellt, ohne den technischen Katalogwert zu verfälschen.

## 3.3 Diagnose – PR #188

Neue read-only Diagnose-Arbeitsliste aus:

- Projektvalidator;
- repositoryweiter Projektanalyse;
- später zusätzlich persistierten Laufzeitdiagnosen.

Keine erfundenen Runtime-Daten.

## 3.4 Dokumentation – PR #189

Neue Dokumentationsseite:

- indexiert Markdown-Dokumente aus dem Repository;
- Bereichsfilter und Suche;
- fester Dokumentinspektor;
- Originaldateien bleiben Single Source of Truth.

## 3.5 Einstellungen – PR #190

Neue Einstellungsseite:

- Repository-/Projektwerte read-only;
- lokale UI-Einstellungen ausschließlich in Browser-`localStorage`;
- keine Rückschreiblogik in `project_state.yaml` oder fachliche Projektdateien.

## 3.6 Kompakte Seitenköpfe – PR #191 / #192

Umgesetzt:

- Start und Qualität oben kompakter;
- Einstellungen und Sicherheit an Bibliotheksmuster angeglichen;
- Erklärungen in Klammern in der ersten Titelzeile;
- damalige nächste Ausbaufolge dokumentiert: Benutzer → Berechtigungen → Fehlermeldung.

---

# 4. Benutzerverwaltung und Simulation

## 4.1 Benutzerverwaltung – PR #193

Neue Seite `Benutzer`.

Angezeigt werden aus vorhandenen ProjectOS-Daten:

- Benutzer-ID;
- Bezeichnung;
- Aktiv-/Deaktiviertstatus;
- Rollen;
- effektive Rechte;
- Herkunft der Rechte;
- Risikoklassen;
- Widerrufe;
- Lifecycle-Historie.

Ohne Projektbundle werden keine Benutzer erfunden.

## 4.2 Testuser, aktive Identität und Simulationsmodus – PR #199

Oben im Z_Cockpit gibt es eine kompakte Anzeige:

```text
Aktive ProjectOS-Identität
```

Dort sichtbar:

- Benutzer;
- Modus;
- Bearbeitungs-/Benutzerstatus;
- Gewichtung;
- Rollen;
- effektive Rechte.

Testuser:

```text
ID: 00000000-0000-0000-0000-000000000001
Bezeichnung: Testuser
Status: Aktiv
Standardgewichtung: 100
Rolle: Testbenutzer
persistierte Rechte: keine
```

Die Testuser-Gewichtung ist lokal simulierbar. Gewichtung ist **keine Berechtigung** und verändert die Autorisierungsentscheidung nicht.

Wichtige Sicherheitsgrenze:

> Die im statischen Cockpit ausgewählte Identität ist keine echte Anmeldung und kein Authentifizierungsbeweis.

Im Simulationsmodus sind lokale KiCad-Schreib-/Editoraktionen blockiert, wo dies sicherheitsrelevant ist.

---

# 5. White-/Blacklist und Rechteverwaltung

## 5.1 Berechtigungsseite – PR #194

Eigener Bereich `Berechtigungen`.

Darstellbare Quellen:

- Rolle;
- direkte Zuweisung;
- Delegation;
- DENY;
- Ausnahme;
- Whitelist;
- Blacklist.

Zusätzlich sichtbar:

- Scope/Zugriffsbereich;
- Risikoklasse;
- Gültigkeit;
- Widerruf;
- effektive Entscheidung.

Grundregel:

```text
wirksames DENY / Blacklist hat Vorrang vor erlaubenden Quellen
```

Die Repository-Entwickler-Whitelist bleibt getrennt von der ProjectOS-Benutzer-Whitelist.

## 5.2 Governance-Ausbau – PR #202

Die Benutzer-, Rechte- und Reportingverwaltung wurde zu einem gemeinsamen Governance-Modell zusammengeführt.

Benutzerprofile unterstützen jetzt unter anderem:

- Bezeichnung;
- Gewichtung;
- optionale eindeutige GitHub-Zuordnung (`github_login`).

Verbindlicher Rechtekatalog:

```text
project.file.read
project.file.write
project.file.share
project.file.admin
project.user.manage
project.permission.manage
cockpit.view
cockpit.edit
github.issue.prepare
github.issue.auto_submit
```

Zugriffsbereiche können projektweit oder seitenbezogen sein, zum Beispiel:

```text
project
page:start
page:projekt
page:geraete
page:bibliotheken
page:hersteller
page:qualitaet
page:diagnose
page:sicherheit
page:dokumentation
page:einstellungen
page:benutzer
page:berechtigungen
page:fehlerbericht
```

Reale schreibende Governance-Aktionen folgen dem vertrauenswürdigen Pfad:

```text
gh-authentifizierter GitHub-Benutzer
 -> eindeutige ProjectOS-github_login-Zuordnung
 -> ProjectOSAuthorizationEvaluator
 -> ProjectOSUserManagementChangeService
 -> DinEditorProjectManager.save(...)
```

`localStorage` und der Simulationsmodus sind niemals Authentifizierungsquellen.

---

# 6. ProjectOS-Projektdateien und Mehrbenutzerbetrieb

## 6.1 Projektdatei direkt aus dem Z_Cockpit – PR #200

Neue Seite `Projekt` mit `Neues Projekt`.

Ablauf unter Windows:

1. Projektname im Cockpit angeben.
2. Lokales `projectos-z:`-Protokoll wird verwendet.
3. Windows zeigt einen normalen `Speichern unter`-Dialog.
4. Der Browser darf keinen beliebigen Pfad einschleusen.
5. `DinEditorProjectManager` erzeugt ein gültiges ProjectOS-v4-Bundle.
6. Das Projekt wird lokal als aktiv gemerkt.
7. Das Cockpit wird mit `--project-bundle` neu erzeugt.
8. Beim nächsten Start wird das aktive, noch gültige Projekt automatisch wieder geladen.

Lokaler Aktivzustand:

```text
build/Z_COCKPIT_ACTIVE_PROJECT.json
```

Dieser Zustand bleibt lokal und gehört nicht als gemeinsame Projektdatei in GitHub.

## 6.2 Schutzklassen und Dateirechte – PR #201

Schutzklassen:

```text
private_team
restricted_local
repository_visible
```

Bedeutung:

- `private_team`: vertrauliche Teamarbeit, Standard für separates privates Projekt-Repository;
- `restricted_local`: vertraulich lokal außerhalb des allgemeinen Repositories;
- `repository_visible`: bewusst im allgemeinen Repository sichtbar.

Für vertrauliche Varianten wird ein Speicherort im allgemeinen Quell-Repository technisch abgewiesen.

Verbindliche ProjectOS-Dateirechte:

```text
project.file.read   -> Projektdatei lesen
project.file.write  -> Projektdatei ändern
project.file.share  -> Projekt teilen/freigeben
project.file.admin  -> Projektzugriff verwalten
```

Wichtige Sicherheitsgrenze:

> GitHub kann innerhalb eines einzelnen Repositories nicht eine einzelne Datei vor bestimmten Repository-Lesern verbergen.

Deshalb gilt für vertrauliche Teamprojekte:

```text
kicad-din-electrical
  -> Programm, Bibliotheken, Z_Cockpit

separates privates GitHub-Projekt-Repository
  -> konkrete *.projectos.json Projektdatei
```

ProjectOS-Rechte und Repository-/Dateisystemrechte sind zwei getrennte Schutzebenen.

---

# 7. Fehlerberichte und automatische GitHub-Meldungen

## 7.1 Grundworkflow – PR #195

Neue Seite `Fehler melden`.

Der Bericht enthält strukturiert:

- Kategorie;
- Kurztitel;
- technische Referenz;
- Beschreibung;
- Reproduktionsschritte;
- Soll-Verhalten;
- Ist-Verhalten;
- optional Projekt-/Diagnose-/Sicherheits-/Repositorystatus.

Benutzer-/Berechtigungsbestände, Tokens, Schlüssel, Passwörter und ungeprüfte Dateiinhalte werden nicht automatisch übernommen.

Der lokale Markdown-Bericht funktioniert unabhängig von GitHub.

## 7.2 Automatische GitHub-Meldung – PR #202

Zusätzlich existiert eine berechtigungsgesteuerte automatische Meldung.

Erforderliches ProjectOS-Recht:

```text
github.issue.auto_submit
```

Vor jedem automatischen Senden wird **erneut** geprüft:

- offizielles Repository `Kurzschuss/kicad-din-electrical`;
- kein Fork/kein fremdes Remote;
- lokaler Stand nicht hinter `origin/main`;
- Repositoryprüfung `current=true`;
- zulässiger Arbeitsbaum/Repositoryzustand;
- `gh` ist authentifiziert;
- GitHub-Login ist eindeutig einem aktiven ProjectOS-Benutzer zugeordnet;
- effektives `github.issue.auto_submit` ist vorhanden;
- kein Blacklist-/DENY-Gegentreffer;
- keine Simulation;
- sichtbare Berichtsvorschau wurde bestätigt;
- Secret-Heuristik findet keine typischen Tokens/Passwörter/Private-Key-Muster.

Die lokale Cockpit-Identität wird dabei **nicht** als Authentifizierung akzeptiert.

## 7.3 Dublettenprüfung

ProjectOS bildet einen stabilen SHA-256-Fingerprint aus:

```text
Kategorie + technische Referenz + normalisiertem Kurztitel
```

Prüfreihenfolge:

1. vorhandenes ProjectOS-Issue mit gleichem Fingerprint;
2. konservative Suche nach manuell vorhandenen Issues mit gleichem normalisierten Titel und passender technischer Referenz.

Wenn eine Dublette existiert:

- kein zweites Issue anlegen;
- bestehendes Issue um Wiederholungsmeldung ergänzen;
- ursprüngliches Issue/URL nachvollziehbar halten;
- ursprünglichen Reporter und weitere Reporter nachvollziehbar halten;
- Meldeanzahl nachvollziehbar halten;
- ProjectOS-Benutzer-ID und Zeitpunkt der Wiederholungsmeldung erfassen.

Letztes lokales Ergebnis:

```text
build/Z_ISSUE_REPORTING_RESULT.json
```

---

# 8. 3D-Vorschauen – PR #196

Die 3D-Infrastruktur unterscheidet bewusst zwischen echten Modellen und technischen Vorschauen.

Statusmodell:

```text
Modell
Modellreferenz fehlt
Hüllkörper
Fehlt
Nicht zugeordnet
```

Ein echtes Modell zählt nur, wenn:

- der KiCad-Footprint eine `model`-Referenz besitzt;
- diese auf eine tatsächlich vorhandene Repositorydatei auflösbar ist.

Vorgesehener Repositorypfad:

```text
3dmodels/Z_3DModell.3dshapes/
```

Unterstützte Formate:

- `.step`;
- `.stp`;
- `.wrl`.

Eine isometrische Hüllkörperansicht aus vorhandener `F.Fab`-Geometrie ist **kein echtes 3D-Modell** und wird auch nicht als solches gezählt.

Es werden keine fehlenden Herstellergehäuse oder STEP-Daten erfunden.

---

# 9. Direkte KiCad-Editoraufrufe – PR #197

Unter Windows existiert das lokale URI-Schema:

```text
kicad-z:
```

Sicherheitsregeln:

- Registrierung nur unter HKCU;
- keine Administratorrechte nötig;
- Browser kann nur definierte Aktionen anstoßen;
- keine beliebigen Executables;
- keine beliebigen Dateipfade;
- keine freien Shell-Befehle.

Footprint:

- zugeordnete `.kicad_mod`-Datei kann direkt im Footprint-Editor geöffnet werden.

Symbol:

- technische Referenz `Bibliothek:Symbol` wird geprüft;
- Referenz wird in die Zwischenablage gelegt;
- KiCad-Symbol-Editor wird geöffnet;
- keine instabile, nicht offiziell verfügbare direkte Symbolselektion wird nachgebaut.

---

# 10. Persistierte Laufzeitdiagnosen – PR #198

Persistiert wird die fachliche Quelle der Diagnose:

- ProjectOS-Wissensknoten;
- typisierte Beziehungen;
- bekannte Message-IDs;
- bekannte Correlation-IDs.

Nicht persistiert werden:

- Ampeln;
- abgeleitete Diagnoseergebnisse;
- Reparaturempfehlungen.

Lokaler Snapshot:

```text
build/PROJECTOS_RUNTIME_MEMORY.json
```

Die Diagnose wird beim Cockpit-Erzeugen reproduzierbar neu berechnet.

Ein fehlender Snapshot ist nicht blockierend.

Das äußere ProjectOS-Projektbundle bleibt v4; hierfür wurde kein Projektdatei-Migrationszwang eingeführt.

---

# 11. Qualitätshandbuch – PR #203

Der erste noch offene Punkt der langfristigen Roadmap wurde heute ebenfalls abgeschlossen:

```text
docs/00_Project/LIBRARY_GUIDELINES.md
```

Das Dokument ist jetzt die verbindliche Paket- und Freigaberichtlinie.

Es regelt unter anderem:

- Quellenhierarchie;
- Gerätepaketprinzip;
- Sprache und technische Kennungen;
- Symbolstandard;
- Footprintstandard;
- kanonische `Z_Footprint_Policy`;
- Gerätekatalogfelder;
- Varianten und Generatoren;
- 3D-Modelle;
- Dokumentation;
- Tests;
- Ausnahmen;
- Definition of Done;
- Qualitätsstatus;
- Paket-Reifegrade.

## 11.1 Kanonische Footprint Policy

Für neue und fachlich überarbeitete Symbole gilt:

```text
Z_Footprint_Policy
```

Zulässige Werte:

```text
required
optional
none
```

Das historische Feld `Footprint Policy` wird nur noch als Legacy-Lesepfad unterstützt.

## 11.2 Qualitätsstatus versus Reifegrad

Maschinenlesbarer Qualitätsstatus:

```text
kicad_conform
z_conform
needs_rework
temporarily_accepted
```

Paket-Reifegrad:

```text
Entwurf
Geprüft
Praxisgetestet
```

Diese Begriffe sind absichtlich getrennt.

`Geprüft` verlangt mindestens:

- Symbol;
- Gerätedaten;
- Dokumentation;
- automatisierte Tests;
- nachvollziehbare Evidenzreferenzen;
- keinen `needs_rework`-Status.

`Praxisgetestet` verlangt zusätzlich ein dokumentiertes Beispielprojekt beziehungsweise einen praktischen Nachweis.

Diese Mindestbedingungen werden jetzt technisch durch `tools/generate_package_progress.py` geprüft.

---

# 12. Aktueller ProjectOS-/Z_Cockpit-Projektstatus

Im zentralen `project_state.yaml` sind alle normalen Bibliotheks-, Z_Cockpit- und Qualitätspunkte auf `done`.

Erledigt sind insbesondere:

```text
Bibliotheken / Gerätekatalog / Vorschauen / Bibliotheksgesundheit
Z_Cockpit Seitenmodell / Navigation / Projektstatus
Projektdatei-Workflow
Projektdatei-Zugriffsschutz
Sicherheit
Hersteller
Diagnose
Dokumentation
Einstellungen
Benutzerverwaltung
Benutzer-Simulation
Whitelist-/Berechtigungsverwaltung
Issue-/Fehlermeldung
Zugriffs-/Reporting-Governance
3D-Vorschauen
KiCad-Editoraufrufe
Laufzeitdiagnose-Persistenz
Qualitätshandbuch
Projektvalidator
Versionsprüfung
Originalitätsprüfung
Entwickler-Whitelist
CODEOWNERS
```

Derzeit gibt es im zentralen Projektmodell **keine normale Aufgabe mit `planned` oder `in_progress`**.

Einziger separat geführter Block:

```text
GitHub-Ruleset gemeinsam prüfen und aktivieren = blocked
```

Dieser Punkt wird nur nach eigener ausdrücklicher Entscheidung bearbeitet.

---

# 13. CI- und Qualitätsstand zum Tagesabschluss

Letzter vollständiger Lauf vor diesem Dokument:

```text
ProjectOS complete test suite #575 = SUCCESS
```

Der vorherige vollständige Implementierungslauf #574 bestätigte unter anderem:

```text
832 Tests bestanden
Python-Syntax grün
Z_ Quality Release Profile grün
KiCad-Bibliotheksvalidator: 0 Fehler
Gerätevarianten aktuell
Gerätekatalog: 0 Fehler
Bibliotheksreferenzen aktuell
Qualitätsbericht aktuell
Symbolvorschauen aktuell
3D-Vorschauen aktuell
HTML-Referenz aktuell
HTML-Gerätekatalog aktuell
ProjectOS-Projektvalidator: 10/10 bestanden
Z_Cockpit-Erzeugung erfolgreich
```

Der Bibliotheksvalidator meldet weiterhin nicht blockierende Hinweise, insbesondere fehlende Hersteller-/Datenblattangaben bei herstellerneutralen oder noch nicht vollständig ausgebauten Bibliotheken. Solche Felder werden nicht mit erfundenen Daten gefüllt.

---

# 14. Heute relevante PR-Kette

Für die Nachvollziehbarkeit umfasst der heutige lokale Arbeitsblock im Wesentlichen PR #174 bis #203.

| PR | Schwerpunkt |
|---|---|
| #174 | MCB 3P Feintuning |
| #175 | Bibliotheks-Tabelle |
| #176 | Zwischen-Handover |
| #177 | kompakter Bibliothekskopf |
| #178 | Inline-Bibliotheksdetails |
| #179 | rechter Symbolinspektor |
| #180 | fixer Eigenschaftenbereich / Geräte-ID-Scroll |
| #181 | MCB/Z_Cockpit-Tageszwischenstand |
| #182 | RCD 2P + 64 Varianten |
| #183 | RCD 2P Referenzangleichung |
| #184 | final freigegebener RCD-2P-Stand |
| #185 | RCD 4P/3+N + 72 Varianten |
| #186 | Projektvalidator |
| #187 | Herstellerseite |
| #188 | Diagnoseseite |
| #189 | Dokumentationsseite |
| #190 | Einstellungen |
| #191 | Start/Qualität kompakter |
| #192 | einheitliche Seitenköpfe / Ausbauplanung |
| #193 | Benutzerverwaltung |
| #194 | Whitelist-/Berechtigungsansicht |
| #195 | Fehlerbericht-Workflow |
| #196 | 3D-Vorschauen |
| #197 | KiCad-Editoraufrufe |
| #198 | Laufzeitdiagnose-Persistenz |
| #199 | Testuser / aktive Identität / Simulation |
| #200 | Projektdatei direkt im Cockpit erzeugen |
| #201 | Schutzklassen und ProjectOS-Dateirechte |
| #202 | Benutzer-/Zugriffs-Governance + automatische GitHub-Meldung |
| #203 | verbindliches Qualitätshandbuch |

Der Stand nach PR #203 ist der Ausgangspunkt für die nächste Sitzung.

---

# 15. Was noch ansteht – langfristige Roadmap

Der zentrale ProjectOS-Plan enthält aktuell keine normale offene Aufgabe. Die längerfristige Projekt-Roadmap enthält jedoch noch erhebliche Arbeit.

## 15.1 Phase B – Benutzerdokumentation

Noch offen:

- weitere verständliche Screenshots ergänzen;
- Beispielprojekte Schritt für Schritt dokumentieren.

**Dies ist derzeit der erste normale Roadmap-Bereich für die Fortsetzung.**

## 15.2 Phase E – priorisierter Bibliotheksausbau

Die Gerätefamilien sollen als vollständige Pakete ausgebaut werden:

1. MCB – Leitungsschutzschalter;
2. RCD – Fehlerstrom-Schutzeinrichtung;
3. RCBO – kombinierter FI/LS;
4. Hauptschalter;
5. Lasttrennschalter;
6. Schütze;
7. Hilfsschalter;
8. Reihenklemmen;
9. Netzteile;
10. Relais;
11. Motorschutz;
12. Überspannungsschutz;
13. Sicherungen;
14. Transformatoren;
15. Messgeräte;
16. Meldegeräte;
17. SPS-Komponenten.

Wichtig zur Einordnung:

- MCB und RCD besitzen heute bereits weit fortgeschrittene Symbol-, Geräte-, Dokumentations- und Teststände.
- Die Paketfortschrittsdaten führen MCB und RCD derzeit als `Geprüft`.
- Für `Praxisgetestet` fehlt insbesondere noch ein dokumentiertes Beispiel-/Praxisprojekt.
- RCBO und Hauptschalter sind noch `Entwurf` und benötigen weiteren Paketaufbau.
- Die bereits freigegebenen MCB- und RCD-Geometrien sind dabei nicht als „noch einmal neu zeichnen“ zu verstehen.

### Noch offene MCB-Paketpunkte laut Roadmap

Die Roadmap führt formal weiterhin:

- Symbol fachlich und grafisch prüfen;
- sinnvolle Varianten festlegen;
- Footprint-Entscheidung dokumentieren;
- Gerätekatalog und Serien vervollständigen;
- SVG- und HTML-Dokumentation ergänzen;
- Benutzeranleitung erstellen;
- Beispielprojekt anlegen;
- Tests ergänzen;
- Qualitätsstatus vergeben.

Viele dieser Punkte sind technisch heute bereits teilweise oder weitgehend erfüllt. Vor einem pauschalen Abhaken soll der neue verbindliche Paketstandard angewandt und der tatsächliche Evidenzstand je Punkt geprüft werden. Das Beispielprojekt ist eindeutig noch offen.

## 15.3 Phase F – Beispielprojekte und Vorlagen

### Einsteigerbeispiele

- erstes Symbol;
- erstes Gerät;
- erste Verbindung;
- Beschriftung und Referenzkennzeichen;
- ERC ausführen und Ergebnisse einordnen.

### Installation

- Lichtschaltung;
- Steckdosenstromkreis;
- Wechselschaltung;
- Kreuzschaltung;
- Tasterschaltung.

### Unterverteilung / Energieverteilung

- kleine Unterverteilung;
- Unterverteilung mit FI/LS;
- Unterverteilung mit mehreren RCD-Gruppen;
- Reservefelder und Erweiterungsplanung;
- Garagenverteilung;
- Gartenverteilung;
- Zähleranlage Einfamilienhaus;
- Baustromverteiler.

### Schaltschrank / Steuerung

- Schützschaltung;
- Motorstarter;
- Zeitrelais;
- Netzteil;
- SPS-Grundaufbau;
- Klemmenplan.

### Zukunftsprojekte

- Wärmepumpe;
- Wallbox;
- PV-Vorbereitung;
- Netzwerkverteiler;
- Kleinsteuerung.

Jedes Beispiel soll ein eigenes `README.md` mit Ziel, Voraussetzungen, Arbeitsschritten, verwendeten Bibliotheken und Einsteigerhinweisen erhalten.

## 15.4 Phase G – Referenz und Wissensplattform

Noch offen:

- Normen- und Symbolreferenz;
- Beschreibungen und typische Einsatzgebiete je Symbol;
- dokumentierte Symbol-zu-Footprint-Zuordnungen;
- Beispielschaltungen je Gerätefamilie;
- Qualitätsstatus in HTML und Gerätekatalog;
- Footprintvorschauen im langfristigen Referenzumfang weiter ausbauen.

Hinweis: Im Z_Cockpit existieren bereits Footprint-/3D-bezogene Vorschau- und Statusfunktionen. Der Roadmap-Punkt ist daher beim späteren Abarbeiten gegen den tatsächlich bereits erreichten Generator-/UI-Stand zu prüfen und gegebenenfalls präziser zu formulieren.

## 15.5 Phase H – Kompatibilität und Veröffentlichung

Noch offen:

- Kompatibilitätsmatrix für unterstützte KiCad-Versionen;
- Statusmatrix für Symbol, Footprint, Generator, HTML und Tests;
- GitHub Pages einrichten;
- Dokumentation online veröffentlichen;
- Downloadbereich;
- Release-Automatisierung weiter vervollständigen;
- automatische Aktualisierung durch GitHub Actions.

## 15.6 Phase I – langfristige Werkzeuge

Noch offen:

- Komponenten- und Wissensdatenbank ausbauen;
- optionaler KiCad-Installationsassistent oder Plugin;
- Projektassistent für typische Anlagen;
- automatische Material- und Stücklisten aus dem Gerätekatalog;
- Hersteller- und Datenblattlisten.

## 15.7 Phase J – Ausbildung

Noch offen:

- Übungen und Beispielaufgaben;
- Musterlösungen;
- Arbeitsblätter;
- Tutorials für Einsteiger;
- Material für Schulen und Ausbildungsstätten.

## 15.8 Separat blockiert: GitHub-Ruleset

Status:

```text
blocked
```

Der Ruleset wird **nicht** mit den normalen Roadmap-Aufgaben vermischt. Aktivierung beziehungsweise Änderung erst nach ausdrücklicher gemeinsamer Prüfung/Freigabe.

---

# 16. Empfohlene Reihenfolge für den nächsten Arbeitsblock

Ohne neue Priorisierung ist die sinnvollste Fortsetzung aus dem aktuellen Roadmap-Stand:

1. **Benutzerdokumentation mit verständlichen Screenshots ergänzen.**
2. **Erstes durchgängiges Schritt-für-Schritt-Beispielprojekt erstellen.**
3. Dieses Beispiel als Praxisnachweis verwenden, um das bereits `Geprüft`e MCB-Paket in Richtung `Praxisgetestet` zu bringen.
4. Danach denselben Paket-/Praxisprozess für RCD anwenden.
5. Anschließend RCBO als nächste Gerätefamilie fachlich vervollständigen.
6. Parallel nur dann weitere Governance-/Security-Arbeit beginnen, wenn dafür ein konkreter neuer Bedarf besteht.
7. GitHub-Ruleset weiterhin separat behandeln.

Diese Reihenfolge ist eine Arbeitsableitung aus der Roadmap, kein neu eingetragener `planned`-Status in `project_state.yaml`.

---

# 17. Sicherheits- und Architekturregeln für die Fortsetzung

Diese Punkte dürfen in späteren Arbeiten nicht verloren gehen:

1. `main` bleibt Single Source of Truth.
2. Statisches Z_Cockpit-HTML ist **keine Authentifizierungsgrenze**.
3. Browser-`localStorage` darf nur lokale UI-/Simulationszustände halten, keine echten Sicherheitsrechte.
4. Reale Governance-Aktionen verwenden den tatsächlich `gh`-authentifizierten Benutzer und dessen eindeutige ProjectOS-Zuordnung.
5. Blacklist/DENY hat Vorrang vor erlaubenden Quellen.
6. Vertrauliche Projektdateien gehören nicht in das allgemeine Quell-Repository.
7. Tatsächliche Dateisichtbarkeit wird durch privates Repository/Dateisystemzugriff geschützt.
8. ProjectOS-Rechte regeln zusätzlich die fachlichen Aktionen innerhalb des Systems.
9. Automatische GitHub-Meldungen sind fail-closed.
10. Fork, veralteter Stand, fehlende Authentifizierung, fehlendes Recht, Simulation, Secretverdacht oder unklarer Zustand sperren die Automatik.
11. Dubletten werden nach Möglichkeit am bestehenden Issue ergänzt statt neu angelegt.
12. Keine Tokens oder Zugangsdaten in ProjectOS-Projektdateien oder Fehlerberichte übernehmen.
13. Fehlende Hersteller-, Datenblatt- oder 3D-Daten nicht erfinden.
14. Hüllkörpervorschauen sind keine echten 3D-Modelle.
15. Runtime-Diagnosen werden aus persistierter Quelle neu berechnet; abgeleitete Ergebnisse werden nicht als Wahrheit gespeichert.
16. Neue/fachlich überarbeitete Symbole verwenden explizit `Z_Footprint_Policy`.
17. `Geprüft` und `Praxisgetestet` nur nach dem neuen Qualitätshandbuch vergeben.
18. Freigegebene MCB-/RCD-Geometrien und die freigegebene Bibliotheksansicht nicht ohne neue ausdrückliche Anforderung verändern.

---

# 18. Wichtige Dateien für die nächste Sitzung

Zuerst lesen:

```text
docs/handover/ARBEITSSTAND_2026-08-10_TAGESABSCHLUSS.md
project_state.yaml
docs/01_Roadmap/PROJECT_ROADMAP.md
docs/00_Project/LIBRARY_GUIDELINES.md
```

Z_Cockpit / ProjectOS:

```text
docs/03_Developer/Z_COCKPIT.md
docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md
docs/03_Developer/Z_COCKPIT_BERECHTIGUNGEN.md
docs/03_Developer/Z_COCKPIT_FEHLERMELDUNG.md
docs/03_Developer/Z_COCKPIT_3D_VORSCHAUEN.md
docs/03_Developer/Z_COCKPIT_KICAD_EDITORAUFRUFE.md
docs/03_Developer/Z_COCKPIT_LAUFZEITDIAGNOSEN.md
```

Detail-Handover des Tages bleiben zusätzlich als historische Fachstände erhalten, insbesondere:

```text
docs/handover/ARBEITSSTAND_2026-08-10_MCB_Z_COCKPIT.md
docs/handover/ARBEITSSTAND_2026-08-10_Z_COCKPIT_AUSBAU.md
docs/handover/ARBEITSSTAND_2026-08-10_Z_COCKPIT_GOVERNANCE.md
docs/handover/ARBEITSSTAND_2026-08-10_QUALITAETSHANDBUCH.md
```

---

# 19. Tagesabschluss

Der Arbeitsblock vom 10.08.2026 ist in einem stabilen Zustand beendet.

Heute wurden insbesondere abgeschlossen:

- MCB-Feintuning und visuell freigegebene Bibliotheksansicht;
- RCD 2P einschließlich finaler Geometrie und Varianten;
- RCD 4P/3+N einschließlich Varianten;
- globaler ProjectOS-Projektvalidator;
- alle ursprünglich vorgesehenen Z_Cockpit-Kernseiten;
- einheitliche Seitenköpfe;
- Benutzerverwaltung;
- Testuser und Simulationsmodus;
- aktive ProjectOS-Identitätsanzeige;
- White-/Blacklist- und Berechtigungsansicht;
- schreibende Governance-Pfade;
- Projektdatei-Erzeugung im Z_Cockpit;
- Schutzklassen und ProjectOS-Dateirechte;
- lokaler/manueller und automatischer Fehlerbericht;
- Repository-/Versions-/Fork-/Benutzer-/Rechte-Gates für automatische GitHub-Meldungen;
- Dublettenprüfung und Meldehistorie;
- 3D-Vorschau-/Modellabdeckung;
- direkte KiCad-Editoraufrufe;
- Persistenz der Laufzeitdiagnosequelle;
- verbindliches Qualitätshandbuch für Bibliothekspakete.

Der aktuelle technische Zustand ist durch die vollständige CI abgesichert. Für die nächste Sitzung sollte nicht erneut an bereits abgenommenen UI-/Symbolständen begonnen werden, sondern anhand dieses Handovers und der Roadmap weitergearbeitet werden.

**Nächster normaler Roadmap-Schwerpunkt:** verständliche Benutzerdokumentation/Screenshots und anschließend Schritt-für-Schritt-Beispielprojekte.  
**Separat blockiert:** GitHub-Ruleset.
