# Beziehungsmodell

**Dokument-ID:** ARC-0006  
**Titel:** Grundlegendes Beziehungsmodell  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Architekturmodell  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Zweck

Dieses Dokument definiert den fachlichen Begriff „Beziehung“ innerhalb des Kernels.

Eine Beziehung beschreibt eine typisierte, fachlich bedeutsame Verbindung zwischen Objekten. Sie ist mehr als ein technischer Fremdschlüssel oder eine zufällige Referenz.

Das Dokument legt keine konkrete Datenbankstruktur, Graphtechnologie, Serialisierung oder API fest.

## 2. Geltungsbereich

Das Beziehungsmodell gilt für alle Verbindungen, die mindestens eine der folgenden Eigenschaften besitzen:

- sie tragen fachliche Bedeutung;
- sie müssen validiert werden;
- sie beeinflussen Lebenszyklen oder Berechtigungen;
- sie besitzen eigene Eigenschaften;
- sie müssen historisiert oder versioniert werden;
- sie werden von mehreren Komponenten oder Domänen verwendet;
- ihre Existenz oder Auflösung muss nachvollziehbar sein.

Rein technische Hilfsreferenzen ohne fachliche Bedeutung sind nicht automatisch Beziehungen im Sinne dieses Modells.

## 3. Definition

Eine Beziehung ist eine identifizierbare, typisierte und validierbare Verbindung zwischen mindestens zwei referenzierbaren Objekten oder anderen ausdrücklich zugelassenen Endpunkten.

Sie beschreibt mindestens:

- welcher Beziehungstyp gilt;
- welches Element Quelle ist;
- welches Element Ziel ist;
- ob die Beziehung gerichtet oder symmetrisch ist;
- in welchem Zustand sie sich befindet;
- nach welchen Regeln sie gültig ist.

## 4. Beziehung als Objekt

Eine fachlich relevante Beziehung wird als dauerhaft identifizierbares Objekt modelliert, wenn sie einen eigenen Lebenszyklus, eigene Eigenschaften, Versionierung, Historie oder Berechtigungsregeln benötigt.

Eine solche Beziehung besitzt mindestens:

- stabile Objektidentität;
- Beziehungstyp;
- Quellreferenz;
- Zielreferenz;
- Schema und Schemaversion;
- Objektversion;
- Lebenszyklusstatus;
- Domänenverantwortung;
- Erzeugungs- und Änderungsinformationen.

Einfache abgeleitete Beziehungen dürfen ohne eigenes persistentes Beziehungsobjekt dargestellt werden, sofern ihre Bedeutung vollständig aus einer maßgeblichen Quelle reproduzierbar ist.

## 5. Beziehungstyp

Jede Beziehung besitzt genau einen fachlichen Beziehungstyp.

Der Beziehungstyp definiert mindestens:

- fachliche Bedeutung;
- erlaubte Quelltypen;
- erlaubte Zieltypen;
- Richtung oder Symmetrie;
- Kardinalitäten;
- zulässige Eigenschaften;
- Lebenszyklusregeln;
- Validierungsregeln;
- Auswirkungen auf Archivierung und Löschung.

Beispiele für Beziehungstypen sind:

- gehört zu;
- enthält;
- verwendet;
- referenziert;
- ersetzt;
- basiert auf;
- ist abhängig von;
- wird simuliert durch;
- ist Eigentum von;
- ist verantwortlich für.

Konkrete Beziehungstypen werden durch zuständige Plattform- oder Domänenmodelle definiert.

## 6. Quelle und Ziel

Eine gerichtete Beziehung besitzt genau eine Quelle und genau ein Ziel, sofern ihr Typ keine mehrstellige Beziehung vorsieht.

Quelle und Ziel werden durch stabile Referenzen identifiziert.

Eine Beziehung darf nicht allein aufgrund gleichlautender Namen, Pfade oder technischer Speicherorte aufgelöst werden.

## 7. Gerichtete und symmetrische Beziehungen

Eine gerichtete Beziehung unterscheidet Quelle und Ziel.

Beispiel:

```text
Projekt enthält Artefakt
```

Eine symmetrische Beziehung behandelt beide Endpunkte fachlich gleichwertig.

Beispiel:

```text
Objekt A ist äquivalent zu Objekt B
```

Die Symmetrie muss durch den Beziehungstyp ausdrücklich festgelegt sein. Sie darf nicht aus einer technischen Darstellung abgeleitet werden.

## 8. Inverse Beziehungen

Ein Beziehungstyp kann eine ausdrückliche inverse Sicht besitzen.

Beispiel:

```text
Projekt enthält Artefakt
Artefakt gehört zu Projekt
```

Es muss festgelegt sein, ob die inverse Beziehung:

- nur eine abgeleitete Lesesicht ist;
- als eigenes Beziehungsobjekt gespeichert wird;
- eigene Eigenschaften oder einen eigenen Lebenszyklus besitzt.

Abgeleitete inverse Beziehungen dürfen nicht unabhängig geändert werden.

## 9. Mehrstellige Beziehungen

Beziehungen mit mehr als zwei fachlich gleichwertigen Beteiligten sind zulässig, wenn eine binäre Zerlegung die Bedeutung verfälschen würde.

Eine mehrstellige Beziehung muss:

- alle Rollen der Beteiligten eindeutig benennen;
- ihre Kardinalitäten definieren;
- vollständig validierbar sein;
- eine eindeutige fachliche Bedeutung besitzen.

Wo möglich, werden Beziehungen binär modelliert, um Verständlichkeit und Prüfbarkeit zu erhalten.

## 10. Kardinalität

Der Beziehungstyp legt zulässige Kardinalitäten fest.

Mindestens zu unterscheiden sind:

- genau eins;
- null oder eins;
- mindestens eins;
- beliebig viele;
- begrenzte Anzahl;
- genau definierte Anzahl.

Kardinalitäten können für Quelle und Ziel unterschiedlich sein.

Eine Kardinalitätsverletzung macht die Beziehung oder den betroffenen Gesamtzustand ungültig.

## 11. Beziehungseigenschaften

Eine Beziehung kann eigene Eigenschaften besitzen.

Beispiele:

- Rolle eines Beteiligten;
- Priorität;
- Reihenfolge;
- Gewichtung;
- Herkunft;
- Gültigkeitszeitraum;
- Begründung;
- Freigabestatus;
- Kommentar;
- Vertrauensgrad.

Beziehungseigenschaften werden durch das zuständige Beziehungsschema definiert und dürfen keine Kerninformationen der Endpunkte duplizieren.

## 12. Gültigkeitszeitraum

Eine Beziehung kann zeitlich begrenzt sein.

Sie kann mindestens besitzen:

- gültig ab;
- gültig bis;
- Aktivierungszeitpunkt;
- Beendigungszeitpunkt;
- Beendigungsgrund.

Historische Gültigkeit und aktueller Status müssen unterscheidbar bleiben.

## 13. Lebenszyklus

Eine Beziehung besitzt einen ausdrücklich definierten Lebenszyklus, wenn ihre Existenz nicht rein abgeleitet ist.

Mögliche Zustände sind:

- Entwurf;
- beantragt;
- aktiv;
- gesperrt;
- beendet;
- veraltet;
- archiviert;
- gelöscht.

Der konkrete Zustandsvorrat wird durch den Beziehungstyp oder sein Schema festgelegt.

Statusübergänge müssen validierbar und nachvollziehbar sein.

## 14. Erzeugung

Vor dem Erzeugen einer Beziehung werden mindestens geprüft:

- Quell- und Zielreferenz sind auflösbar;
- Beziehungstyp ist bekannt;
- Quell- und Zieltypen sind zulässig;
- Kardinalitäten werden eingehalten;
- Pflichtbeziehungen und Ausschlussregeln werden beachtet;
- erforderliche Berechtigungen liegen vor;
- kein unzulässiger Zyklus entsteht;
- Lebenszyklusregeln der beteiligten Objekte erlauben die Beziehung.

Eine ungültige Beziehung darf nicht als erfolgreich erzeugt gemeldet werden.

## 15. Änderung

Änderungen an Beziehungstyp, Quelle oder Ziel sind keine gewöhnlichen Eigenschaftsänderungen.

Sie erfordern eine ausdrückliche Transformationsregel oder werden als Beendigung der bisherigen und Erzeugung einer neuen Beziehung behandelt.

Fachlich relevante Änderungen erhöhen die Beziehungsversion und werden historisiert.

## 16. Beendigung und Entfernung

Das Beenden einer Beziehung ist von ihrer physischen Löschung zu unterscheiden.

Eine Beziehung kann fachlich beendet, aber aus Gründen der Historie, Auditierbarkeit oder Nachvollziehbarkeit weiterhin gespeichert bleiben.

Vor Entfernung werden mindestens geprüft:

- Pflichtbeziehungen;
- abhängige Objekte oder Beziehungen;
- Lebenszyklusregeln;
- Berechtigungen;
- Archivierungs- und Auditpflichten;
- Auswirkungen auf abgeleitete Beziehungen.

## 17. Zyklen

Zyklische Beziehungen sind nur zulässig, wenn der Beziehungstyp oder das zuständige Modell sie ausdrücklich erlaubt.

Unzulässige Zyklen müssen vor Speicherung erkannt werden.

Beispiele möglicher Verbote:

- ein Objekt darf nicht direkt oder indirekt sich selbst enthalten;
- eine Versionsableitung darf keinen Kreis bilden;
- eine hierarchische Eigentumsstruktur darf keinen Zyklus enthalten.

Nicht jede zyklische Struktur ist grundsätzlich fehlerhaft. Die Zulässigkeit ist fachlich zu definieren.

## 18. Komposition und Aggregation

Beziehungen können unterschiedliche Stärke besitzen.

### 18.1 Komposition

Der Lebenszyklus eines enthaltenen Elements ist wesentlich an den Container gebunden.

### 18.2 Aggregation

Ein Element gehört fachlich zu einer Sammlung, kann aber unabhängig fortbestehen.

Die konkrete Bedeutung und das Verhalten bei Archivierung oder Löschung müssen durch den Beziehungstyp festgelegt werden.

## 19. Eigentum und Verantwortung

Eigentum, Verantwortung, Mitgliedschaft und Berechtigung sind unterschiedliche Beziehungstypen.

Sie dürfen nicht stillschweigend gleichgesetzt werden.

Eine Eigentumsbeziehung erzeugt nicht automatisch uneingeschränkte technische Berechtigung, sofern dies nicht ausdrücklich im Autorisierungsmodell festgelegt ist.

## 20. Ableitungen

Eine Beziehung kann aus anderen maßgeblichen Daten abgeleitet werden.

Eine abgeleitete Beziehung muss:

- reproduzierbar sein;
- ihre Quelle benennen;
- als abgeleitet erkennbar sein;
- nicht unabhängig geändert werden;
- bei Änderung ihrer Grundlage aktualisiert oder ungültig werden.

Abgeleitete Beziehungen sind nicht automatisch historisch autoritativ.

## 21. Beziehungsschema

Jeder persistente Beziehungstyp verweist auf ein Schema.

Das Schema definiert mindestens:

- Beziehungstyp;
- Quell- und Zieltypen;
- Richtung;
- Kardinalitäten;
- Eigenschaften;
- Pflichtangaben;
- Lebenszykluszustände;
- Validierungsregeln;
- Kompatibilitäts- und Migrationsregeln.

`SCHEMA_MODEL.md` ist für die allgemeinen Schemaregeln maßgeblich.

## 22. Versionierung

Eine persistente Beziehung besitzt eine eigene Objektversion.

Die Beziehungsversion ist unabhängig von den Versionen der beteiligten Objekte.

Änderungen der Endpunkte führen nicht automatisch zu einer neuen Beziehungsversion, solange die Beziehung selbst fachlich unverändert bleibt.

Eine veröffentlichte historische Beziehungsversion darf nicht rückwirkend in ihrer Bedeutung verändert werden.

## 23. Historie

Für fachlich relevante Beziehungen muss nachvollziehbar sein:

- wann sie erzeugt wurde;
- durch welche Identität oder welchen Prozess;
- welche Versionen existierten;
- welche Eigenschaften geändert wurden;
- wann und warum sie beendet wurde;
- welche Endpunkte betroffen waren;
- welche Entscheidung oder Anforderung zugrunde lag.

Die technische Form der Historie bleibt offen.

## 24. Validierung

Die Validierung einer Beziehung umfasst mindestens:

- gültige Identität;
- bekannten Beziehungstyp;
- auflösbare Endpunkte;
- zulässige Endpunkttypen;
- gültige Richtung;
- eingehaltene Kardinalitäten;
- gültige Eigenschaften;
- zulässigen Lebenszyklusstatus;
- eingehaltene Ausschluss- und Zyklusregeln;
- gültige Berechtigungs- und Verantwortungsregeln;
- konsistente Version und Historie.

Validierungsfehler dürfen nicht stillschweigend ignoriert werden.

## 25. Berechtigungen

Lesen, Erzeugen, Ändern und Beenden einer Beziehung können unterschiedliche Berechtigungen erfordern.

Die Berechtigungsentscheidung kann abhängen von:

- Beziehungstyp;
- Quellobjekt;
- Zielobjekt;
- Geltungsbereich;
- handelnder Identität;
- Eigentum oder Verantwortung;
- Lebenszyklusstatus;
- Projekt- oder Organisationskontext.

Die konkrete Autorisierung wird durch Plattformmodelle festgelegt.

## 26. Domänenverantwortung

Jeder Beziehungstyp besitzt genau eine fachlich zuständige Domäne.

Diese verantwortet:

- Bedeutung;
- Endpunkttypen;
- Kardinalitäten;
- Eigenschaften;
- Lebenszyklus;
- Validierung;
- Kompatibilität;
- Migration.

Andere Domänen dürfen den Beziehungstyp verwenden, aber nicht stillschweigend verändern.

## 27. Beziehungsinvarianten

Für jede persistente Beziehung gelten mindestens folgende Invarianten:

1. Sie besitzt eine stabile Identität.
2. Sie besitzt genau einen Beziehungstyp.
3. Ihre Endpunkte sind eindeutig referenziert.
4. Richtung oder Symmetrie sind ausdrücklich definiert.
5. Endpunkttypen und Kardinalitäten sind zulässig.
6. Ihre Eigenschaften entsprechen dem gültigen Schema.
7. Ihr Lebenszyklusstatus ist zulässig.
8. Unzulässige Zyklen werden verhindert.
9. Eine abgeleitete Beziehung wird nicht unabhängig verändert.
10. Eine beendete Beziehung bleibt historisch nachvollziehbar, sofern Aufbewahrungspflichten bestehen.
11. Eine Beziehung ersetzt keine fachliche Eigenschaft, wenn keine eigenständige Verbindung vorliegt.
12. Ungültige Beziehungen dürfen nicht als erfolgreich gespeichert oder freigegeben gemeldet werden.

## 28. Nicht festgelegt

Dieses Dokument legt noch nicht fest:

- Graphdatenbank oder relationale Speicherung;
- Fremdschlüsselstrukturen;
- konkrete API-Endpunkte;
- konkrete technische Feldnamen;
- konkrete Beziehungstypen der Plattform oder Fachdomänen;
- technische Indexierung;
- konkrete Konsistenzverfahren verteilter Systeme;
- Serialisierungsformate.

## 29. Abhängigkeiten

Dieses Dokument konkretisiert:

- `CORE_MODEL.md`;
- `OBJECT_MODEL.md`;
- `OBJECT_INTERFACE.md`;
- `OBJECT_SERVICE.md`;
- `SCHEMA_MODEL.md`.

Nachgeordnete Plattform- und Domänenmodelle definieren konkrete Beziehungstypen auf dieser Grundlage.

## 30. Ergebnis

Beziehungen sind eigenständige fachliche Konzepte.

Sie werden typisiert, validiert, versioniert und historisiert, wenn ihre Bedeutung dies erfordert. Technische Referenzen allein begründen noch keine fachliche Beziehung.
