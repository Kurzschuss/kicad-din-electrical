# Workspace-Modell

**Dokument-ID:** PLT-0004  
**Titel:** Fachliches Modell eines Workspace  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert den Workspace als benutzer- und sitzungsnahen Arbeitskontext der Plattform.

Ein Workspace ist kein Projekt und keine fachliche Quelle der Wahrheit. Er beschreibt, wie eine Identität mit einem oder mehreren Projekten arbeitet, ohne den fachlichen Projektzustand selbst zu besitzen.

## 2. Architekturstellung

Der Workspace gehört zur Plattformebene und verwendet die Core- und Projektmodelle.

Er darf weder Core-Regeln noch fachliche Domänenregeln redefinieren.

Der Workspace darf temporäre oder persönliche Zustände halten, solange diese nicht stillschweigend als autoritative Projektinformationen behandelt werden.

## 3. Definition

Ein Workspace ist ein referenzierbarer Arbeitskontext, der eine Arbeitsumgebung für eine Identität, Sitzung oder definierte Arbeitsgruppe beschreibt.

Er kann insbesondere festhalten:

- geöffnete Projekte;
- aktive Projektreferenz;
- persönliche Ansichten;
- Fenster- und Panelzustände;
- Filter und Sortierungen;
- lokale Navigation;
- zuletzt verwendete Elemente;
- lokale Entwürfe oder Arbeitsstände;
- temporäre Auswahlzustände;
- persönliche Werkzeugeinstellungen;
- lokale Synchronisations- oder Verfügbarkeitsinformationen.

## 4. Workspace und Projekt

Projekt und Workspace sind ausdrücklich getrennt.

Das Projekt enthält fachlich dauerhafte Informationen.

Der Workspace enthält arbeitsbezogene Informationen.

Daraus folgen mindestens diese Regeln:

1. Das Löschen eines Workspace löscht kein Projekt.
2. Das Umbenennen eines Workspace ändert keine Projektidentität.
3. Ein Projekt kann in mehreren Workspaces geöffnet werden.
4. Ein Workspace kann mehrere Projekte referenzieren.
5. Ein Projekt darf nicht von der Existenz eines bestimmten Workspace abhängen.
6. Ein Workspace darf keine fachliche Projektregel überschreiben.

## 5. Workspace und Identität

Ein Workspace kann einer Akteursidentität zugeordnet sein.

Diese Zuordnung kann beispielsweise unterscheiden zwischen:

- persönlichem Workspace;
- gemeinsamem Team-Workspace;
- temporärem Sitzungs-Workspace;
- systemseitig bereitgestelltem Workspace.

Die konkrete Eigentums- und Berechtigungslogik wird durch die Identitäts- und Autorisierungsplattform definiert.

## 6. Workspace und Sitzung

Ein Workspace ist nicht mit einer Sitzung gleichzusetzen.

Eine Sitzung beschreibt einen authentifizierten Nutzungskontext.

Ein Workspace kann über mehrere Sitzungen fortbestehen.

Umgekehrt kann eine Sitzung mehrere Workspaces verwenden.

## 7. Dauerhaftigkeit

Workspace-Zustände können unterschiedliche Persistenzklassen besitzen:

- rein temporär;
- sitzungsgebunden;
- lokal persistent;
- benutzerbezogen persistent;
- gemeinsam geteilt.

Die Persistenzklasse muss erkennbar sein.

Ein temporärer Zustand darf nicht stillschweigend zu dauerhaftem Projektwissen werden.

## 8. Lokale Entwürfe

Ein Workspace darf lokale, noch nicht in das Projekt übernommene Entwürfe oder Zwischenstände enthalten.

Solche Inhalte müssen eindeutig als nicht autoritativ gekennzeichnet sein.

Ihre Existenz darf den gespeicherten Projektzustand nicht verändern.

Die Übernahme in das Projekt erfolgt ausschließlich über explizite Projekt- oder Objektdienste.

## 9. Undo/Redo und Arbeitszustand

Workspace-nahe Bearbeitungszustände können Undo-/Redo-Informationen enthalten oder referenzieren.

Die genaue Undo-/Redo-Architektur wird nicht in diesem Dokument definiert.

Wichtig ist die Trennung:

- Workspace-Arbeitszustand;
- fachlicher Projektzustand;
- letzter erfolgreicher Savepoint;
- Persistenzziel.

Ein Workspace darf bei fehlgeschlagenem Speichern diese Grenzen nicht aufheben.

## 10. Offline-First

Ein Workspace soll seinen lokalen Arbeitskontext ohne permanente Netzwerkverbindung erhalten können.

Nicht verfügbare externe Projekte oder Ressourcen müssen sichtbar als nicht verfügbar gekennzeichnet werden.

Lokale Ansichten und persönliche Einstellungen dürfen nicht von externen Diensten abhängen, sofern dies nicht ausdrücklich erforderlich ist.

## 11. Synchronisation

Wenn Workspace-Zustände zwischen Geräten oder Sitzungen synchronisiert werden, muss zwischen persönlichem Komfortzustand und fachlich relevanten Informationen unterschieden werden.

Synchronisationskonflikte eines Workspace dürfen keinen Projektzustand stillschweigend überschreiben.

## 12. Validierung

Ein Workspace ist mindestens darauf zu prüfen, dass:

1. seine eigene Identität oder stabile Referenz gültig ist;
2. referenzierte Projekte eindeutig auflösbar oder als nicht verfügbar gekennzeichnet sind;
3. keine Workspace-Eigenschaft als autoritative Projektquelle verwendet wird;
4. Persistenzklassen konsistent sind;
5. persönliche und gemeinsam geteilte Zustände unterscheidbar sind;
6. lokale Entwürfe ausdrücklich als nicht autoritativ markiert sind.

## 13. Invarianten

1. Workspace und Projekt sind unterschiedliche Objekte.
2. Ein Workspace besitzt keine fachliche Hoheit über ein Projekt.
3. Das Löschen eines Workspace löscht keine Projektidentität.
4. Persönliche Ansichten verändern keine fachlichen Projektinformationen.
5. Lokale Entwürfe sind nicht automatisch Projektinhalt.
6. Eine Sitzung ist nicht mit einem Workspace gleichzusetzen.
7. Workspace-Synchronisation darf keine fachliche Projektänderung ohne explizite Projektoperation verursachen.
8. Der Workspace respektiert Projekt-, Identitäts- und Autorisierungsgrenzen.

## 14. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- konkrete GUI-Layouts;
- Fensterkoordinaten oder UI-Frameworks;
- Benutzerkonten;
- Sitzungsformate;
- Authentifizierungsverfahren;
- Projektdateiformate;
- konkrete Undo-/Redo-Datenstrukturen;
- Cloud-Synchronisationsprotokolle;
- KiCad-spezifische Workspace-Ansichten.

## 15. Abhängigkeiten

Dieses Dokument basiert auf:

- `PLATFORM_MODEL.md`;
- `PROJECT_MODEL.md`;
- `PROJECT_SERVICE.md`;
- `OBJECT_MODEL.md`;
- `OBJECT_INTERFACE.md`;
- `RELATION_MODEL.md`;
- `ADR-0002-identitaet-als-plattformkonzept.md`;
- `ADR-0003-architekturebenen-und-kernelgrenze.md`.

## 16. Ergebnis

Der Workspace ist als eigenständiger Arbeitskontext definiert.

Er hält benutzer-, sitzungs- oder arbeitsbezogene Zustände, ohne das Projekt selbst zu ersetzen oder dessen fachliche Autorität zu übernehmen.
