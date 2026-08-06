# Objektdienst

**Dokument-ID:** ARC-0003  
**Titel:** Fachlicher Objektdienst  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Architekturmodell  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Zweck

Dieses Dokument definiert die fachlichen Operationen und Garantien für den Umgang mit Objekten.

`OBJECT_MODEL.md` definiert, was ein Objekt ist. `OBJECT_INTERFACE.md` definiert den universellen Vertrag jedes Objekts. Dieses Dokument beschreibt, wie Objekte fachlich erzeugt, geladen, gesucht, geändert, validiert, gespeichert, versioniert, archiviert und referenziert werden.

Es legt keine konkrete Programmiersprache, Datenbank, API, Dateistruktur oder Transporttechnologie fest.

## 2. Geltungsbereich

Der Objektdienst gilt für alle dauerhaft gespeicherten oder systemweit referenzierbaren Objekte.

Domänenspezifische Dienste dürfen zusätzliche Operationen anbieten. Sie müssen die hier festgelegten Garantien jedoch einhalten.

## 3. Verantwortlichkeit

Der Objektdienst ist verantwortlich für:

- die Erzeugung gültiger Objekte;
- die Vergabe oder Entgegennahme einer gültigen Objektidentität;
- das Laden von Objekten anhand stabiler Referenzen;
- die Suche nach Objekten anhand zulässiger Kriterien;
- die Validierung vor einer dauerhaften Änderung;
- die kontrollierte Änderung des Objektzustands;
- die Erhöhung der Objektversion bei fachlich relevanten Änderungen;
- die Erkennung von Versionskonflikten;
- die Pflege von Änderungs- und Historieninformationen;
- die Prüfung von Beziehungen;
- die Archivierung und gegebenenfalls Löschung;
- die Auflösung von Objektreferenzen.

Der Objektdienst definiert keine domänenspezifische Fachlogik, die ausschließlich dem jeweiligen Objekttyp gehört.

## 4. Grundprinzipien

Für alle Operationen gelten folgende Grundsätze:

1. Identität bleibt stabil.
2. Änderungen sind explizit.
3. Ungültige Zustände werden nicht dauerhaft gespeichert.
4. Berechtigungen werden vor schreibenden Operationen geprüft.
5. Versionen werden nicht stillschweigend überschrieben.
6. Fehler werden ausdrücklich gemeldet.
7. Operationen sind nachvollziehbar.
8. Technische Repräsentation und fachliches Objekt bleiben getrennt.

## 5. Erzeugen

Die Erzeugung eines Objekts muss Objekttyp und Schema auflösen, eine eindeutige Identität vergeben oder validieren, Kern- und Fachattribute prüfen, den anfänglichen Lebenszyklusstatus setzen, die erzeugende Identität erfassen, Beziehungen validieren und das vollständige Objekt vor dem Speichern prüfen.

Ein Objekt darf nicht erzeugt werden, wenn die Identität bereits vergeben, der Objekttyp unbekannt, das Schema nicht auflösbar, ein Pflichtattribut nicht vorhanden, eine Beziehung ungültig oder die erzeugende Identität nicht autorisiert ist.

## 6. Laden

Ein Objekt wird anhand einer stabilen Objektreferenz geladen.

Die Ladeoperation muss die Referenz auflösen, die Objektidentität prüfen, den aktuellen fachlichen Zustand sowie Typ, Schema und Objektversion bereitstellen und nicht auflösbare, archivierte oder gelöschte Objekte unterscheidbar behandeln.

Eine Ladeoperation darf nicht stillschweigend ein anderes Objekt zurückgeben.

## 7. Suchen

Die Suche dient dem Auffinden von Objekten anhand fachlicher oder technischer Kriterien, beispielsweise Objekttyp, Domänenverantwortung, Lebenszyklusstatus, Eigentümer, Beziehungen, Fachattribute, Zeiträume, Schemaversion oder Objektversion.

Suchergebnisse müssen stabile Objektreferenzen enthalten. Eine Suche darf keine Berechtigungsgrenzen umgehen oder nicht sichtbare Objekte durch Metadaten offenlegen.

## 8. Ändern

Änderungen erfolgen als ausdrückliche Änderungsanforderung gegen eine bekannte Objektversion.

Vor einer Änderung werden Identität, aktuelle Version, Berechtigung, Attribute, Schema, Lebenszyklusübergang, Beziehungen und domänenspezifische Invarianten geprüft.

Eine Änderung darf die Objektidentität nicht ersetzen. Fachlich relevante Änderungen erhöhen die Objektversion und aktualisieren Änderungszeitpunkt sowie ändernde Identität.

## 9. Validieren

Die Validierung prüft Kernattribute, Fachattribute, Schema, Objekttyp, Lebenszyklusstatus, Beziehungen, Objektinvarianten, domänenspezifische Regeln sowie gegebenenfalls Berechtigungs- und Eigentumsregeln.

Das Ergebnis unterscheidet zwischen gültig, ungültig und nicht vollständig prüfbar. Fehler und Warnungen werden strukturiert und nachvollziehbar zurückgegeben.

## 10. Speichern

Speichern bedeutet die dauerhafte Übernahme eines validierten Objektzustands.

Vor dem Speichern muss sichergestellt sein, dass das Objekt gültig, die erwartete Version aktuell, keine unzulässige parallele Änderung vorhanden, die Berechtigung geprüft und Historie, Audit sowie Beziehungen konsistent sind.

Ein Speichervorgang ist vollständig erfolgreich oder fehlgeschlagen. Ein Teilerfolg darf nicht als vollständiger Erfolg gemeldet werden.

## 11. Versionskonflikte

Konkurrierende Änderungen müssen erkannt werden. Eine Änderung gegen eine veraltete Version darf einen neueren Zustand nicht stillschweigend überschreiben.

Ein Konfliktergebnis enthält mindestens Objektidentität, erwartete Version, aktuelle Version, Konfliktart und mögliche nächste Schritte.

Automatische Zusammenführungen sind nur mit dokumentierten und deterministischen Regeln zulässig.

## 12. Historie

Jede fachlich relevante Änderung muss nachvollziehbar sein. Die Historie enthält soweit anwendbar Objektidentität, alte und neue Version, Zeitpunkt, ändernde Identität oder Prozess, Änderungsart, Begründung oder Bezug sowie betroffene Eigenschaften und Beziehungen.

Die konkrete technische Speicherung bleibt offen.

## 13. Beziehungen

Vor Anlage, Änderung oder Entfernung einer Beziehung werden Existenz der Objekte, Beziehungstyp, Richtung, Geltungsbereich, Kardinalität, Lebenszyklusabhängigkeiten, Berechtigungen und mögliche unzulässige Zyklen geprüft.

Eine Beziehung darf nicht zu einem fachlich ungültigen Gesamtzustand führen.

## 14. Referenzen

Objekte werden über stabile Objektreferenzen adressiert. Anzeigenamen, Dateipfade und Speicherorte sind keine stabilen Referenzen.

Die Referenzauflösung unterscheidet mindestens: gefunden, nicht gefunden, archiviert, gelöscht, Zugriff nicht erlaubt sowie ungültig oder mehrdeutig.

## 15. Archivieren

Archivierung erhält Identität und Historie, beendet jedoch die reguläre aktive Nutzung.

Vor der Archivierung werden Lebenszyklusübergang, Abhängigkeiten, Verantwortlichkeiten, Aufbewahrungspflichten und Berechtigungen geprüft.

## 16. Löschen

Löschen ist von Archivieren zu unterscheiden. Es ist nur zulässig, wenn Lebenszyklus und Objekttyp es erlauben, keine unzulässigen Abhängigkeiten bestehen, fachliche und rechtliche Anforderungen erfüllt, Berechtigungen vorhanden und Auswirkungen dokumentiert sind.

Eine gelöschte Objektidentität darf nicht wiederverwendet werden. Physische, logische oder anonymisierende Löschung wird später festgelegt.

## 17. Berechtigungen

Schreibende und sicherheitsrelevante Operationen erfordern eine ausdrückliche Autorisierungsprüfung.

Der Objektdienst setzt Benutzer, Konto, Rolle und Berechtigung nicht gleich. Er arbeitet mit Identitäten und Berechtigungsentscheidungen. Die konkrete Identitäts- und Autorisierungsarchitektur wird später definiert.

## 18. Fehlerklassen

Der Objektdienst unterscheidet mindestens:

- Objekt nicht gefunden;
- Referenz ungültig;
- Identität bereits vergeben;
- Schema unbekannt;
- Validierung fehlgeschlagen;
- Berechtigung verweigert;
- Versionskonflikt;
- Lebenszyklusübergang unzulässig;
- Beziehung ungültig;
- Abhängigkeit verhindert Operation;
- Speicherung fehlgeschlagen;
- Historien- oder Auditnachweis unvollständig.

Fehler dürfen nicht als erfolgreiche Operation dargestellt werden.

## 19. Transaktionale Grenzen

Fachlich zusammengehörige Änderungen besitzen eine klar definierte atomare Grenze. Innerhalb dieser Grenze werden entweder alle erforderlichen Änderungen übernommen oder keine Änderung als erfolgreich bestätigt.

Die konkrete technische Umsetzung bleibt offen.

## 20. Ereignisse

Erfolgreiche fachlich relevante Operationen können Ereignisse erzeugen. Ein Ereignis nennt mindestens betroffenes Objekt, abgeschlossene Operation, entstandene Objektversion, Zeitpunkt und handelnde Identität oder Prozess.

Ob Ereignisse gespeichert, verteilt oder als Zustandsquelle genutzt werden, ist nicht Bestandteil dieses Dokuments.

## 21. Stapeloperationen

Operationen auf mehreren Objekten definieren ihre Erfolgsgrenze ausdrücklich. Für jedes Objekt muss erkennbar sein, ob die Operation erfolgreich, fehlgeschlagen, nicht ausgeführt oder zurückgesetzt wurde.

Teilerfolge dürfen nicht verborgen werden.

## 22. Offline-Betrieb

Der Objektdienst unterstützt Kernoperationen im Rahmen des Offline-First-Prinzips, soweit keine dokumentierte Online-Abhängigkeit besteht.

Bei späterer Synchronisation müssen Konflikte, Versionen, Identitäten und Historien nachvollziehbar behandelt werden. Die Synchronisationsarchitektur wird separat definiert.

## 23. Beobachtbarkeit und Audit

Wesentliche Operationen müssen nachvollziehbar protokollierbar sein. Sicherheits-, berechtigungs-, identitäts- und datenrelevante Operationen müssen einem Audit zugeführt werden können.

Auditinformationen dürfen nicht unbemerkt durch normale Objektänderungen manipuliert werden.

## 24. Erweiterbarkeit

Domänenspezifische Objektdienste dürfen zusätzliche Validierungen, Suchoperationen, fachliche Kommandos, Lebenszyklusoperationen und Ereignisse definieren.

Sie dürfen Identitätsregeln, Validierung, Versionskonflikte, Berechtigungsprüfungen, Historie, Audit oder Beziehungsregeln nicht umgehen.

## 25. Invarianten des Objektdienstes

Für jede erfolgreiche Operation gelten mindestens:

1. Die Objektidentität bleibt eindeutig und stabil.
2. Der resultierende Zustand ist validiert.
3. Die Objektversion ist konsistent.
4. Die handelnde Identität oder der Prozess ist nachvollziehbar.
5. Berechtigungen wurden geprüft, sofern erforderlich.
6. Beziehungen sind gültig.
7. Fehler oder Teilerfolge wurden nicht verborgen.
8. Ein gemeldeter Erfolg entspricht einem dauerhaft übernommenen fachlichen Ergebnis.

## 26. Offene Architekturentscheidungen

Dieses Dokument legt bewusst nicht fest:

- Format der Objektidentität;
- Persistenztechnologie;
- API-Form;
- Serialisierungsformat;
- Versionierungsverfahren;
- Konfliktauflösung;
- Event Sourcing;
- technische Transaktionen;
- Offline-Synchronisation;
- konkrete Identitäts- und Berechtigungsplattform.

Diese Entscheidungen erfordern eigene Spezifikationen oder ADRs.

## 27. Abhängigkeiten

Dieses Dokument baut auf folgenden Artefakten auf:

- `PROJECT_CONSTITUTION.md`;
- `PROJECT_PRINCIPLES.md`;
- `PROJECT_GLOSSARY.md`;
- `OBJECT_MODEL.md`;
- `OBJECT_INTERFACE.md`.

Bei einem Widerspruch gilt das höherrangige Artefakt.
