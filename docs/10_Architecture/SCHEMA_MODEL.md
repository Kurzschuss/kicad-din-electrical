# Schemamodell

**Dokument-ID:** ARC-0005  
**Titel:** Grundlegendes Schemamodell  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Architekturmodell  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Zweck

Dieses Dokument definiert den fachlichen Begriff „Schema“ innerhalb des Kernels.

Ein Schema beschreibt die zulässige Struktur, Bedeutung und Validierung schemagebundener Objekte oder anderer ausdrücklich dafür vorgesehener Strukturen.

Es legt keine konkrete Schema-Technologie wie JSON Schema, XML Schema, SQL-DDL oder eine Programmiersprachen-Typdefinition fest.

## 2. Geltungsbereich

Das Schemamodell gilt für alle dauerhaft gespeicherten oder systemweit referenzierbaren Objekte, deren Struktur, Eigenschaften, Beziehungen, Zustände oder Validierungsregeln ausdrücklich beschrieben werden müssen.

Ein Schema ist erforderlich, wenn mindestens einer der folgenden Punkte zutrifft:

- Pflicht- und optionale Eigenschaften müssen festgelegt werden;
- Datentypen oder Wertebereiche müssen validiert werden;
- zulässige Beziehungen müssen definiert werden;
- Lebenszykluszustände oder Übergänge müssen eingeschränkt werden;
- Kompatibilität und Migration müssen nachvollziehbar sein;
- mehrere Komponenten oder Domänen müssen dieselbe Struktur eindeutig verstehen.

## 3. Definition

Ein Schema ist ein versioniertes, referenzierbares und validierbares Core-Artefakt, das die zulässige fachliche Struktur eines Objekttyps oder einer anderen schemagebundenen Struktur definiert.

Ein Schema beantwortet insbesondere:

- Welche Eigenschaften sind zulässig?
- Welche Eigenschaften sind verpflichtend?
- Welche Datentypen und Wertebereiche gelten?
- Welche Beziehungen sind zulässig?
- Welche Lebenszykluszustände sind zulässig?
- Welche Invarianten müssen erfüllt sein?
- Welche Version des Schemas gilt?
- Wie werden ältere Versionen behandelt?

## 4. Schema als Objekt

Ein Schema wird als dauerhaft identifizierbares Objekt modelliert.

Damit besitzt es mindestens:

- eine stabile Objektidentität;
- einen eindeutigen Schematyp;
- eine Schemaversion;
- einen Lebenszyklusstatus;
- eine zuständige Domäne;
- Erzeugungs- und Änderungsinformationen;
- Beziehungen zu anderen Schemata und Modellen;
- eine nachvollziehbare Historie.

Ein Schema darf sich nicht ausschließlich durch einen Dateinamen, Pfad oder technischen Speicherort identifizieren.

## 5. Schemareferenz

Jedes schemagebundene Objekt verweist auf:

- eine stabile Schemareferenz;
- eine konkrete Schemaversion.

Die Schemareferenz identifiziert die fachliche Schemalinie. Die Schemaversion bezeichnet einen bestimmten Stand dieser Linie.

Eine Referenz auf ein unbekanntes, nicht auflösbares oder für den Objekttyp unzulässiges Schema macht das Objekt ungültig oder nicht vollständig prüfbar.

## 6. Schemainhalt

Ein Schema definiert mindestens, soweit anwendbar:

- den fachlichen Zweck;
- den zugehörigen Objekttyp oder Strukturtyp;
- erlaubte Eigenschaften;
- Pflicht- und optionale Eigenschaften;
- Datentypen;
- Wertebereiche;
- Kardinalitäten;
- Standardwerte;
- Änderbarkeitsregeln;
- zulässige Beziehungen;
- zulässige Lebenszykluszustände;
- Validierungsregeln;
- Invarianten;
- Kompatibilitätsaussagen;
- Migrationshinweise oder Migrationsregeln.

## 7. Eigenschaften

Eigenschaften werden durch das Schema eindeutig benannt und fachlich beschrieben.

Für jede Eigenschaft werden mindestens festgelegt, soweit erforderlich:

- fachlicher Name;
- Bedeutung;
- Datentyp;
- Kardinalität;
- Pflicht oder optional;
- zulässiger Wertebereich;
- Standardwert;
- Änderbarkeit;
- Sichtbarkeit;
- Validierungsregeln;
- Auswirkungen auf Versionierung und Historie.

Ein Schema darf kein Fachattribut definieren, das ein Kernattribut widersprüchlich neu beschreibt.

## 8. Datentypen

Datentypen werden fachlich beschrieben und dürfen nicht unnötig an eine konkrete Programmiersprache oder Speichertechnologie gebunden sein.

Mögliche fachliche Datentypklassen sind beispielsweise:

- Text;
- Ganzzahl;
- Dezimalzahl;
- Wahrheitswert;
- Datum;
- Zeitpunkt;
- Dauer;
- Aufzählung;
- strukturierter Wert;
- Objektreferenz;
- Beziehungsreferenz;
- Menge oder Liste;
- Messwert mit Einheit.

Die konkrete technische Abbildung wird in Implementierungsspezifikationen festgelegt.

## 9. Kardinalität

Ein Schema legt fest, wie oft eine Eigenschaft oder Beziehung vorkommen darf.

Mindestens zu unterscheiden sind:

- genau einmal;
- optional höchstens einmal;
- mindestens einmal;
- beliebig oft;
- begrenzte Anzahl;
- genau definierte Anzahl.

Kardinalitätsverletzungen führen zu einem Validierungsfehler.

## 10. Standardwerte

Standardwerte sind zulässig, wenn sie fachlich eindeutig, dokumentiert und reproduzierbar sind.

Ein Standardwert darf:

- keine sicherheitsrelevante Entscheidung verbergen;
- keine unbekannte Identität oder Berechtigung erzeugen;
- keine fachlich wesentliche Eingabe stillschweigend ersetzen;
- nicht von einem unkontrollierten externen Zustand abhängen.

Es muss unterscheidbar bleiben, ob ein Wert ausdrücklich gesetzt oder durch einen Standard abgeleitet wurde, sofern dies fachlich relevant ist.

## 11. Beziehungen

Ein Schema legt fest, welche Beziehungstypen für den zugehörigen Objekttyp zulässig sind.

Dabei können insbesondere definiert werden:

- zulässige Quell- und Zieltypen;
- Richtung oder Symmetrie;
- Kardinalität;
- Pflichtbeziehungen;
- Ausschlussregeln;
- Lebenszyklusabhängigkeiten;
- Gültigkeitszeiträume;
- zulässige Beziehungseigenschaften;
- Regeln für Löschung und Archivierung.

Die vollständige Definition von Beziehungen erfolgt in `RELATION_MODEL.md`.

## 12. Lebenszyklus

Ein Schema kann zulässige Lebenszykluszustände und Zustandsübergänge definieren.

Ein Zustandsübergang kann Bedingungen, erforderliche Berechtigungen, Validierungen, Freigaben und erzeugte Ereignisse besitzen.

Ein Objekt darf keinen Zustand annehmen, der durch sein Schema nicht zugelassen ist.

## 13. Validierungsregeln

Validierungsregeln müssen eindeutig, reproduzierbar und soweit möglich automatisierbar sein.

Sie können prüfen:

- Vorhandensein von Pflichtangaben;
- Datentypen;
- Wertebereiche;
- Formate;
- Kardinalitäten;
- Abhängigkeiten zwischen Eigenschaften;
- Beziehungen;
- Statusübergänge;
- fachliche Invarianten;
- Kompatibilität;
- Vollständigkeit von Referenzen.

Eine Regel muss ein strukturiertes Ergebnis mit mindestens Regelkennung, Status, betroffener Stelle und verständlicher Begründung liefern können.

## 14. Invarianten

Invarianten beschreiben Bedingungen, die für jeden gültigen Zustand gelten müssen.

Ein Schema darf keine Invariante definieren, die einer höherrangigen Core- oder Plattformregel widerspricht.

Eine Verletzung einer Invariante verhindert die erfolgreiche Freigabe oder Speicherung eines Zustands, sofern keine ausdrücklich dokumentierte Ausnahme vorgesehen ist.

## 15. Schemafamilie und Schemalinie

Mehrere Versionen desselben fachlichen Schemas bilden eine Schemalinie.

Unterschiedliche Schemata können zu einer Schemafamilie gehören, wenn sie verwandte, aber eigenständige Objekttypen oder Varianten beschreiben.

Schemalinie und Schemafamilie dürfen nicht zur stillschweigenden Vermischung unterschiedlicher fachlicher Bedeutungen führen.

## 16. Versionierung

Jede veröffentlichte Schemaänderung erzeugt eine neue Schemaversion.

Eine bestehende veröffentlichte Version wird nicht rückwirkend in ihrer Bedeutung verändert.

Schemaänderungen werden mindestens eingeordnet als:

- redaktionell ohne Bedeutungsänderung;
- rückwärtskompatible Erweiterung;
- kompatible Präzisierung;
- migrationspflichtige Änderung;
- inkompatible Änderung.

Das konkrete Versionsformat wird gesondert festgelegt.

## 17. Kompatibilität

Für jede neue Schemaversion muss bewertet werden:

- Können Objekte älterer Versionen weiterhin gelesen werden?
- Können sie ohne Änderung validiert werden?
- Ist eine Migration erforderlich?
- Können ältere Komponenten die neue Version verarbeiten?
- Gehen Informationen bei Rückmigration verloren?
- Welche Übergangsfristen oder Parallelversionen sind notwendig?

Kompatibilität darf nicht allein aus ähnlichen Feldnamen abgeleitet werden.

## 18. Migration

Eine Migration überführt ein schemagebundenes Objekt kontrolliert von einer Schemaversion in eine andere.

Eine Migration muss mindestens definieren:

- Quellversion;
- Zielversion;
- Voraussetzungen;
- Transformationsregeln;
- Validierung des Ergebnisses;
- Umgang mit nicht abbildbaren Informationen;
- Fehler- und Rücksetzverhalten;
- Audit- und Historienanforderungen.

Migrationen dürfen die Objektidentität nicht stillschweigend ersetzen.

## 19. Erweiterung und Spezialisierung

Ein Schema kann ein anderes Schema nur über ausdrücklich definierte Mechanismen erweitern oder spezialisieren.

Dabei muss eindeutig bleiben:

- welches Schema maßgeblich ist;
- welche Regeln geerbt oder übernommen werden;
- welche Regeln ergänzt werden;
- ob Einschränkungen zulässig sind;
- wie Konflikte behandelt werden;
- wie Versionen gekoppelt sind.

Unkontrollierte Mehrfachvererbung oder widersprüchliche Überschreibungen sind unzulässig.

## 20. Geltungsbereich und Domänenverantwortung

Jedes Schema besitzt genau eine fachlich zuständige Domäne.

Die Domäne verantwortet:

- fachliche Bedeutung;
- Eigenschaften und Beziehungen;
- Validierungsregeln;
- Versionierung;
- Kompatibilität;
- Migration;
- Lebenszyklus und Freigabe.

Andere Domänen dürfen das Schema verwenden, aber nicht stillschweigend verändern.

## 21. Lebenszyklus eines Schemas

Ein Schema kann mindestens folgende Zustände besitzen:

- Entwurf;
- In Review;
- freigegeben;
- aktiv;
- veraltet;
- archiviert.

Nur ausdrücklich freigegebene oder aktive Schemaversionen dürfen für produktive Objekte verwendet werden, sofern keine dokumentierte Ausnahme besteht.

Ein veraltetes Schema bleibt für historische Objekte und Migrationen referenzierbar.

## 22. Auflösung und Verfügbarkeit

Eine Schemareferenz muss innerhalb ihres vorgesehenen Betriebsmodus zuverlässig auflösbar sein.

Offline-First bedeutet, dass für lokal nutzbare Objekte auch die erforderlichen Schemata und Validierungsregeln lokal verfügbar sein müssen.

Ein externes Schema darf nicht ohne kontrollierte Versionierung und lokale Nachvollziehbarkeit die fachliche Bedeutung bestehender Objekte verändern.

## 23. Menschen- und Maschinenlesbarkeit

Ein Schema benötigt eine menschenlesbare fachliche Beschreibung.

Soweit automatisierte Validierung oder Verarbeitung erforderlich ist, soll zusätzlich eine maschinenlesbare Darstellung existieren.

Beide Darstellungen müssen derselben fachlichen Bedeutung folgen. Im Konfliktfall muss festgelegt sein, welche Darstellung maßgeblich ist.

## 24. Validierung eines Schemas

Ein Schema selbst muss validierbar sein.

Die Schemavalidierung prüft mindestens:

- eindeutige Identität und Version;
- eindeutigen Zweck und Geltungsbereich;
- bekannte Eigenschaftsdefinitionen;
- widerspruchsfreie Pflicht- und Kardinalitätsregeln;
- gültige Beziehungen;
- auflösbare Referenzen;
- konsistente Lebenszyklusregeln;
- widerspruchsfreie Invarianten;
- dokumentierte Kompatibilitätsaussagen;
- bekannte Domänenverantwortung.

Ein ungültiges Schema darf nicht als freigegeben gemeldet werden.

## 25. Schema-Invarianten

Für jedes Schema gelten mindestens folgende Invarianten:

1. Ein Schema besitzt eine stabile Identität.
2. Eine veröffentlichte Schemaversion verändert ihre Bedeutung nicht rückwirkend.
3. Jede Eigenschaft besitzt eine eindeutige fachliche Bedeutung.
4. Pflichtangaben, Kardinalitäten und Standardwerte widersprechen sich nicht.
5. Jede referenzierte Struktur ist auflösbar oder ausdrücklich extern definiert.
6. Jede Validierungsregel ist eindeutig identifizierbar.
7. Ein Schema definiert keine unzulässigen Beziehungen oder Statusübergänge.
8. Eine Migration erhält die Objektidentität, sofern keine neue fachliche Einheit entsteht.
9. Ein Schema besitzt genau eine zuständige Domäne.
10. Ein ungültiges Schema darf nicht für neue produktive Objekte verwendet werden.

## 26. Nicht festgelegt

Dieses Dokument legt noch nicht fest:

- konkrete Schemaformate;
- konkrete Programmiersprachen-Typen;
- JSON-, YAML-, XML- oder SQL-Abbildungen;
- konkrete Versionsnummernregeln;
- Registry- oder Repository-Technologie;
- konkrete Codegenerierung;
- Vererbungsmechanismen einer bestimmten Sprache;
- technische Caching- und Verteilungsverfahren.

## 27. Abhängigkeiten

Dieses Dokument konkretisiert:

- `CORE_MODEL.md`;
- `OBJECT_MODEL.md`;
- `OBJECT_INTERFACE.md`;
- `OBJECT_SERVICE.md`;
- `ADR-0003-architekturebenen-und-kernelgrenze.md`.

Es bildet gemeinsam mit `RELATION_MODEL.md` die Grundlage für spätere Plattform- und Domänenschemata.

## 28. Ergebnis

Ein Schema ist die versionierte und referenzierbare fachliche Definition der zulässigen Struktur eines schemagebundenen Objekts oder einer anderen dafür vorgesehenen Struktur.

Es trennt fachliche Bedeutung von technischer Darstellung und ermöglicht konsistente Validierung, Kompatibilitätsbewertung und Migration.