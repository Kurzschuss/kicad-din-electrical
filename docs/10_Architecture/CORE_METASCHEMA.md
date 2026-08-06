# Core-Metaschema

**Dokument-ID:** ARC-0007  
**Titel:** Minimaler Bootstrap-Vertrag für Core-Schemata  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** A  
**Autoritätsebene:** Architekturmodell  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Zweck

Dieses Dokument definiert den minimalen Bootstrap-Vertrag, mit dem Core-Schemata eindeutig identifiziert, versioniert, referenziert und validiert werden können.

Es beendet die Rekursion, die dadurch entsteht, dass Schemata selbst als Objekte modelliert werden und jedes Objekt auf ein Schema verweist.

Dieses Dokument konkretisiert ADR-0004. Es ist kein allgemeines Fachschema und darf nicht für Plattform- oder Domänensonderregeln erweitert werden.

## 2. Geltungsbereich

Das Core-Metaschema gilt ausschließlich für:

- das Core-Metaschema selbst;
- grundlegende Core-Schemata während des Bootstrap;
- die minimale Validierung, die erforderlich ist, bevor reguläre Schemaregeln angewendet werden können.

Reguläre Schemata müssen nach erfolgreichem Bootstrap vollständig den Regeln aus `SCHEMA_MODEL.md` folgen.

## 3. Grundsatz

Der Bootstrap ist eine eng begrenzte Vertrauenswurzel des Kernels.

Er definiert nur Informationen, die notwendig sind, um ein Schema als eindeutiges und versioniertes Core-Artefakt zu erkennen und seine grundlegende innere Konsistenz zu prüfen.

Der Bootstrap darf keine Benutzer-, Rollen-, Berechtigungs-, Projekt-, Organisations-, Geräte- oder Domänenlogik enthalten.

## 4. Minimaler Metaschema-Vertrag

Ein Core-Schema muss im Bootstrap mindestens folgende Informationen bereitstellen:

| Feld | Bedeutung |
|---|---|
| `schema_id` | Stabile Identität der Schemalinie |
| `schema_version` | Eindeutige Version dieses Schemastands |
| `schema_name` | Menschenlesbare Bezeichnung |
| `schema_purpose` | Eindeutiger Zweck und Geltungsbereich |
| `schema_status` | Lebenszyklus- oder Freigabestatus |
| `structure_kind` | Art der beschriebenen Struktur |
| `property_definitions` | Minimal beschriebene Eigenschaften |
| `reference_definitions` | Minimal beschriebene Referenzen |
| `validation_rule_ids` | Eindeutige Kennungen der Bootstrap-Regeln |
| `created_at` | Erzeugungszeitpunkt |
| `modified_at` | Letzter Änderungszeitpunkt |

Die technischen Feldnamen sind noch nicht endgültig verbindlich. Verbindlich sind Bedeutung und Mindestumfang.

## 5. Schemaidentität

`schema_id` identifiziert genau eine fachliche Schemalinie.

Die Identität:

- ist stabil;
- ist versionsunabhängig;
- wird nicht wiederverwendet;
- hängt nicht von Dateiname, Pfad oder Speicherort ab;
- bleibt bei technischer Migration erhalten.

## 6. Schemaversion

`schema_version` identifiziert einen bestimmten veröffentlichten Stand einer Schemalinie.

Eine veröffentlichte Version wird nicht rückwirkend in ihrer Bedeutung verändert.

Das konkrete Versionsformat wird in einem späteren Versionsmodell oder ADR festgelegt.

## 7. Strukturart

`structure_kind` beschreibt, welche Art von Struktur das Schema definiert.

Zulässige Bootstrap-Kategorien sind zunächst:

- Objektschema;
- Beziehungsschema;
- Metaschema;
- andere ausdrücklich durch ADR zugelassene Core-Struktur.

Neue Kategorien erfordern eine dokumentierte Begründung.

## 8. Minimale Eigenschaftsdefinition

Eine Bootstrap-Eigenschaftsdefinition enthält mindestens:

- stabile Eigenschaftskennung;
- fachlichen Namen;
- Datentypklasse;
- Pflicht oder optional;
- Kardinalität;
- Änderbarkeit;
- gegebenenfalls Wertebereich;
- gegebenenfalls Standardwert;
- zugehörige Validierungsregeln.

Komplexe Fachregeln gehören nicht in das Core-Metaschema.

## 9. Minimale Referenzdefinition

Eine Bootstrap-Referenzdefinition enthält mindestens:

- stabile Referenzkennung;
- Referenzart;
- erwartete Zielkategorie;
- Kardinalität;
- Pflicht oder optional;
- Verhalten bei nicht auflösbarer Referenz.

Opaque Referenzen nach ADR-0004 dürfen verwendet werden.

Das Core-Metaschema darf das vollständige Modell eines externen Zielobjekts nicht voraussetzen.

## 10. Validierungsregeln

Jede Bootstrap-Regel besitzt eine eindeutige Regelkennung.

Mindestens zu prüfen sind:

1. `schema_id` ist vorhanden und gültig.
2. `schema_version` ist vorhanden und gültig.
3. Name, Zweck und Status sind vorhanden.
4. Eigenschaftskennungen sind innerhalb des Schemas eindeutig.
5. Referenzkennungen sind innerhalb des Schemas eindeutig.
6. Pflichtangaben und Kardinalitäten widersprechen sich nicht.
7. Jede referenzierte Regelkennung ist definiert.
8. Das Schema enthält keine unzulässigen Plattform- oder Domänenregeln.
9. Der Bootstrap-Umfang bleibt auf die minimal notwendige Struktur begrenzt.

Ein fehlgeschlagener Bootstrap verhindert die Freigabe des betroffenen Core-Schemas.

## 11. Selbstbeschreibung

Das Core-Metaschema darf sich selbst beschreiben.

Dafür gelten zusätzliche Bedingungen:

- die selbstbeschreibende Version ist eindeutig festgelegt;
- die Validierung ist deterministisch;
- der Validierungsalgorithmus benötigt keine spätere Plattform- oder Domänenlogik;
- eine veröffentlichte Bootstrap-Version wird nicht rückwirkend verändert;
- Änderungen werden durch ein eigenes ADR und eine Kompatibilitätsanalyse genehmigt.

Alternativ darf eine feste Bootstrap-Repräsentation verwendet werden, sofern sie denselben Vertrag erfüllt.

## 12. Lebenszyklusstatus

Das Core-Metaschema verwendet mindestens folgende Statuswerte:

- Entwurf;
- In Review;
- freigegeben;
- aktiv;
- veraltet;
- archiviert.

Nur freigegebene oder aktive Versionen dürfen als produktive Bootstrap-Verträge verwendet werden.

Veraltete Versionen bleiben für historische Validierung und Migration referenzierbar.

## 13. Kompatibilität

Jede Änderung am Core-Metaschema muss bewerten:

- Können bestehende Core-Schemata weiterhin validiert werden?
- Ist eine Migration erforderlich?
- Können ältere Kernelversionen die neue Bootstrap-Version verstehen?
- Welche Informationen gehen bei Rückmigration verloren?
- Ist Parallelbetrieb mehrerer Bootstrap-Versionen erforderlich?

Inkompatible Änderungen erfordern ein eigenes ADR.

## 14. Migration

Eine Migration des Core-Metaschemas muss mindestens definieren:

- Quellversion;
- Zielversion;
- Transformationsregeln;
- Validierung des Ergebnisses;
- Fehler- und Rücksetzverhalten;
- Behandlung historischer Schemata;
- Audit- und Nachweisanforderungen.

Eine Migration darf die Schemaidentität nicht stillschweigend ersetzen.

## 15. Offline-First

Das für einen lokalen Betriebsmodus notwendige Core-Metaschema muss lokal verfügbar sein.

Eine externe Quelle darf die Bedeutung einer bereits verwendeten Bootstrap-Version nicht stillschweigend verändern.

Lokale Kopien müssen eindeutig auf Version und Herkunft zurückführbar sein.

## 16. Sicherheits- und Vertrauensgrenze

Das Core-Metaschema ist Teil der vertrauenswürdigen Kernelbasis.

Daher gelten erhöhte Anforderungen:

- Änderungen erfolgen selten und kontrolliert;
- jede Änderung benötigt Review und Kompatibilitätsanalyse;
- Veröffentlichungen müssen eindeutig versioniert sein;
- manipulierte oder nicht verifizierbare Bootstrap-Artefakte dürfen nicht akzeptiert werden;
- die technische Implementierung muss eine Integritätsprüfung unterstützen.

Die konkrete kryptografische oder technische Sicherung wird später festgelegt.

## 17. Abgrenzung

Das Core-Metaschema definiert ausdrücklich nicht:

- konkrete Fachattribute von Plattform- oder Domänenobjekten;
- Benutzer-, Konto-, Rollen- oder Berechtigungsmodelle;
- Projekt- oder Organisationsmodelle;
- konkrete Beziehungstypen außerhalb des Bootstrap;
- konkrete Datenspeicher oder Transportformate;
- konkrete Programmiersprachen-Typen;
- konkrete UUID- oder Versionsformate;
- vollständige Autorisierungsregeln.

## 18. Invarianten

Für das Core-Metaschema gelten mindestens folgende Invarianten:

1. Es besitzt eine stabile Schemaidentität.
2. Jede veröffentlichte Version ist unveränderlich in ihrer Bedeutung.
3. Der Bootstrap bleibt minimal und domänenunabhängig.
4. Eigenschafts- und Referenzkennungen sind eindeutig.
5. Jede Validierungsregel ist eindeutig identifizierbar.
6. Selbstbeschreibung ist deterministisch und reproduzierbar.
7. Reguläre Schemata wechseln nach dem Bootstrap in die gewöhnlichen Regeln aus `SCHEMA_MODEL.md`.
8. Nicht auflösbare Referenzen werden ausdrücklich gemeldet.
9. Änderungen am Bootstrap benötigen ein eigenes ADR.
10. Ein ungültiges Core-Metaschema darf nicht als aktiv verwendet werden.

## 19. Abhängigkeiten

Dieses Dokument konkretisiert:

- `ADR-0004-core-referenzen-und-schema-bootstrap.md`;
- `CORE_MODEL.md`;
- `OBJECT_MODEL.md`;
- `OBJECT_INTERFACE.md`;
- `SCHEMA_MODEL.md`;
- `RELATION_MODEL.md`.

## 20. Ergebnis

Das Core-Metaschema bildet den kleinsten kontrollierten Startpunkt der schemaorientierten Kernelarchitektur.

Es ermöglicht, Core-Schemata eindeutig zu identifizieren, zu versionieren und grundlegend zu validieren, ohne eine unbegrenzte rekursive Schemakette oder eine Abhängigkeit zu Plattform- und Domänenmodellen zu erzeugen.
