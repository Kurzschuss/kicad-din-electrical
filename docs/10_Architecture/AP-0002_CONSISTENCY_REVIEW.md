# Konsistenzreview AP-0002

**Dokument-ID:** REV-0001  
**Titel:** Konsistenzreview des Kernmodells  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** C  
**Autoritätsebene:** Review-Nachweis  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Zweck

Dieses Dokument weist das Konsistenzreview der in AP-0002 entstandenen Core-Artefakte nach.

Geprüft wurden:

- `CORE_MODEL.md`;
- `OBJECT_MODEL.md`;
- `OBJECT_INTERFACE.md`;
- `OBJECT_SERVICE.md`;
- `SCHEMA_MODEL.md`;
- `RELATION_MODEL.md`;
- ADR-0002;
- ADR-0003;
- ADR-0004.

## 2. Prüfkriterien

Das Review prüft insbesondere:

- eindeutige Zuständigkeit jedes Dokuments;
- Widerspruchsfreiheit;
- Einhaltung der Kernelgrenze;
- Trennung von Core, Plattform und Domäne;
- Rekursion von Schema und Beziehung als Objekte;
- eindeutige Identitätsbegriffe;
- Referenzierbarkeit und Validierbarkeit;
- offene technische Entscheidungen;
- unzulässige Doppeldefinitionen.

## 3. Ergebnisübersicht

| Prüfbereich | Ergebnis | Maßnahme |
|---|---|---|
| Objektdefinition | bestanden | keine grundlegende Korrektur erforderlich |
| Objektschnittstelle | bestanden mit Klärung | opake Akteurs- und Verantwortungsreferenzen durch ADR-0004 festgelegt |
| Objektdienst | bestanden mit Klärung | Autorisierung wird von der Plattform entschieden; Core erzwingt nur deren Beachtung |
| Schemamodell | bestanden mit Klärung | kontrollierter Core-Metaschema-Bootstrap durch ADR-0004 festgelegt |
| Beziehungsmodell | bestanden | persistente und abgeleitete Beziehungen sind getrennt |
| Kernelgrenze | bestanden mit Klärung | opake Referenzen gelten nicht als Modellabhängigkeit |
| Identitätsbegriffe | bestanden | Objektidentität und Akteursidentität sind getrennt |
| Technologieneutralität | bestanden | konkrete Formate und Technologien bleiben offen |

## 4. Feststellung F-001: Core und Akteursreferenzen

### Beobachtung

`OBJECT_INTERFACE.md` und `OBJECT_SERVICE.md` verwenden Akteursangaben wie `created_by` und `modified_by`. ADR-0003 verbietet dem Core gleichzeitig Kenntnisse über Plattformmodelle.

### Bewertung

Ohne zusätzliche Regel wäre unklar, ob diese Angaben eine unzulässige Abhängigkeit zur Identitätsplattform erzeugen.

### Entscheidung

Die Angaben werden als opake, typisierte Referenzen behandelt. Der Core speichert und prüft ihre Referenzintegrität, kennt aber nicht das vollständige Zielmodell.

### Nachweis

ADR-0004.

### Status

Geklärt.

## 5. Feststellung F-002: Domänenverantwortung im Core

### Beobachtung

Core-Objekte und Schemata besitzen eine zuständige Domäne oder einen Verantwortungsbezug, während der Core keine konkrete Domäne kennen darf.

### Bewertung

Die Information ist für Ownership und Nachvollziehbarkeit erforderlich, darf aber nicht zu domänenspezifischer Logik im Core führen.

### Entscheidung

Die Verantwortungsangabe ist eine opake Referenz. Ihre fachliche Bedeutung und Zulässigkeit werden außerhalb des Core definiert.

### Nachweis

ADR-0004.

### Status

Geklärt.

## 6. Feststellung F-003: Autorisierung im Objektdienst

### Beobachtung

Der Objektdienst verlangt Berechtigungsprüfungen, obwohl Rollen und Berechtigungen Plattformkonzepte sind.

### Bewertung

Der Core darf keine Autorisierungsregeln definieren, muss geschützte Operationen aber gegen Umgehung absichern.

### Entscheidung

Die Plattform ermittelt die Autorisierungsentscheidung. Der Core verlangt und beachtet einen Autorisierungskontext beziehungsweise eine Entscheidung, interpretiert aber keine Rollen oder Berechtigungsmodelle.

### Nachweis

ADR-0004.

### Status

Geklärt.

## 7. Feststellung F-004: Schema als Objekt

### Beobachtung

Ein Schema ist selbst ein Objekt. Jedes Objekt verweist auf ein Schema. Daraus entsteht ohne Startpunkt eine rekursive Abhängigkeit.

### Bewertung

Die Rekursion muss kontrolliert beendet werden, ohne Schemata ihre Objektidentität, Version und Historie zu nehmen.

### Entscheidung

Ein minimaler, versionierter Core-Metaschema-Vertrag bildet den Bootstrap. Reguläre Schemata folgen anschließend vollständig den gewöhnlichen Schemaregeln.

### Nachweis

ADR-0004.

### Status

Geklärt; Detailartefakt für das Core-Metaschema noch offen.

## 8. Feststellung F-005: Beziehung als Objekt

### Beobachtung

`RELATION_MODEL.md` behandelt fachlich relevante Beziehungen als Objekte, erlaubt aber auch reproduzierbare abgeleitete Beziehungen ohne eigenes persistentes Objekt.

### Bewertung

Die Unterscheidung ist erforderlich, damit nicht jede technische oder berechnete Verbindung künstlich persistiert werden muss.

### Entscheidung

Persistente Beziehungen benötigen eigene Identität, Schema, Version und Lebenszyklus. Abgeleitete Beziehungen müssen reproduzierbar und als abgeleitet gekennzeichnet sein und dürfen nicht unabhängig geändert werden.

### Status

Bestanden.

## 9. Feststellung F-006: Doppelte Definitionen

### Beobachtung

Identität, Schema, Beziehungen, Historie und Validierung werden in mehreren Dokumenten erwähnt.

### Bewertung

Die Wiederholungen sind überwiegend kontextbezogene Verträge, keine konkurrierenden Definitionen:

- `OBJECT_MODEL.md` definiert das Objekt fachlich;
- `OBJECT_INTERFACE.md` definiert den gemeinsamen Objektvertrag;
- `OBJECT_SERVICE.md` definiert Operationen und Garantien;
- `SCHEMA_MODEL.md` definiert Schemata;
- `RELATION_MODEL.md` definiert Beziehungen;
- `CORE_MODEL.md` definiert Umfang und Grenzen.

### Maßnahme

Untergeordnete Dokumente sollen bei späteren Überarbeitungen verstärkt auf die maßgebliche Definition verweisen, statt vollständige Definitionen zu wiederholen.

### Status

Akzeptiert mit redaktioneller Folgeaufgabe.

## 10. Feststellung F-007: Eigenschaft, Ereignis, Version und Lebenszyklus

### Beobachtung

Diese Konzepte sind im `CORE_MODEL.md` aufgeführt, besitzen aber noch keine eigenen Detailmodelle.

### Bewertung

Das ist derzeit kein Widerspruch. Die vorhandenen Modelle enthalten ausreichende Mindestregeln für AP-0002.

Eigene Dokumente werden erst erstellt, wenn eine unabhängige Verantwortung nachgewiesen ist und die bestehenden Modelle nicht mehr ausreichen.

### Status

Bewusst offen.

## 11. Offene Folgearbeiten

Aus dem Review entstehen folgende klar begrenzte Folgearbeiten:

1. Core-Metaschema als eigenes minimales Artefakt spezifizieren.
2. Opaque Referenz und Referenzauflösung später technisch spezifizieren.
3. Autorisierungskontext als Vertrag zwischen Plattform und Core definieren.
4. Redaktionelle Wiederholungen bei der nächsten Dokumentversion reduzieren.
5. Dokument-IDs und Ordnerstruktur nach Annahme der Architekturebenen konsolidieren.

Diese Punkte verhindern nicht die Fortsetzung der Architekturarbeit, solange ADR-0004 als maßgebliche Klärung beachtet wird.

## 12. Review-Urteil

AP-0002 ist inhaltlich konsistent genug, um als geschlossener Core-Entwurf in das nächste Review- und Freigabestadium überzugehen.

Es wurden keine ungelösten Widersprüche gefunden, die das Objekt-, Schema- oder Beziehungsmodell grundsätzlich unbrauchbar machen.

Die kritischen Punkte Core-Referenzen, Autorisierung und Schema-Bootstrap sind durch ADR-0004 ausdrücklich entschieden.

## 13. Empfohlener nächster Schritt

Vor weiteren Core-Modellen soll das minimale Core-Metaschema spezifiziert werden.

Danach kann die Plattformebene mit `PROJECT_MODEL.md` beginnen, ohne die Kernelgrenze erneut zu öffnen.