# Objektschnittstelle

**Dokument-ID:** ARC-0002  
**Titel:** Universelle Objektschnittstelle  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Architekturmodell  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Zweck

Dieses Dokument definiert den universellen fachlichen Vertrag, den jedes Objekt der Plattform erfüllen muss.

`OBJECT_MODEL.md` definiert, was ein Objekt ist. Dieses Dokument definiert, welche gemeinsamen Informationen, Verweise und Invarianten jedes Objekt bereitstellen muss.

Es legt keine konkrete Programmiersprache, Serialisierung, Datenbankstruktur, API oder Dateiform fest.

## 2. Geltungsbereich

Die Objektschnittstelle gilt für alle dauerhaft gespeicherten oder systemweit referenzierbaren Objekte.

Domänenspezifische Objekttypen dürfen zusätzliche Fachattribute und Regeln definieren. Sie dürfen die hier festgelegten Kernattribute und Invarianten jedoch nicht umgehen oder widersprüchlich verändern.

## 3. Trennung von Kern- und Fachattributen

Jedes Objekt besteht aus zwei logisch getrennten Attributgruppen:

- **Kernattribute** gelten für jedes Objekt und werden durch diese Schnittstelle definiert.
- **Fachattribute** gelten nur für bestimmte Objekttypen und werden durch das zuständige Schema oder Fachmodell definiert.

Fachattribute dürfen Kernattribute nicht verdecken, umdeuten oder duplizieren.

## 4. Verpflichtende Kernattribute

Jedes Objekt besitzt mindestens folgende Kernattribute:

| Attribut | Bedeutung |
|---|---|
| `object_id` | Eindeutige und unveränderliche Objektidentität |
| `object_type` | Eindeutiger fachlicher Objekttyp |
| `schema_ref` | Referenz auf das gültige Schema |
| `schema_version` | Version des verwendeten Schemas |
| `object_version` | Version des aktuellen Objektzustands |
| `lifecycle_status` | Aktueller fachlicher Lebenszyklusstatus |
| `domain_owner` | Zuständige fachliche Domäne |
| `created_at` | Zeitpunkt der fachlichen Erzeugung |
| `created_by` | Identität des erzeugenden Akteurs oder Prozesses |
| `modified_at` | Zeitpunkt der letzten fachlichen Änderung |
| `modified_by` | Identität des zuletzt ändernden Akteurs oder Prozesses |
| `relations` | Menge der fachlich gültigen Beziehungen |

Die technischen Feldnamen sind noch nicht verbindlich. Verbindlich sind Bedeutung und Verantwortlichkeit der Attribute.

## 5. Objektidentität

`object_id` identifiziert genau ein fachliches Objekt.

Die Objektidentität:

- ist eindeutig;
- ist unveränderlich;
- wird nicht wiederverwendet;
- bleibt bei Umbenennung, Verschiebung, Migration oder Darstellungswechsel erhalten;
- ist unabhängig von Dateipfad, Anzeigename, Eigentümer, Status und Version.

Das konkrete Identifikatorformat wird in einem eigenen ADR festgelegt.

## 6. Objekttyp

`object_type` bezeichnet die fachliche Art des Objekts.

Der Objekttyp:

- ist eindeutig referenzierbar;
- verweist auf ein zuständiges Modell oder Schema;
- bestimmt zulässige Fachattribute, Beziehungen und Zustände;
- darf nicht stillschweigend geändert werden.

Eine Typänderung ist nur zulässig, wenn das zuständige Modell eine kontrollierte Transformation vorsieht.

## 7. Schema

Jedes Objekt verweist auf genau ein für seinen aktuellen Zustand maßgebliches Schema.

Die Schemainformation besteht mindestens aus:

- einer stabilen Schemareferenz;
- einer Schemaversion.

Das Schema definiert:

- zulässige Fachattribute;
- Pflichtattribute;
- Datentypen und Wertebereiche;
- zulässige Beziehungen;
- zulässige Statuswerte;
- Validierungsregeln;
- gegebenenfalls Migrationsregeln.

Ein Objekt darf nicht als gültig gelten, wenn sein referenziertes Schema unbekannt oder nicht auflösbar ist.

## 8. Objektversion

`object_version` bezeichnet die Version des fachlichen Objektzustands.

Die Objektversion:

- ändert sich bei fachlich relevanten Änderungen;
- ist nicht mit der Schemaversion gleichzusetzen;
- ist nicht mit einer Repository- oder Release-Version gleichzusetzen;
- muss Vergleiche und Konflikterkennung ermöglichen;
- darf nicht stillschweigend zurückgesetzt oder wiederverwendet werden.

Das konkrete Versionierungsverfahren wird später festgelegt.

## 9. Lebenszyklusstatus

Jedes Objekt besitzt genau einen aktuellen fachlichen Lebenszyklusstatus.

Die zulässigen Statuswerte werden durch den Objekttyp oder dessen Schema definiert.

Ein gemeinsamer Grundvorrat kann enthalten:

- `neu`;
- `entwurf`;
- `aktiv`;
- `gesperrt`;
- `veraltet`;
- `archiviert`;
- `gelöscht`.

Nicht jeder Objekttyp muss alle Statuswerte verwenden.

Statusübergänge müssen ausdrücklich zulässig, validierbar und nachvollziehbar sein.

## 10. Domänenverantwortung

`domain_owner` bezeichnet die fachlich zuständige Domäne.

Die zuständige Domäne verantwortet:

- Typdefinition;
- Schema;
- Lebenszyklus;
- Validierung;
- zulässige Beziehungen;
- Kompatibilität;
- Migrationen;
- fachliche Entscheidungen.

Die Domänenverantwortung ist nicht automatisch mit Eigentum oder Zugriffsberechtigung gleichzusetzen.

## 11. Eigentum und Verantwortlichkeit

Objekte können zusätzlich fachliche Eigentümer oder Verantwortliche besitzen.

Solche Angaben werden als ausdrücklich typisierte Referenzen modelliert, beispielsweise:

- Eigentümer;
- Verantwortlicher;
- Freigabeverantwortlicher;
- Betreiber;
- Verwalter.

Diese Referenzen verweisen auf Identitäten oder andere dafür zugelassene Objekte, nicht ausschließlich auf Benutzerkonten.

Die genaue Identitäts- und Berechtigungsarchitektur wird in eigenen Modellen und ADRs festgelegt.

## 12. Urheber- und Änderungsinformationen

Jedes Objekt besitzt mindestens:

- `created_at`;
- `created_by`;
- `modified_at`;
- `modified_by`.

Zeitangaben müssen eindeutig interpretierbar sein.

Akteursreferenzen müssen auf eine nachverfolgbare Identität oder einen ausdrücklich definierten Systemprozess verweisen.

Ein Objekt darf keine sicherheits- oder revisionsrelevante Änderung mit unbekanntem Urheber akzeptieren, sofern keine ausdrücklich dokumentierte Ausnahme besteht.

## 13. Beziehungen

`relations` enthält die fachlich gültigen Beziehungen des Objekts.

Jede Beziehung besitzt mindestens:

- einen Beziehungstyp;
- eine Quellreferenz;
- eine Zielreferenz;
- einen Status;
- gegebenenfalls eine eigene Version;
- gegebenenfalls eigene Eigenschaften.

Beziehungen müssen durch das zuständige Schema oder Beziehungsmodell erlaubt sein.

Eine Beziehung darf nicht allein durch das Vorhandensein eines technischen Fremdschlüssels als fachlich gültig gelten.

## 14. Optionale Kernattribute

Die Plattform kann gemeinsame optionale Kernattribute vorsehen, darunter:

- Anzeigename;
- Beschreibung;
- fachlicher Eigentümer;
- verantwortliche Identität;
- Freigabestatus;
- Klassifikation;
- Tags;
- Herkunft;
- externe Referenzen;
- Archivierungsgrund;
- Löschgrund;
- Gültigkeitszeitraum.

Ob ein solches Attribut für einen Objekttyp verpflichtend ist, legt dessen Schema fest.

## 15. Fachattribute

Fachattribute werden ausschließlich durch das zuständige Fachmodell oder Schema definiert.

Sie müssen:

- eindeutig benannt sein;
- einen dokumentierten Zweck besitzen;
- validierbar sein;
- mit der Projektsprache und Terminologie übereinstimmen;
- versioniert werden;
- migrationsfähig sein, wenn sie dauerhaft gespeichert werden.

Ein Fachattribut darf keine bereits vorhandene Kernbedeutung neu definieren.

## 16. Historie

Jedes Objekt muss so verwaltet werden können, dass wesentliche Zustandsänderungen nachvollziehbar bleiben.

Die Historie soll, soweit relevant, beantworten:

- was wurde geändert;
- wann wurde geändert;
- durch wen oder welchen Prozess wurde geändert;
- aus welchem Grund wurde geändert;
- welche Objekt- und Schemaversion war betroffen;
- welche Beziehungen wurden verändert.

Dieses Dokument legt nicht fest, ob Historie durch Ereignisse, Versionen, Änderungsprotokolle oder andere Mechanismen gespeichert wird.

## 17. Validierung

Jedes Objekt muss gegen seinen universellen Vertrag und sein fachliches Schema validierbar sein.

Die Mindestvalidierung umfasst:

- gültige und eindeutige Objektidentität;
- bekannten Objekttyp;
- auflösbare Schemareferenz;
- gültige Schemaversion;
- konsistente Objektversion;
- zulässigen Lebenszyklusstatus;
- bekannte Domänenverantwortung;
- gültige Urheber- und Zeitangaben;
- gültige Beziehungen;
- vollständige Pflichtattribute;
- Einhaltung fachlicher Invarianten.

Validierungsfehler dürfen nicht stillschweigend ignoriert werden.

## 18. Invarianten

Für jedes Objekt gelten mindestens folgende Invarianten:

1. Ein Objekt besitzt genau eine stabile Objektidentität.
2. Eine Objektidentität wird nicht wiederverwendet.
3. Ein Objekt besitzt genau einen aktuellen Objekttyp.
4. Ein Objekt verweist auf genau ein maßgebliches Schema und eine Schemaversion.
5. Ein Objekt besitzt genau eine aktuelle Objektversion.
6. Ein Objekt besitzt genau einen aktuellen Lebenszyklusstatus.
7. Jede fachliche Änderung ist einer nachverfolgbaren Identität oder einem definierten Prozess zugeordnet.
8. Jede Beziehung ist typisiert und validierbar.
9. Fachattribute widersprechen keinen Kernattributen.
10. Ein ungültiges Objekt darf nicht als erfolgreich gespeichert oder freigegeben gemeldet werden.
11. Ein Objekt darf sich nicht durch widersprüchliche Kerninformationen selbst beschreiben.
12. Änderungen an Identität, Typ, Schema, Status und Beziehungen erfolgen nur über definierte Regeln.

## 19. Lesesicht und Änderungssicht

Die Plattform unterscheidet fachlich zwischen:

- dem Lesen eines aktuellen oder historischen Objektzustands;
- dem Anfordern einer Objektänderung;
- der Validierung einer Objektänderung;
- der bestätigten Speicherung einer Objektänderung.

Eine Änderung gilt erst dann als wirksam, wenn sie validiert und durch den zuständigen Objektdienst bestätigt wurde.

Die konkreten Operationen werden in `OBJECT_SERVICE.md` definiert.

## 20. Erweiterbarkeit

Neue gemeinsame Kernattribute dürfen nur eingeführt werden, wenn sie:

- für mehrere unabhängige Objekttypen erforderlich sind;
- nicht sinnvoll als Fachattribut modelliert werden können;
- eine klar definierte Semantik besitzen;
- Auswirkungen auf bestehende Objekte und Schemata berücksichtigen;
- durch Review und gegebenenfalls ADR freigegeben wurden.

Domänenspezifische Anforderungen dürfen die universelle Schnittstelle nicht unnötig erweitern.

## 21. Nicht festgelegt

Dieses Dokument legt ausdrücklich noch nicht fest:

- das UUID- oder ID-Format;
- konkrete Feldnamen in Code oder Dateien;
- Serialisierungsformate;
- Datenbanktabellen;
- API-Protokolle;
- Event Sourcing;
- Speicherorte von Beziehungen;
- konkrete Statuswerte aller Objekttypen;
- konkrete Identitäts-, Rollen- oder Berechtigungsmodelle.

Diese Entscheidungen erfolgen in nachgeordneten Modellen, Spezifikationen oder ADRs.

## 22. Abhängigkeiten

Dieses Dokument konkretisiert:

- `PROJECT_CONSTITUTION.md`;
- `PROJECT_PRINCIPLES.md`;
- `PROJECT_GLOSSARY.md`;
- `OBJECT_MODEL.md`.

Es bildet gemeinsam mit `OBJECT_MODEL.md` die Grundlage für `OBJECT_SERVICE.md`.
