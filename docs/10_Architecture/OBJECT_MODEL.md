# Objektmodell

**Dokument-ID:** ARC-0001  
**Titel:** Grundlegendes Objektmodell  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Architekturmodell  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Zweck

Dieses Dokument definiert den fachlichen Begriff „Objekt“ als kleinste gemeinsame, dauerhaft identifizierbare Einheit der Plattform.

Es beschreibt die Eigenschaften und Regeln, die für alle Objekte gelten, unabhängig davon, ob ein Objekt später beispielsweise ein Gerät, Benutzer, Projekt, Dokument, Symbol, Footprint, Test, Dienst oder eine Simulation repräsentiert.

Dieses Dokument definiert keine konkrete Programmiersprache, Klasse, Datenbanktabelle, Datei- oder Übertragungsstruktur.

## 2. Geltungsbereich

Das Objektmodell gilt für alle dauerhaft gespeicherten oder systemweit referenzierbaren fachlichen Einheiten.

Nicht jede temporäre Variable, Berechnung oder technische Hilfsstruktur ist automatisch ein Objekt im Sinne dieses Modells.

Eine Einheit wird als Objekt modelliert, wenn mindestens eine der folgenden Bedingungen erfüllt ist:

- sie besitzt eine fachlich relevante Identität;
- sie muss dauerhaft referenziert werden können;
- sie besitzt einen eigenen Lebenszyklus;
- sie hat Beziehungen zu anderen Objekten;
- Änderungen an ihr müssen nachvollziehbar sein;
- sie wird von mehreren Komponenten oder Domänen verwendet;
- sie benötigt eigene Validierungs-, Eigentums- oder Berechtigungsregeln.

## 3. Definition

Ein Objekt ist eine fachliche Einheit mit stabiler Identität, definiertem Typ, nachvollziehbarem Zustand und ausdrücklich modellierten Beziehungen.

Ein Objekt ist unabhängig von seiner technischen Darstellung.

Dasselbe Objekt kann gleichzeitig oder nacheinander durch unterschiedliche technische Darstellungen repräsentiert werden, ohne seine fachliche Identität zu verlieren.

## 4. Objekt und technische Darstellung

Ein Objekt ist nicht gleichbedeutend mit:

- einer Klasse;
- einer Instanz einer Programmiersprache;
- einer Datenbankzeile;
- einer Datei;
- einem JSON-, YAML- oder XML-Dokument;
- einem Benutzeroberflächenelement;
- einer Netzwerkressource;
- einem KiCad-Symbol oder Footprint als Dateiformat.

Solche Elemente können Darstellungen, Speicherformen oder technische Repräsentationen eines Objekts sein.

Die Zuordnung zwischen Objekt und Darstellung muss ausdrücklich definiert werden.

## 5. Identität

Jedes Objekt besitzt eine eindeutige, stabile und unveränderliche Objektidentität.

Die Identität wird bei der Erzeugung vergeben und darf während der Lebensdauer des Objekts nicht wiederverwendet oder stillschweigend ersetzt werden.

Die Objektidentität ist unabhängig von:

- Name;
- Anzeigename;
- Dateiname;
- Dateipfad;
- Speicherort;
- Eigentümer;
- Status;
- Version;
- technischer Darstellung;
- fachlicher Klassifikation.

Eine Änderung dieser Merkmale erzeugt nicht automatisch ein neues Objekt.

Die konkrete technische Form der Identität, beispielsweise UUID oder ein anderes Kennungsschema, wird in einer nachgeordneten Spezifikation oder einem ADR festgelegt.

## 6. Objekttyp

Jedes Objekt besitzt genau einen maßgeblichen Objekttyp.

Der Objekttyp beschreibt die fachliche Kategorie und legt fest:

- welches Schema gilt;
- welche Eigenschaften zulässig oder erforderlich sind;
- welche Beziehungen zulässig sind;
- welcher Lebenszyklus gilt;
- welche Validierungsregeln gelten;
- welche Domäne verantwortlich ist.

Ein Objekttyp ist selbst ein versioniertes und referenzierbares Architektur- oder Schemaartefakt.

Ob Mehrfachtypisierung, Vererbung oder Komposition unterstützt werden, wird später ausdrücklich entschieden.

## 7. Zustand

Der Zustand eines Objekts besteht aus den zum betrachteten Zeitpunkt gültigen Eigenschaften, Beziehungen, Statusangaben und Versionsinformationen.

Der Zustand ist veränderlich.

Die Identität ist davon unabhängig und bleibt stabil.

Ein Objekt darf nicht allein über seinen aktuellen Zustand definiert werden.

## 8. Eigenschaften

Eigenschaften beschreiben fachliche Merkmale eines Objekts.

Jede Eigenschaft besitzt mindestens:

- einen eindeutigen Namen innerhalb ihres Schemas;
- eine fachliche Bedeutung;
- einen Datentyp oder Wertebereich;
- eine Angabe, ob sie erforderlich oder optional ist;
- Validierungsregeln;
- gegebenenfalls einen Standardwert;
- gegebenenfalls Sichtbarkeits- oder Berechtigungsregeln.

Eigenschaften dürfen keine versteckten fachlichen Regeln enthalten.

Berechnete Eigenschaften müssen als berechnet gekennzeichnet sein und ihre maßgebliche Ableitung offenlegen.

## 9. Beziehungen

Beziehungen verbinden Objekte fachlich miteinander.

Eine Beziehung ist nicht lediglich ein technischer Fremdschlüssel oder eine Dateireferenz.

Eine Beziehung besitzt mindestens:

- einen Beziehungstyp;
- ein Ausgangsobjekt;
- ein Zielobjekt oder eine definierte Menge von Zielobjekten;
- eine Richtung oder ausdrücklich definierte Symmetrie;
- Kardinalitätsregeln;
- Validierungsregeln;
- gegebenenfalls einen eigenen Status und Lebenszyklus.

Beziehungen können eigene Eigenschaften besitzen, wenn diese fachlich zur Beziehung und nicht zu einem der beteiligten Objekte gehören.

Ob Beziehungen technisch als eigenständige Objekte gespeichert werden, wird in einem späteren Modell oder ADR entschieden.

## 10. Schema

Jedes Objekt verweist auf ein gültiges, versioniertes Schema.

Das Schema definiert die zulässige Struktur des Objekts.

Es beschreibt mindestens:

- erforderliche und optionale Eigenschaften;
- zulässige Datentypen und Wertebereiche;
- zulässige Beziehungen;
- Invarianten;
- Validierungsregeln;
- relevante Versions- und Migrationsregeln.

Ein Objekt darf nicht stillschweigend von seinem maßgeblichen Schema abweichen.

## 11. Domänenverantwortung

Jeder Objekttyp besitzt genau eine fachlich verantwortliche Domäne.

Die verantwortliche Domäne definiert:

- Bedeutung und Zweck;
- Schema;
- Lebenszyklus;
- Validierungsregeln;
- zulässige Änderungen;
- Kompatibilitätsregeln;
- maßgebliche Dienste und Schnittstellen.

Andere Domänen dürfen ein Objekt referenzieren und verwenden, aber seine fachliche Definition nicht eigenständig verändern.

## 12. Eigentum und Verantwortung

Fachliches Eigentum, technische Verwaltung und Berechtigung sind getrennte Konzepte.

Ein Objekt kann einen fachlichen Eigentümer besitzen. Der Eigentümer ist jedoch nicht automatisch berechtigt, jede technische oder sicherheitsrelevante Änderung auszuführen.

Ein Objekt kann außerdem verantwortliche Rollen, Benutzer, Organisationseinheiten oder Systemprozesse referenzieren.

Die vollständige Ausgestaltung erfolgt später in den Modellen für Identität, Rollen und Berechtigungen.

## 13. Lebenszyklus

Jeder Objekttyp besitzt einen ausdrücklich definierten Lebenszyklus.

Ein Lebenszyklus besteht aus:

- zulässigen Zuständen;
- zulässigen Zustandsübergängen;
- Voraussetzungen für Übergänge;
- Auswirkungen eines Übergangs;
- verantwortlichen Akteuren oder Diensten;
- erforderlichen Validierungen und Ereignissen.

Ein Objekt darf nicht in einen fachlich unzulässigen Zustand überführt werden.

Das Löschen eines Objekts ist ein Lebenszyklusvorgang und keine rein technische Speicheroperation.

## 14. Erzeugung

Bei der Erzeugung eines Objekts müssen mindestens feststehen:

- Objektidentität;
- Objekttyp;
- Schemaversion;
- verantwortliche Domäne;
- initialer Lebenszyklusstatus;
- Erzeugungszeitpunkt;
- erzeugender Akteur oder Prozess, soweit anwendbar.

Ein Objekt gilt erst als erzeugt, wenn seine Mindestinvarianten erfüllt sind.

## 15. Änderung

Änderungen an Objekten erfolgen ausschließlich über definierte und validierbare Vorgänge.

Eine Änderung muss, soweit für Bedeutung und Risiko erforderlich, erkennen lassen:

- welches Objekt betroffen ist;
- welche Werte oder Beziehungen geändert werden;
- wer oder welcher Prozess die Änderung veranlasst;
- wann sie erfolgt;
- auf welcher Version sie basiert;
- warum sie erfolgt;
- welche Validierung durchgeführt wurde.

Teilweise oder fehlgeschlagene Änderungen dürfen nicht als erfolgreich abgeschlossen gelten.

## 16. Löschung, Deaktivierung und Archivierung

Physische Löschung, fachliche Löschung, Deaktivierung und Archivierung sind unterschiedliche Vorgänge.

Sie dürfen nicht gleichgesetzt werden.

Vor einer Löschung müssen mindestens geprüft werden:

- bestehende Beziehungen;
- Aufbewahrungs- und Nachweispflichten;
- Historie;
- Referenzintegrität;
- Berechtigungen;
- Wiederherstellbarkeit;
- Auswirkungen auf abhängige Objekte.

Die konkreten Regeln werden je Objekttyp definiert.

## 17. Versionierung

Objektidentität und Objektversion sind getrennt.

Mehrere Versionen können dasselbe fachliche Objekt beschreiben.

Eine neue Version erzeugt nicht automatisch eine neue Objektidentität.

Die Versionierung muss mindestens unterscheiden können zwischen:

- Änderung des Objektzustands;
- Änderung der technischen Darstellung;
- Änderung des Schemas;
- Änderung des Objekttyps oder seiner fachlichen Bedeutung;
- inkompatibler Neudefinition.

Die konkrete Versionsstrategie wird in einer nachgeordneten Spezifikation festgelegt.

## 18. Historie

Für fachlich relevante Objekte wird eine nachvollziehbare Änderungshistorie geführt.

Die Historie soll, soweit anwendbar, beantworten:

- was geändert wurde;
- wann es geändert wurde;
- wer oder welcher Prozess die Änderung vorgenommen hat;
- warum die Änderung vorgenommen wurde;
- welche Version vorher und nachher gültig war;
- welche Beziehungen betroffen waren.

Historie ist nicht automatisch mit vollständigem Event Sourcing gleichzusetzen.

Die technische Historienstrategie wird später entschieden.

## 19. Ereignisse

Ein Ereignis beschreibt eine fachlich bedeutsame, bereits eingetretene Tatsache.

Ereignisse können unter anderem entstehen durch:

- Erzeugung;
- Zustandsänderung;
- Änderung einer Eigenschaft;
- Erzeugung oder Auflösung einer Beziehung;
- Validierungsfehler;
- Migration;
- Archivierung oder Löschung.

Ob jedes Ereignis selbst als Objekt modelliert wird, ist noch nicht entschieden.

Ereignisse dürfen nicht mit Befehlen oder Änderungswünschen verwechselt werden.

## 20. Validierung

Ein Objekt ist gültig, wenn es:

- eine gültige Identität besitzt;
- einem bekannten Objekttyp entspricht;
- auf ein gültiges Schema verweist;
- alle erforderlichen Eigenschaften enthält;
- alle Eigenschaftsregeln erfüllt;
- nur zulässige Beziehungen besitzt;
- einen gültigen Lebenszyklusstatus besitzt;
- alle Invarianten erfüllt.

Validierung erfolgt bei Erzeugung, Änderung, Migration und vor sicherheits- oder integritätsrelevanten Vorgängen.

## 21. Invarianten

Für jedes Objekt gelten mindestens folgende unveränderliche Grundregeln:

1. Die Objektidentität ist eindeutig und stabil.
2. Das Objekt besitzt genau einen maßgeblichen Objekttyp.
3. Das Objekt verweist auf ein gültiges Schema.
4. Der aktuelle Zustand erfüllt das maßgebliche Schema.
5. Beziehungen verweisen nur auf gültige und zulässige Ziele.
6. Lebenszyklusübergänge erfolgen ausschließlich nach definierten Regeln.
7. Fachlich relevante Änderungen sind nachvollziehbar.
8. Die verantwortliche Domäne ist eindeutig.
9. Berechtigungsprüfungen dürfen nicht durch die technische Darstellung umgangen werden.
10. Eine technische Migration darf die fachliche Identität nicht stillschweigend verändern.

## 22. Referenzierung

Objekte werden über ihre stabile Objektidentität referenziert.

Namen, Pfade und Darstellungskennungen können als Such- oder Komfortmerkmale dienen, sind aber keine dauerhaften Primärreferenzen.

Eine Referenz muss erkennen lassen, auf welches Objekt und gegebenenfalls auf welche Version oder Darstellung sie sich bezieht.

Ungültige oder nicht auflösbare Referenzen müssen erkennbar sein und dürfen nicht stillschweigend auf ein anderes Objekt umgebogen werden.

## 23. Gleichheit und Vergleich

Zwei Darstellungen gelten als Darstellungen desselben Objekts, wenn sie dieselbe Objektidentität besitzen.

Gleiche Eigenschaftswerte allein bedeuten nicht, dass zwei Einheiten dasselbe Objekt sind.

Für fachliche Vergleiche können zusätzliche Gleichheitsregeln je Objekttyp definiert werden.

## 24. Kopie, Ableitung und Variante

Eine Kopie, Ableitung oder Variante muss ausdrücklich modelliert werden.

Es ist zu unterscheiden zwischen:

- neuer Darstellung desselben Objekts;
- neuer Version desselben Objekts;
- neuem Objekt auf Basis eines bestehenden Objekts;
- Variante eines Objekttyps;
- technischer Kopie ohne eigene fachliche Identität.

Bei Erzeugung eines neuen Objekts wird eine neue Objektidentität vergeben und die Herkunft gegebenenfalls als Beziehung dokumentiert.

## 25. Erweiterbarkeit

Neue Objekttypen erweitern das Kernmodell durch eigene Schemata, Lebenszyklen, Beziehungen und Validierungsregeln.

Sie dürfen die Grundinvarianten dieses Dokuments nicht umgehen.

Domänenspezifische Sonderregeln müssen in der zuständigen Domäne dokumentiert werden und dürfen nicht unbemerkt in den Kern einfließen.

## 26. Benutzer, Geräte und technische Akteure

Dieses Objektmodell entscheidet noch nicht abschließend, wie Benutzer, Identitäten, Konten, Geräte, Dienste und API-Clients untereinander abgegrenzt werden.

Es legt lediglich fest, dass dauerhaft referenzierbare fachliche Einheiten und Akteure nach denselben Grundregeln für Identität, Typ, Schema, Lebenszyklus, Historie und Beziehungen modelliert werden können.

Die Identitätsplattform wird in eigenen Modellen und mindestens einem ADR definiert.

## 27. Nicht-Ziele

Dieses Dokument legt ausdrücklich noch nicht fest:

- das konkrete Format der Objekt-ID;
- ein konkretes Dateiformat;
- eine Datenbankstruktur;
- eine API;
- eine Programmiersprache;
- ein Klassenmodell;
- Event Sourcing;
- CQRS;
- Mehrfachvererbung;
- die konkrete Speicherung von Beziehungen;
- die konkrete Historien- und Migrationsstrategie;
- die vollständige Identitäts- und Berechtigungsarchitektur.

Diese Entscheidungen erfolgen in nachgeordneten Spezifikationen und ADRs.

## 28. Abhängigkeiten

Dieses Dokument konkretisiert:

- `PROJECT_CONSTITUTION.md`;
- `PROJECT_PRINCIPLES.md`;
- `PROJECT_GLOSSARY.md`;
- `ADR-0001-repository-first-und-documentation-first.md`.

Darauf aufbauende Dokumente sind insbesondere:

- `OBJECT_INTERFACE.md`;
- `OBJECT_SERVICE.md`;
- zukünftige Schema- und Versionsspezifikationen;
- Modelle für Projekte, Identitäten, Konten, Rollen und Berechtigungen;
- domänenspezifische Objektmodelle.

## 29. Offene Architekturentscheidungen

Vor der Freigabe oder in nachfolgenden ADRs sind insbesondere zu klären:

- technische Form und Namensraum der Objektidentität;
- Verhältnis von Objekttyp und Schema;
- Behandlung von Beziehungen als eigene Objekte oder Strukturen;
- Objektversionierung und Konfliktbehandlung;
- Historienmodell;
- Ereignismodell;
- Migrationsstrategie;
- Modellierung von Identitäten und technischen Akteuren.

## 30. Akzeptanzkriterien

Dieses Dokument ist für den Status „Freigegeben“ bereit, wenn:

- der Objektbegriff eindeutig und technologieunabhängig definiert ist;
- Identität und Zustand klar getrennt sind;
- Eigenschaften, Beziehungen, Schema und Lebenszyklus abgegrenzt sind;
- Grundinvarianten vollständig und widerspruchsfrei sind;
- Nicht-Ziele und offene Entscheidungen ausdrücklich benannt sind;
- die Begriffe mit dem Projektglossar übereinstimmen;
- keine Festlegung die spätere Identitätsplattform vorwegnimmt;
- `OBJECT_INTERFACE.md` und `OBJECT_SERVICE.md` darauf aufbauen können.
