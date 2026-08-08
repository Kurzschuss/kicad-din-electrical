# Projektmodell

**Dokument-ID:** PLT-0002  
**Titel:** Fachliches Modell eines Projekts  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert das Projekt als fachliches Plattformobjekt.

Ein Projekt ist weder Repository noch Verzeichnis noch Workspace. Es bildet einen dauerhaften fachlichen und organisatorischen Bezugsrahmen für Ziele, Artefakte, Domänen, Beteiligte, Konfiguration, Entscheidungen, Releases und Nachweise.

## 2. Architekturstellung

Das Projekt verwendet die universellen Core-Verträge aus `OBJECT_MODEL.md`, `OBJECT_INTERFACE.md`, `SCHEMA_MODEL.md` und `RELATION_MODEL.md`.

Es gehört zur Plattformebene und darf den Core nicht erweitern.

Domänen dürfen innerhalb eines Projekts aktiviert und verwendet werden, ohne dass das Projektmodell deren konkrete Fachlogik kennen muss.

## 3. Projektidentität

Jedes Projekt besitzt eine stabile Objektidentität.

Diese Identität:

- ist unabhängig von Projektname, Speicherort und Repository;
- bleibt bei Umbenennung oder Verschiebung erhalten;
- wird nicht wiederverwendet;
- ist versionsunabhängig;
- darf nicht aus einem Dateipfad abgeleitet werden.

## 4. Projektkern

Ein Projekt beschreibt mindestens:

- Projektidentität;
- Name und optionale Kurzbezeichnung;
- Zweck, Ziel und fachlichen Kontext;
- Lebenszyklusstatus;
- verwendete Projekt-Schemaversion;
- Eigentums- und Verantwortungsreferenzen;
- aktivierte Domänen;
- Artefaktbeziehungen;
- Beteiligungs- und Mitgliedschaftsbeziehungen;
- Konfigurationsreferenzen;
- Historien- und Auditbezüge;
- Release- und Versionsbezüge;
- Wissens- und Entscheidungsbezüge.

## 5. Projekt und Repository

Ein Repository ist eine technische Ablage und kein fachliches Projekt.

Daher gilt:

- ein Projekt kann ohne Git existieren;
- ein Repository kann mehrere Projekte enthalten;
- ein Projekt kann Artefakte aus mehreren Repositories referenzieren;
- ein Wechsel des Repositorys verändert nicht die Projektidentität;
- Repository-Metadaten dürfen als technische Referenzen geführt werden, sind aber nicht Teil der fachlichen Projektidentität.

## 6. Projekt und Workspace

Projekt und Workspace sind getrennte Konzepte.

Das Projekt beschreibt den dauerhaften fachlichen Zustand.

Der Workspace beschreibt einen Arbeitskontext, beispielsweise geöffnete Projekte, lokale Ansichten, persönliche Einstellungen oder temporäre Arbeitszustände.

Ein Workspace darf ein Projekt nicht besitzen. Ein Projekt darf nicht von einem bestimmten Workspace abhängig sein.

## 7. Domänen

Ein Projekt kann null, eine oder mehrere Domänen aktivieren.

Die Aktivierung einer Domäne bedeutet nicht, dass deren gesamtes Fachmodell Bestandteil des Projektmodells wird.

Das Projekt führt nur die notwendigen Referenzen und Aktivierungsinformationen.

Domänenspezifische Regeln bleiben Eigentum der jeweiligen Domäne.

## 8. Artefakte

Ein Projekt kann fachliche und technische Artefakte referenzieren.

Dazu können beispielsweise gehören:

- Modelle;
- Dokumente;
- Konfigurationen;
- Schaltplan- und Bibliotheksartefakte;
- Simulationen;
- Tests;
- Entscheidungen;
- Releases;
- externe Referenzen.

Das Projektmodell definiert nicht die interne Struktur dieser Artefakte.

## 9. Beteiligte und Verantwortlichkeit

Das Projekt kann Beziehungen zu Akteursidentitäten besitzen.

Dabei werden mindestens getrennt betrachtet:

- Eigentum;
- Projektleitung;
- Stellvertretung;
- fachliche Verantwortung;
- Mitgliedschaft;
- Review- und Freigabeverantwortung;
- Vertrauens- oder Eskalationsbeziehungen, sofern durch die Identitätsplattform vorgesehen.

Die konkrete Berechtigungswirkung dieser Beziehungen wird nicht im Projektmodell entschieden, sondern durch die Autorisierungsplattform.

## 10. Lebenszyklus

Ein Projekt besitzt einen kontrollierten Lebenszyklus.

Mindestens werden konzeptionell unterschieden:

- Entwurf;
- aktiv;
- pausiert;
- abgeschlossen;
- archiviert.

Weitere Zustände oder Übergänge müssen im Projektschema definiert werden.

Archivierung ist nicht gleich Löschung.

## 11. Version und Release

Die Objektversion des Projektobjekts ist von einem fachlichen Projekt-Release zu unterscheiden.

Eine Objektversion beschreibt den Zustand des Projektobjekts.

Ein Release beschreibt einen ausdrücklich benannten oder freigegebenen Gesamtstand ausgewählter Projektartefakte.

Ein Release kann mehrere Objekt-, Schema-, Dokument- und Implementierungsversionen zusammenfassen.

## 12. Konfiguration

Projektkonfiguration wird nicht als unstrukturierte Sammlung beliebiger Einstellungen behandelt.

Konfigurationsstände müssen referenzierbar, validierbar und soweit erforderlich versionierbar sein.

Die genaue Struktur wird später im `CONFIGURATION_MODEL.md` definiert.

## 13. Projektwissen

Ein Projekt kann Wissen über Anforderungen, Entscheidungen, Modelle, Implementierungen, Tests, Releases, Erkenntnisse und deren Beziehungen referenzieren.

Das Projekt selbst ist jedoch nicht das Projektgedächtnis.

Die Regeln für dauerhaftes Projektwissen werden später im `MEMORY_MODEL.md` definiert.

## 14. Historie und Audit

Projektgeschichte und Audit sind getrennt.

Die Historie beschreibt die fachliche Entwicklung des Projektobjekts.

Audit beschreibt nachweisrelevante Handlungen, Akteure, Berechtigungskontexte und Ergebnisse.

Das Projektmodell darf Auditinformationen referenzieren, definiert aber nicht deren vollständiges Modell.

## 15. Offline-First

Ein Projekt muss in seinem freigegebenen lokalen Betriebsumfang ohne dauerhafte Netzwerkverbindung nutzbar sein.

Dazu müssen die für den lokalen Betrieb erforderlichen Projektmetadaten, Schemata, Konfigurationen und Referenzinformationen lokal verfügbar sein.

Nicht verfügbare externe Referenzen müssen erkennbar bleiben und dürfen nicht stillschweigend durch andere Inhalte ersetzt werden.

## 16. Validierung

Ein Projekt ist mindestens darauf zu prüfen, dass:

1. eine gültige Projektidentität vorhanden ist;
2. das Projektschema bekannt und zulässig ist;
3. der Lebenszyklusstatus gültig ist;
4. erforderliche Verantwortungsreferenzen vorhanden sind;
5. aktivierte Domänen eindeutig identifiziert sind;
6. Pflichtreferenzen auflösbar oder ausdrücklich als extern/nicht verfügbar markiert sind;
7. Beziehungen die vorgesehenen Beziehungstypen und Kardinalitäten erfüllen;
8. Konfigurationsreferenzen mit dem Projektstand vereinbar sind;
9. keine technische Ablage fälschlich als Projektidentität verwendet wird.

## 17. Invarianten

Für jedes Projekt gelten mindestens folgende Invarianten:

1. Ein Projekt besitzt genau eine stabile Projektidentität.
2. Projektidentität und Speicherort sind getrennt.
3. Projekt und Workspace sind getrennt.
4. Projekt und Repository sind getrennt.
5. Domänenspezifische Fachlogik bleibt außerhalb des Projektmodells.
6. Berechtigungsentscheidungen werden nicht im Projektmodell implementiert.
7. Archivierung löscht die Projektidentität nicht.
8. Ein Projekt-Release ist nicht mit der Objektversion des Projekts gleichzusetzen.
9. Historie und Audit bleiben getrennt.
10. Externe oder nicht auflösbare Referenzen werden sichtbar behandelt.

## 18. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- konkrete Dateiformate;
- Repository-Strukturen;
- Git-Workflows;
- Workspace-Details;
- Benutzerkonten oder Authentifizierung;
- Rollen- oder Berechtigungslogik;
- konkrete Elektrodomänen;
- Datenbanktabellen;
- Cloud-Synchronisation;
- konkrete GUI-Strukturen.

## 19. Abhängigkeiten

Dieses Dokument basiert auf:

- `PLATFORM_MODEL.md`;
- `CORE_MODEL.md`;
- `OBJECT_MODEL.md`;
- `OBJECT_INTERFACE.md`;
- `SCHEMA_MODEL.md`;
- `RELATION_MODEL.md`;
- `ADR-0002-identitaet-als-plattformkonzept.md`;
- `ADR-0003-architekturebenen-und-kernelgrenze.md`;
- `ADR-0004-core-referenzen-und-schema-bootstrap.md`.

## 20. Ergebnis

Das Projekt ist als dauerhaft identifizierbares, domänenunabhängiges Plattformobjekt definiert.

Es bildet den fachlichen Bezugsrahmen für Projektarbeit, ohne mit Repository, Workspace, Benutzerverwaltung oder einer konkreten Fachdomäne gleichgesetzt zu werden.
