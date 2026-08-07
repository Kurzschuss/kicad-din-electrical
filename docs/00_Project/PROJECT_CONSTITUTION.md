# Projektverfassung

**Dokument-ID:** GOV-0001  
**Titel:** Projektverfassung  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** A  
**Autoritätsebene:** Verfassung  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Präambel

Dieses Projekt dient dem Aufbau einer langfristig wartbaren, nachvollziehbaren, erweiterbaren und technisch belastbaren Engineering-Plattform.

Das Projekt besteht nicht ausschließlich aus Quellcode. Es umfasst ebenso Wissen, Modelle, Begriffe, Regeln, Entscheidungen, Spezifikationen, Schnittstellen, Implementierungen, Tests, Simulationen und historische Zusammenhänge.

Alle wesentlichen Bestandteile werden als versionierte, überprüfbare und referenzierbare Projektartefakte behandelt.

Das Projekt soll unabhängig vom Wissen einzelner Personen bestehen können. Seine Ziele, seine Architektur, seine Entscheidungen und seine fachlichen Zusammenhänge müssen allein anhand des Repositorys nachvollziehbar sein.

Langfristige Integrität hat Vorrang vor kurzfristiger Geschwindigkeit. Nachvollziehbarkeit hat Vorrang vor Bequemlichkeit. Explizite Regeln haben Vorrang vor impliziten Annahmen.

## 2. Zweck

Diese Projektverfassung definiert die dauerhaft gültigen Grundsätze des Projekts. Sie bildet die höchste normative Ebene innerhalb des Repositorys.

Alle untergeordneten Dokumente, Modelle, Spezifikationen, Architekturentscheidungen, Implementierungen und Tests müssen mit dieser Verfassung vereinbar sein.

Die Verfassung beschreibt bewusst keine kurzfristigen Maßnahmen, konkreten Technologien oder Implementierungsdetails.

## 3. Geltungsbereich

Diese Verfassung gilt für alle Projektbereiche, Domänen, Modelle, Dienste, Schnittstellen, Dokumente, Implementierungen, Tests, Simulationen, Projektentscheidungen, Mitwirkenden und automatisierten Prozesse.

Sie gilt unabhängig davon, welche Programmiersprachen, Frameworks, Datenbanken, Betriebssysteme, Protokolle oder Werkzeuge verwendet werden.

## 4. Normative Rangordnung

Innerhalb des Projekts gilt folgende Rangordnung:

```text
Projektverfassung
    ↓
Projektprinzipien
    ↓
Architecture Decision Records
    ↓
Architekturmodelle
    ↓
Fachmodelle
    ↓
Spezifikationen
    ↓
Schnittstellen
    ↓
Implementierungen
    ↓
Tests und Nachweise
```

Ein untergeordnetes Artefakt darf einem übergeordneten Artefakt nicht widersprechen. Bei einem Widerspruch gilt das höherrangige Artefakt.

Eine Implementierung gilt als fehlerhaft, wenn sie einem verbindlichen Modell oder einer verbindlichen Spezifikation widerspricht.

## 5. Repository als verbindliche Quelle

Das Repository ist die maßgebliche und verbindliche Wissensquelle des Projekts.

Eine Information gilt erst dann als Bestandteil des Projekts, wenn sie im Repository dokumentiert, eindeutig referenzierbar, versioniert, überprüfbar und mit höherrangigen Regeln vereinbar ist.

Chatverläufe, mündliche Absprachen, persönliche Notizen, nicht versionierte Entwürfe, lokale Dateien außerhalb des Repositorys und nicht dokumentierte Annahmen besitzen keine normative Wirkung.

Solche Quellen dürfen zur Vorbereitung dienen, ersetzen jedoch kein verbindliches Repository-Artefakt.

## 6. Projektsprache

Die maßgebliche Projektsprache ist Deutsch.

Normative Projektdokumente werden grundsätzlich in deutscher Sprache geführt. Englische technische Begriffe dürfen verwendet werden, wenn sie fachlich etabliert, Bestandteil externer Schnittstellen oder zur eindeutigen technischen Zuordnung erforderlich sind.

Wichtige Begriffe müssen projektweit einheitlich verwendet werden. Ergänzende Übersetzungen sind zulässig; sofern nicht ausdrücklich anders festgelegt, bleibt die deutsche Fassung verbindlich.

## 7. Kontrollierte Terminologie

Das Projekt verwendet eine kontrollierte Fachsprache. Jeder zentrale Begriff besitzt genau eine maßgebliche Definition.

Unterschiedliche Begriffe dürfen nicht ohne Begründung für denselben Sachverhalt verwendet werden. Ein Begriff darf nicht in verschiedenen Domänen stillschweigend unterschiedliche Bedeutungen erhalten.

Neue zentrale Begriffe werden im Projektglossar definiert, bevor sie in normativen Dokumenten verwendet werden.

## 8. Single Source of Truth

Für jedes normative Thema existiert genau eine maßgebliche Quelle.

Andere Artefakte dürfen auf diese Quelle verweisen, jedoch keine konkurrierende oder abweichende Definition enthalten.

Normative Inhalte werden nicht unnötig kopiert. Verweise haben Vorrang vor Wiederholungen.

## 9. Dokumentation vor Implementierung

Dokumentation ist Bestandteil der Entwicklung und kein nachgelagerter Arbeitsschritt.

Grundlegende Regeln, Modelle, Verantwortlichkeiten, Schnittstellen und Architekturentscheidungen werden vor oder spätestens gemeinsam mit der Implementierung dokumentiert.

Eine Implementierung darf keine wesentlichen fachlichen Regeln einführen, die ausschließlich im Quellcode existieren.

Fehlt während der Umsetzung eine grundlegende Entscheidung, wird die Umsetzung angehalten, der Entscheidungsbedarf dokumentiert, das zuständige Modell, die Spezifikation oder ein ADR erstellt und geprüft und erst danach die Umsetzung fortgesetzt.

## 10. Architektur vor Implementierung

Die Architektur führt die Implementierung. Die Implementierung erzeugt nicht stillschweigend die Architektur.

Quellcode ist eine technische Umsetzung dokumentierter Modelle und Regeln.

Neue grundlegende Strukturen erfordern vor ihrer dauerhaften Einführung eine fachliche Begründung, eine Beschreibung der Verantwortung, eine Analyse der Auswirkungen und gegebenenfalls ein ADR.

## 11. Modelle vor Technologien

Das Projekt trennt fachliche Konzepte von technischen Darstellungen.

Grundlegende Modelle dürfen nicht unnötig von Programmiersprachen, Frameworks, Datenbanken, Dateiformaten, Protokollen, Cloud-Diensten, Benutzeroberflächen oder Herstellerprodukten abhängen.

Technologien können ausgetauscht werden. Die fachliche Bedeutung muss unabhängig davon verständlich bleiben.

## 12. Objektorientiertes Grundprinzip

Das Projekt verwendet Objekte als grundlegende fachliche Einheiten.

Ein Objekt ist nicht automatisch eine Klasse, Tabellenzeile, Datei, ein JSON-Dokument oder eine Benutzeroberflächenkomponente.

Ein Objekt besitzt eine fachliche Identität. Seine Eigenschaften, Beziehungen, Zustände und technischen Repräsentationen können sich ändern; seine Identität bleibt erhalten, solange das fachliche Objekt fortbesteht.

Die vollständige Definition erfolgt in `OBJECT_MODEL.md`.

## 13. Identität

Jedes dauerhaft gespeicherte oder extern referenzierbare Objekt besitzt eine eindeutige und stabile Identität.

Identität darf nicht ausschließlich von veränderlichen Merkmalen wie Name, Dateipfad, Speicherort, Anzeigename, Eigentümer, aktueller Version oder Benutzeroberflächenbezeichnung abhängen.

Ein Objekt darf verschoben, umbenannt, neu dargestellt oder technisch migriert werden, ohne dadurch seine Identität zu verlieren.

## 14. Beziehungen

Beziehungen zwischen Objekten sind eigenständige fachliche Konzepte und dürfen nicht ausschließlich als technische Referenzen behandelt werden.

Relevante Beziehungen besitzen einen definierten Typ, beteiligte Objekte, eine Richtung oder definierte Symmetrie, einen Geltungsbereich und Validierungsregeln.

Zulässige Beziehungen werden in den zuständigen Modellen definiert.

## 15. Domänenverantwortung

Jedes fachliche Konzept besitzt eine eindeutig zuständige Domäne.

Die zuständige Domäne verantwortet die maßgebliche Definition, das fachliche Modell, Validierungsregeln, Lebenszyklus, Änderungsregeln, Kompatibilität und zugehörige Entscheidungen.

Eine Domäne darf Begriffe oder Regeln einer anderen Domäne nicht stillschweigend neu definieren.

Domänenübergreifende Zusammenarbeit erfolgt über dokumentierte Schnittstellen, Dienste, Ereignisse, Verträge, Beziehungen oder Referenzen.

## 16. Domänenunabhängiger Kern

Der Kern der Plattform bleibt soweit wie möglich unabhängig von einzelnen Anwendungsdomänen.

Neue Domänen sollen auf bestehenden Kernkonzepten aufbauen. Eine Domäne darf projektweite Regeln zu Identität, Versionierung, Validierung, Eigentum, Berechtigungen, Historie, Nachvollziehbarkeit, Dokumentation oder Sicherheit nicht umgehen.

Erfordert eine Domäne eine Änderung des Kerns, muss diese Änderung domänenunabhängig begründet werden.

## 17. Offline-First

Grundlegende Funktionen des Projekts sollen ohne permanente Verbindung zu externen Diensten nutzbar bleiben.

Lokaler Betrieb ist kein nachträglicher Notbetrieb, sondern ein regulärer Betriebsfall.

Externe Dienste dürfen das System erweitern, sollen jedoch nicht ohne dokumentierte Entscheidung zur einzigen maßgeblichen Quelle für grundlegende Projektdaten werden.

Ausnahmen erfordern eine dokumentierte Begründung und gegebenenfalls ein ADR.

## 18. Simulation-First

Verhalten mit wesentlichen Auswirkungen soll vor der realen Ausführung kontrolliert geprüft werden können.

Dies gilt insbesondere bei möglichen Auswirkungen auf Sicherheit, Datenintegrität, reale Geräte, externe Systeme, Berechtigungen, irreversible Zustände, Migrationen oder komplexe Abläufe.

Simulationen sollen soweit möglich dieselben fachlichen Modelle, Regeln und Schnittstellen verwenden wie die reale Ausführung. Abweichungen müssen dokumentiert werden.

## 19. Explizit vor implizit

Wesentliches Verhalten muss ausdrücklich definiert sein und darf nicht ausschließlich von versteckten Standardwerten, nicht dokumentierten Konventionen, zufälligen Ausführungsreihenfolgen, unbeabsichtigten Seiteneffekten oder persönlichen Annahmen abhängen.

Standardwerte müssen dokumentiert, sichtbar, nachvollziehbar und überprüfbar sein.

## 20. Entscheidungen und ADRs

Wesentliche Architekturentscheidungen werden als Architecture Decision Records dokumentiert.

Ein ADR enthält mindestens Kontext, Problemstellung, Randbedingungen, betrachtete Alternativen, Entscheidung, Begründung, Konsequenzen, Risiken und Status.

Ein angenommenes ADR wird nicht gelöscht. Wird eine Entscheidung später ersetzt, bleibt das ursprüngliche ADR erhalten und wird als ersetzt gekennzeichnet.

Ein ADR darf der Projektverfassung nicht widersprechen.

## 21. Nachvollziehbarkeit

Wesentliche Projektänderungen müssen über ihren gesamten Lebenszyklus nachvollziehbar sein.

Soweit anwendbar, soll die Kette von Projektziel über Anforderung, Entscheidung, Modell, Spezifikation, Implementierung, Test oder Simulation bis zu Freigabe und Release erkennbar sein.

Der notwendige Umfang richtet sich nach Risiko, Tragweite, Dauerhaftigkeit, Sicherheitsrelevanz und Anzahl betroffener Komponenten.

## 22. Versionierung

Das Projekt unterscheidet mindestens Repository- oder Release-Version, Dokumentversion, Modellversion, Schemaversion, Schnittstellenversion und Objektrepräsentationsversion.

Diese Versionen erfüllen unterschiedliche Zwecke und dürfen nicht ohne ausdrückliche Definition gleichgesetzt werden.

## 23. Historie

Das Projekt bewahrt die für das Verständnis wesentlicher Änderungen notwendige Historie.

Soweit relevant, muss nachvollziehbar sein, was geändert wurde, wann die Änderung erfolgte, wer oder welcher Prozess sie durchgeführt hat, warum sie notwendig war, welche Entscheidung zugrunde lag und welche Versionen betroffen waren.

## 24. Änderungssteuerung

Änderungen erfolgen bewusst, kontrolliert und nachvollziehbar.

Vor einer wesentlichen Änderung werden Auswirkungen auf Modelle, Schnittstellen, gespeicherte Daten, Identitäten, Beziehungen, Berechtigungen, Sicherheitsgrenzen, Kompatibilität, Dokumentation, Tests, Simulationen und abhängige Domänen geprüft.

Grundlegende Änderungen benötigen ein ADR. Eine Änderung darf keine bestehende Regel stillschweigend aufheben.

## 25. Rückwärtskompatibilität

Kompatibilität ist ein eigenständiges Architekturthema.

Eine Änderung an bestehenden Objekten, Daten, Schnittstellen, Abläufen oder Integrationen muss dokumentieren, welche Bestandteile betroffen sind, ob Daten gültig bleiben, ob eine Migration notwendig ist, wie alte Versionen behandelt werden und ob eine Rückkehr möglich ist.

Ein absichtlicher Kompatibilitätsbruch muss begründet, dokumentiert, geprüft, versioniert und freigegeben werden.

## 26. Sicherheit durch Architektur

Sicherheit wird bereits während Modellierung und Spezifikation berücksichtigt und nicht ausschließlich nachträglich in der Implementierung ergänzt.

Sicherheitsrelevante Verantwortlichkeiten und Vertrauensgrenzen müssen ausdrücklich definiert sein.

Soweit anwendbar gelten minimale Berechtigungen, ausdrückliche Autorisierung, sichere Standardwerte, Trennung von Verantwortlichkeiten, Eingabevalidierung, Schutz sensibler Informationen und nachvollziehbare sicherheitsrelevante Änderungen.

Identitäten, Benutzerkonten, Rollen, Berechtigungen, fachliche Eigentümerschaft und Sitzungen sind getrennte Verantwortungsbereiche und werden ausdrücklich modelliert.

## 27. Fehler und Wiederherstellung

Fehler sind ein regulärer Systemzustand.

Kritische Abläufe müssen erkennbare Fehlerzustände, verständliche Fehlermeldungen, Auswirkungen, Wiederholungs- und Wiederherstellungsverhalten, Rücksetzverhalten und Erwartungen an die Datenintegrität definieren.

Das System darf keinen erfolgreichen Abschluss melden, wenn ein maßgeblicher Vorgang nicht erfolgreich abgeschlossen wurde.

## 28. Qualität

Projektqualität umfasst fachliche Korrektheit, Klarheit, Konsistenz, Wartbarkeit, Verständlichkeit, Testbarkeit, Sicherheit, Erweiterbarkeit, Wiederherstellbarkeit, Beobachtbarkeit, Dokumentationsqualität und architektonische Integrität.

Eine schnelle Umsetzung gilt nicht als qualitativ hochwertig, wenn sie wesentliche Projektprinzipien verletzt.

## 29. Einfachheit

Das Projekt bevorzugt die einfachste Lösung, die dokumentierte Anforderungen erfüllt, die Architektur respektiert und langfristig wartbar bleibt.

Einfachheit bedeutet die Vermeidung unnötiger Abstraktionen, Ausnahmen, Abhängigkeiten, Sonderfälle, Duplikate, versteckter Mechanismen und technischer Komplexität.

Neue Abstraktionen werden nur eingeführt, wenn sie ein konkretes und nachgewiesenes Problem lösen.

## 30. Modularität

Komponenten und Domänen besitzen klar definierte Verantwortlichkeiten und Grenzen.

Ein Modul stellt nur die Schnittstellen bereit, die von anderen Bereichen tatsächlich benötigt werden. Interne Implementierungsdetails dürfen nicht unbeabsichtigt zu öffentlichen Verträgen werden.

Module sollen soweit sinnvoll unabhängig verständlich, testbar, austauschbar und versionierbar sein.

## 31. Kontrollierte Erweiterbarkeit

Das Projekt soll erweitert werden können, ohne den Kern unkontrolliert zu verändern.

Erweiterungen verwenden dokumentierte Schnittstellen, Ereignisse, Dienste, Schemata, Beziehungen, Plugin-Mechanismen oder Verträge.

Eine Erweiterung darf Identitätsregeln, Berechtigungen, Validierung, Eigentumsregeln, Lebenszyklen, Versionsregeln, Sicherheitsregeln oder Nachvollziehbarkeit nicht umgehen.

## 32. Keine versteckten Fachregeln

Fachliche Regeln dürfen nicht ausschließlich in Benutzeroberflächen, Skripten, Datenbanktriggern, Importprozessen, Nachrichtenhandlern, Hintergrunddiensten, Konfigurationsdateien oder einzelnen Codepfaden existieren.

Jede wesentliche Fachregel benötigt eine maßgebliche Spezifikation oder ein zuständiges Modell.

## 33. Trennung der Verantwortlichkeiten

Das Projekt trennt mindestens Governance, Architektur, Fachmodelle, Spezifikationen, Dienste, Infrastruktur, Implementierung, Tests, Simulation und Betriebskonfiguration.

Ein Artefakt soll nicht mehrere voneinander unabhängige Verantwortlichkeiten vermischen. Ist eine Vermischung notwendig, muss sie ausdrücklich begründet werden.

## 34. Menschen- und Maschinenlesbarkeit

Maßgebliche Projektartefakte müssen für Menschen verständlich sein.

Soweit automatisierte Verarbeitung einen nachweisbaren Nutzen bietet, sollen wichtige Strukturen zusätzlich maschinenlesbar dargestellt werden.

Menschenlesbare und maschinenlesbare Darstellungen dürfen sich nicht widersprechen. Es muss festgelegt sein, welche Darstellung im Konfliktfall maßgeblich ist.

## 35. Projektgedächtnis

Das Repository bildet das langfristige Gedächtnis des Projekts.

Zum Projektgedächtnis gehören Ziele, Begriffe, Modelle, Entscheidungen, Begründungen, bekannte Einschränkungen, historische Versionen, Migrationen, Releases, verworfene wesentliche Alternativen sowie relevante fachliche und technische Erkenntnisse.

Temporäre Diskussionen werden in dauerhafte Artefakte überführt, sobald sie das Projekt wesentlich beeinflussen.

## 36. Verantwortung der Mitwirkenden

Jede mitwirkende Person und jeder automatisierte Prozess trägt Verantwortung für die Integrität des Projekts.

Mitwirkende müssen maßgebliche Quellen beachten, Änderungen nachvollziehbar durchführen, betroffene Dokumente aktualisieren, Annahmen offenlegen, bekannte Einschränkungen dokumentieren, erforderliche Tests bereitstellen, verdeckte Abhängigkeiten vermeiden und die Projektsprache und Terminologie einhalten.

## 37. Definition of Done

Eine Änderung gilt erst als abgeschlossen, wenn alle für ihren Umfang erforderlichen Bedingungen erfüllt sind.

Dazu gehören soweit anwendbar: dokumentierter Zweck und Geltungsbereich, getroffene Entscheidungen, aktualisierte Modelle und Spezifikationen, abgeschlossene Implementierung, erfolgreiche Tests oder Simulationen, geprüfte Verweise, aktualisierte Dokumentation, geprüfte Sicherheits- und Kompatibilitätsauswirkungen, beschriebene Migrationen, offengelegte Einschränkungen, durchgeführtes Review und ein logisch zusammengehöriger Commit.

Fertiggestellter Code allein erfüllt die Definition of Done nicht.

## 38. Verfassungsrang

Diese Projektverfassung ist das höchste normative Artefakt des Projekts.

Kein untergeordnetes Dokument darf sie stillschweigend außer Kraft setzen. Ein ADR kann eine Regel konkretisieren, darf der Verfassung jedoch nicht widersprechen.

Widerspricht eine Implementierung oder ein untergeordnetes Dokument der Verfassung, ist das betreffende Artefakt anzupassen.

## 39. Änderung der Projektverfassung

Die Projektverfassung wird bewusst selten geändert.

Eine inhaltliche Änderung erfordert eine dokumentierte Begründung, eine Analyse der Auswirkungen, eine Prüfung betroffener Artefakte, ein ausdrückliches Review, eine ausdrückliche Freigabe, eine Erhöhung der Dokumentversion und einen dauerhaften historischen Nachweis.

Redaktionelle Korrekturen ohne Bedeutungsänderung können nach einem vereinfachten Verfahren erfolgen, das in `DEVELOPMENT_PROCESS.md` festgelegt wird.

## 40. Untergeordnete Dokumente

Die Verfassung wird insbesondere durch folgende Dokumente konkretisiert:

- `PROJECT_PRINCIPLES.md`
- `ARCHITECTURE_VISION.md`
- `DEVELOPMENT_PROCESS.md`
- `OBJECT_MODEL.md`
- `OBJECT_INTERFACE.md`
- `OBJECT_SERVICE.md`
- `PROJECT_MODEL.md`
- `PROJECT_MEMORY.md`
- `PROJECT_BUS.md`
- `USER_MANAGEMENT.md`
- `ROLE_MODEL.md`
- `PERMISSION_MODEL.md`
- `IMPROVEMENT_SYSTEM.md`
- `SIMULATION.md`
- Architecture Decision Records

Die Nennung eines Dokuments bedeutet nicht, dass sein Inhalt bereits beschlossen ist. Jedes Dokument muss einzeln erstellt, geprüft und freigegeben werden.

## 41. Schlussgrundsatz

Das Projekt muss ohne das persönliche Gedächtnis einzelner Beteiligter verständlich bleiben.

Sein Zweck, seine Sprache, seine Modelle, seine Entscheidungen, seine Regeln, seine Implementierungen und seine Geschichte werden deshalb als ausdrückliche, versionierte, überprüfbare und dauerhaft referenzierbare Projektartefakte bewahrt.
