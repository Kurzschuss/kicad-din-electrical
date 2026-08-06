# ADR-0004: Core-Referenzen und Schema-Bootstrap

**Dokument-ID:** ADR-0004  
**Titel:** Opaque Core-Referenzen und kontrollierter Schema-Bootstrap  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** A  
**Entscheidungsart:** Grundlegende Architekturentscheidung  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Kontext

Das Konsistenzreview von AP-0002 hat zwei Spannungen sichtbar gemacht.

Erstens verwenden Core-Artefakte Angaben wie `created_by`, `modified_by`, `domain_owner`, Eigentümer und Verantwortliche. Gleichzeitig legt ADR-0003 fest, dass der Core keine Plattform- oder Domänenmodelle kennen darf.

Zweitens werden Schemata und bestimmte Beziehungen selbst als Objekte modelliert. Jedes Objekt verweist jedoch auf ein Schema. Ohne ausdrückliche Bootstrap-Regel entsteht eine unendliche Begründungskette: Ein Schema benötigt ein Schema, dessen Schema wiederum ein Schema benötigt.

## 2. Problemstellung

Es muss geklärt werden:

- wie der Core auf Akteure, Verantwortungsbereiche und andere externe Konzepte verweisen darf, ohne deren Modelle zu kennen;
- ob solche Verweise fachliche Abhängigkeiten zum Plattformmodell erzeugen;
- wie die ersten Core-Schemata gültig beschrieben und validiert werden;
- wie verhindert wird, dass ein Bootstrap-Mechanismus zu einem unkontrollierten Sonderweg wird.

## 3. Entscheidung

### 3.1 Opaque Referenzen

Der Core darf stabile, typisierte und auflösbare Referenzen auf außerhalb des Core definierte Objekte tragen.

Eine solche Referenz ist **opak**. Der Core kennt ausschließlich:

- die stabile Zielreferenz;
- die Referenzart oder erwartete Zielkategorie;
- den Auflösungsstatus;
- gegebenenfalls die für die Core-Operation notwendige Minimalinformation.

Der Core kennt nicht:

- das vollständige Plattform- oder Domänenmodell des Zielobjekts;
- konkrete Benutzer-, Konto-, Rollen- oder Berechtigungsregeln;
- konkrete Organisations- oder Projekthierarchien;
- domänenspezifische Eigenschaften des Zielobjekts.

Damit erzeugt das Tragen einer opaken Referenz keine umgekehrte Modellabhängigkeit.

### 3.2 Akteursreferenzen

Angaben wie `created_by` und `modified_by` sind im Core opake Akteursreferenzen.

Der Core verlangt lediglich, dass eine Referenz:

- stabil ist;
- nach dem vorgesehenen Betriebsmodus auflösbar oder nachvollziehbar ist;
- nicht stillschweigend auf ein anderes Ziel umgedeutet wird.

Ob das Ziel ein Benutzer, Gerät, Dienst, API-Client, eine Automatisierung oder ein Systemprozess ist, entscheidet die Plattform.

### 3.3 Verantwortungsreferenzen

`domain_owner`, Eigentümer und Verantwortliche werden als unterschiedliche typisierte Referenzen behandelt.

Der Core darf prüfen, ob eine erforderliche Referenz vorhanden, syntaktisch gültig und grundsätzlich auflösbar ist. Die fachliche Bedeutung, Berechtigung und Zulässigkeit des referenzierten Zieltyps wird durch Plattform- oder Domänenmodelle festgelegt.

### 3.4 Autorisierungsentscheidungen

Der Core definiert keine Rollen oder Berechtigungen.

Schreibende Core-Operationen dürfen jedoch eine bereits ermittelte Autorisierungsentscheidung oder einen prüfbaren Autorisierungskontext verlangen.

Die Plattform ist verantwortlich für die Ermittlung dieser Entscheidung. Der Core ist verantwortlich dafür, eine erforderliche Entscheidung nicht zu umgehen und ihr Ergebnis in der Operation zu beachten.

### 3.5 Schema-Bootstrap

Der Kernel verwendet einen kontrollierten Bootstrap für seine grundlegenden Schemata.

Dafür gilt:

1. Es existiert ein minimaler, versionierter **Core-Metaschema-Vertrag**.
2. Dieser Vertrag definiert nur die Struktur, die erforderlich ist, um Core-Schemata eindeutig zu identifizieren, zu versionieren und zu validieren.
3. Das Core-Metaschema darf sich selbst beschreiben oder durch eine fest definierte Bootstrap-Repräsentation beschrieben werden.
4. Die Bootstrap-Repräsentation ist Teil des vertrauenswürdigen Kernelkerns und wird besonders streng versioniert und geprüft.
5. Alle regulären Schemata, einschließlich späterer Versionen des Core-Metaschemas, werden nach den gewöhnlichen Schemaregeln behandelt.

### 3.6 Begrenzung des Bootstrap

Der Bootstrap darf keine allgemeinen Fachregeln, Plattformregeln oder Domänensonderfälle enthalten.

Er darf ausschließlich die kleinste notwendige Grundlage definieren für:

- stabile Schemaidentität;
- Schemaversion;
- grundlegende Eigenschaftsdefinitionen;
- grundlegende Referenzen;
- Validierungsregel-Identität;
- Lebenszyklus- und Freigabestatus des Schemas.

Eine Erweiterung des Bootstrap erfordert ein eigenes ADR und eine ausdrückliche Kompatibilitätsanalyse.

## 4. Abhängigkeitsregel

Die Abhängigkeitsrichtung bleibt unverändert:

```text
Core → keine Kenntnis konkreter Plattform- oder Domänenmodelle
Plattform → verwendet Core und löst opake Referenzen fachlich auf
Domäne → verwendet Core und Plattform
```

Eine opake Referenz ist keine Modellkenntnis. Sobald der Core Eigenschaften oder Regeln des Zielmodells auswertet, wäre die Kernelgrenze verletzt.

## 5. Auswirkungen auf bestehende Dokumente

### 5.1 `OBJECT_INTERFACE.md`

- `created_by` und `modified_by` sind opake Akteursreferenzen.
- `domain_owner` ist eine opake Verantwortungsreferenz.
- Eigentümer und Verantwortliche werden nicht im Core fachlich interpretiert.

### 5.2 `OBJECT_SERVICE.md`

- Der Objektdienst definiert keine Berechtigungsmodelle.
- Er verlangt bei geschützten Operationen einen Autorisierungskontext oder eine Autorisierungsentscheidung der Plattform.
- Er darf eine fehlende oder negative Entscheidung nicht umgehen.

### 5.3 `SCHEMA_MODEL.md`

- Das Core-Metaschema und sein Bootstrap werden als ausdrückliche Ausnahme mit eng begrenztem Zweck aufgenommen.
- Reguläre Schemata bleiben vollständig schema- und versionsgebunden.

### 5.4 `RELATION_MODEL.md`

- Persistente Beziehungen verwenden reguläre Beziehungsschemata.
- Beziehungen, die zum Schema-Bootstrap selbst gehören, dürfen nur die minimalen Regeln des Core-Metaschemas verwenden.

### 5.5 `CORE_MODEL.md` und ADR-0003

- Die Kernelgrenze bleibt bestehen.
- Opaque Referenzen werden ausdrücklich als zulässiger Mechanismus ergänzt.

## 6. Betrachtete Alternativen

### 6.1 Akteure und Domänen vollständig in den Core aufnehmen

Diese Alternative wurde verworfen, weil sie Benutzer-, Organisations- und Domänenmodelle in den Kernel ziehen und dessen Unabhängigkeit aufheben würde.

### 6.2 Core-Objekte ohne Urheber- und Verantwortungsreferenzen

Diese Alternative wurde verworfen, weil Nachvollziehbarkeit, Auditierbarkeit und kontrollierte Zuständigkeit dadurch erst nachträglich und uneinheitlich ergänzt würden.

### 6.3 Schemata nicht als Objekte behandeln

Diese Alternative wurde verworfen, weil Schemata stabile Identität, Version, Lebenszyklus, Historie und Referenzierbarkeit benötigen.

### 6.4 Unbegrenzte Selbstbeschreibung

Diese Alternative wurde verworfen, weil eine vollständig freie Selbstbeschreibung schwer prüfbar ist und die Gefahr zirkulärer, nicht deterministischer Definitionen erzeugt.

## 7. Konsequenzen

### Positive Konsequenzen

- Kernelgrenze und Nachvollziehbarkeit bleiben gleichzeitig erhalten;
- menschliche und technische Akteure können einheitlich referenziert werden;
- Plattformmodelle bleiben austauschbar und erweiterbar;
- Schema-Selbstbeschreibung erhält einen kontrollierten Startpunkt;
- zirkuläre Definitionsprobleme werden ausdrücklich gelöst;
- Autorisierung bleibt getrennt vom Objektdienst.

### Negative Konsequenzen

- Referenzauflösung benötigt klare Schnittstellen zwischen Core und Plattform;
- nicht auflösbare Referenzen müssen als eigener Zustand behandelt werden;
- der Core-Metaschema-Vertrag wird zu einem besonders kritischen Artefakt;
- Änderungen am Bootstrap benötigen hohen Prüfaufwand.

## 8. Invarianten

1. Eine opake Referenz darf vom Core nicht fachlich umgedeutet werden.
2. Der Core darf keine Rollen-, Konto- oder Organisationsregeln auswerten.
3. Eine schreibende geschützte Operation darf eine erforderliche Autorisierungsentscheidung nicht umgehen.
4. Das Bootstrap-Metaschema bleibt minimal und domänenunabhängig.
5. Eine veröffentlichte Bootstrap-Version wird nicht rückwirkend in ihrer Bedeutung verändert.
6. Reguläre Schemata verwenden nach dem Bootstrap die gewöhnlichen Schema-, Versions- und Migrationsregeln.
7. Nicht auflösbare Referenzen werden ausdrücklich gemeldet und nicht stillschweigend ersetzt.

## 9. Nicht festgelegt

Dieses ADR legt noch nicht fest:

- das konkrete Referenzformat;
- die konkrete Resolver-Schnittstelle;
- die technische Darstellung des Core-Metaschemas;
- die konkrete Autorisierungs-API;
- das konkrete UUID- oder Versionsformat;
- die Speicherung und Verteilung des Bootstrap-Artefakts.

## 10. Akzeptanzkriterien

Dieses ADR gilt als umgesetzt, wenn:

- Core-Dokumente Akteurs- und Verantwortungsangaben als opake Referenzen behandeln;
- der Objektdienst keine eigenen Rollen- oder Berechtigungsmodelle definiert;
- der Schema-Bootstrap ausdrücklich dokumentiert ist;
- das Core-Metaschema minimal und versioniert spezifiziert wird;
- reguläre Schemata nach dem Bootstrap den normalen Schemaregeln folgen;
- Referenzauflösungsfehler unterscheidbar behandelt werden.

## 11. Entscheidungsergebnis

Der Core darf opake Referenzen auf Plattform- und Domänenobjekte tragen, ohne deren Modelle zu kennen. Die fachliche Auflösung und Autorisierung verbleibt außerhalb des Core.

Die Rekursion von Schemata als Objekten wird durch einen minimalen, kontrollierten und versionierten Core-Metaschema-Bootstrap beendet.