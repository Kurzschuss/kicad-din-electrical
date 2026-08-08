# Projektgedächtnismodell

**Dokument-ID:** PLT-0017  
**Titel:** Fachliches Modell für dauerhaftes Projektwissen und Wissensbeziehungen  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert das Projektgedächtnis von ProjectOS.

Das Projektgedächtnis bewahrt dauerhaft nachvollziehbares Projektwissen über Anforderungen, Entscheidungen, Modelle, Implementierungen, Tests, Releases, Erkenntnisse, Probleme und deren Beziehungen.

Es verhindert, dass entscheidendes Wissen ausschließlich in Chats, einzelnen Dokumenten, persönlichen Notizen oder implizitem Erfahrungswissen verbleibt.

## 2. Grundsatz

Das Projektgedächtnis ist kein Chatarchiv und keine ungeordnete Dokumentenablage.

Es besteht aus expliziten Wissenselementen und typisierten Beziehungen zwischen diesen Elementen.

Beispiel:

```text
Anforderung
   ↓ begründet
Entscheidung
   ↓ prägt
Modell
   ↓ wird umgesetzt durch
Implementierung
   ↓ wird geprüft durch
Test
   ↓ fließt ein in
Release
   ↓ erzeugt
Erkenntnis
```

## 3. Architekturstellung

Das Projektgedächtnis gehört zur Plattformebene.

Es baut insbesondere auf `PROJECT_MODEL.md`, `OBJECT_MODEL.md`, `RELATION_MODEL.md`, `AUDIT_MODEL.md`, `USER_WEIGHT_MODEL.md` und späteren Such- und Busmodellen auf.

Das Projektgedächtnis darf keine konkurrierende Source of Truth für fachliche Objekte erzeugen. Es referenziert maßgebliche Artefakte und hält deren Wissenskontext nachvollziehbar.

## 4. Wissenselement

Ein Wissenselement ist ein dauerhaft referenzierbarer Wissensbaustein.

Es beschreibt mindestens:

- stabile Wissens-ID;
- Wissensart;
- Titel oder Kurzbezeichnung;
- Inhalt oder Zusammenfassung;
- Projektbezug;
- Status;
- Gültigkeits- oder Zeitbezug;
- Herkunft;
- verantwortliche oder beitragende Akteursidentitäten;
- Vertrauens- bzw. Evidenzstatus, soweit relevant;
- Beziehungen zu anderen Wissenselementen oder Projektartefakten;
- Historien- und Auditbezüge.

## 5. Wissensarten

Mindestens sollen folgende Wissensarten unterstützt werden:

- Anforderung;
- Entscheidung;
- Annahme;
- Begründung;
- Architekturprinzip;
- Modellreferenz;
- Implementierungsreferenz;
- Testreferenz;
- Fehler oder Problem;
- Risiko;
- Erkenntnis;
- Erfahrung;
- Verbesserungsvorschlag;
- Review-Ergebnis;
- Freigabe;
- Releasebezug;
- externe Quelle oder Nachweis;
- offene Frage;
- verworfene Alternative.

Weitere Wissensarten dürfen ergänzt werden, sofern sie eindeutig definiert sind.

## 6. Entscheidung als Wissen

Eine Entscheidung muss nachvollziehbar machen können:

- welche Frage entschieden wurde;
- welche Alternativen betrachtet wurden;
- welche Alternative gewählt wurde;
- warum sie gewählt wurde;
- wer beteiligt war;
- welcher Gültigkeitsbereich betroffen ist;
- welche Artefakte oder Modelle daraus folgen;
- welche Annahmen zugrunde lagen;
- ob und wann die Entscheidung ersetzt wurde.

ADRs sind eine mögliche Darstellungsform einer Entscheidung, aber nicht die einzige Form von Projektwissen.

## 7. Anforderungen

Anforderungen können als Wissenselemente geführt oder auf maßgebliche Anforderungsartefakte referenziert werden.

Sie müssen mit ihren Umsetzungen und Nachweisen verknüpfbar sein.

Mindestens sollen Beziehungen möglich sein wie:

- Anforderung wird erfüllt durch Modell;
- Anforderung wird umgesetzt durch Implementierung;
- Anforderung wird geprüft durch Test;
- Anforderung wird beeinflusst durch Entscheidung;
- Anforderung wird ersetzt durch neue Anforderung.

## 8. Erkenntnisse

Erkenntnisse dokumentieren dauerhaft relevantes Wissen, das während Entwicklung, Test, Betrieb oder Review entsteht.

Beispiele:

- Fehlerursache;
- unerwartete Wechselwirkung;
- bestätigte Annahme;
- widerlegte Annahme;
- Designregel;
- wiederkehrendes Problem;
- Optimierung;
- fachlicher Grenzfall.

Eine Erkenntnis soll auf ihre Evidenz und ihren Entstehungskontext verweisen können.

## 9. Wissensbeziehungen

Wissensbeziehungen sind typisiert.

Beispiele sind:

- begründet;
- widerspricht;
- bestätigt;
- widerlegt;
- ersetzt;
- ergänzt;
- hängt ab von;
- umgesetzt durch;
- geprüft durch;
- verursacht;
- betrifft;
- abgeleitet aus;
- dokumentiert in;
- veröffentlicht in;
- gelernt aus.

Unstrukturierte Freitextverweise sollen nicht die einzige Form wichtiger Beziehungen sein.

## 10. Wissen und Artefakte

Das Projektgedächtnis darf auf konkrete Artefakte referenzieren, beispielsweise:

- Markdown-Dokumente;
- ADRs;
- Quellcodedateien;
- Tests;
- KiCad-Artefakte;
- Simulationen;
- Releases;
- Issues;
- Pull Requests;
- externe Normen oder Dokumente.

Das Artefakt bleibt dort autoritativ, wo es seine fachliche oder technische Verantwortung besitzt.

Das Projektgedächtnis hält den Zusammenhang und die Bedeutung fest.

## 11. Wissen und Chat

Chatverläufe können Quellen für neue Wissenselemente sein.

Ein Chat selbst wird jedoch nicht automatisch zur maßgeblichen Wissensquelle.

Dauerhaft relevante Inhalte müssen in explizite Projektartefakte oder Wissenselemente überführt werden.

Dadurch wird vermieden, dass Entscheidungen nur deshalb gültig bleiben, weil sie irgendwann in einem Chat erwähnt wurden.

## 12. Herkunft und Provenienz

Jedes relevante Wissenselement muss seine Herkunft nachvollziehbar machen können.

Mögliche Herkunft sind:

- Benutzerbeitrag;
- ADR;
- Dokument;
- Commit;
- Pull Request;
- Issue;
- Testlauf;
- Simulation;
- Review;
- externe Quelle;
- importiertes Altsystem;
- automatisch abgeleitete Erkenntnis.

Automatisch erzeugtes Wissen muss als solches erkennbar bleiben.

## 13. Evidenz

Wissenselemente können Evidenz referenzieren.

Dabei kann unterschieden werden zwischen:

- Behauptung;
- plausibler Annahme;
- geprüft;
- experimentell bestätigt;
- durch Test bestätigt;
- fachlich reviewed;
- freigegeben;
- widerlegt;
- veraltet.

Ein Evidenzstatus ist keine Berechtigung und ersetzt keine formale Freigabe.

## 14. Unsicherheit

ProjectOS soll unsicheres Wissen explizit darstellen können.

Offene Fragen, Annahmen und Hypothesen dürfen nicht so gespeichert werden, als wären sie bestätigte Tatsachen.

Unsicherheit kann insbesondere beschrieben werden durch:

- Status;
- Evidenzgrad;
- offene Gegenargumente;
- fehlende Nachweise;
- Ablauf- oder Reviewbedarf.

## 15. Widersprüche

Widersprüchliche Wissenselemente dürfen nicht stillschweigend zusammengeführt werden.

Wenn zwei Aussagen nicht gleichzeitig gelten können, muss der Konflikt sichtbar bleiben, bis er aufgelöst wurde.

Eine spätere Entscheidung kann einen Widerspruch auflösen, darf ältere Wissensstände aber nicht unsichtbar umschreiben.

## 16. Ersetzung und Veraltung

Wissen kann ersetzt oder veraltet werden.

Dabei gilt:

- alte Wissenselemente bleiben historisch nachvollziehbar;
- ein Nachfolger kann ausdrücklich referenziert werden;
- aktuelle und historische Gültigkeit bleiben unterscheidbar;
- Such- und Cockpitansichten dürfen aktuelle Inhalte bevorzugen, historische Inhalte aber nicht verlieren.

## 17. Benutzergewichtung

Die Benutzergewichtung aus `USER_WEIGHT_MODEL.md` kann bei der Einordnung von Beiträgen, Reviews und Verbesserungsvorschlägen verwendet werden.

Sie darf jedoch niemals allein bestimmen, ob ein Wissenselement wahr oder gültig ist.

Ein hoher Kompetenzwert kann fachliche Relevanz erhöhen, ersetzt aber keine Evidenz, keine formale Freigabe und keine nachvollziehbare Begründung.

## 18. Improvement-System

Das Improvement-System soll eng mit dem Projektgedächtnis verbunden werden.

Ein Verbesserungsvorschlag kann insbesondere verknüpft werden mit:

- erkanntem Problem;
- betroffenen Anforderungen;
- bestehenden Entscheidungen;
- Dubletten;
- Benutzergewichtungen;
- Reviews;
- angenommener Lösung;
- Umsetzung;
- Test;
- Release;
- späterer Erkenntnis über Wirkung oder Regression.

Dadurch bleibt nachvollziehbar, was aus einem Verbesserungsvorschlag tatsächlich geworden ist.

## 19. Dubletten

Dubletten im Wissensbestand sollen erkennbar und referenzierbar sein.

Eine Dublette wird nicht zwingend gelöscht.

Stattdessen kann sie:

- auf das führende Wissenselement verweisen;
- zusätzliche Evidenz beitragen;
- einen abweichenden Kontext dokumentieren;
- als tatsächlich unabhängige Bestätigung erhalten bleiben.

## 20. Projektübergreifendes Wissen

Einige Wissenselemente können über ein einzelnes Projekt hinaus relevant sein.

Dafür muss unterschieden werden zwischen:

- projektspezifischem Wissen;
- organisationsbezogenem Wissen;
- domänenbezogenem Wissen;
- plattformweitem Wissen.

Eine Übernahme in einen weiteren Gültigkeitsbereich muss explizit erfolgen und darf nicht automatisch aus einem Einzelprojekt abgeleitet werden.

## 21. Zugriff und Sichtbarkeit

Wissenselemente unterliegen der Autorisierung.

Sichtbarkeit kann unter anderem abhängen von:

- Projekt;
- Organisation;
- Domäne;
- Vertraulichkeit;
- Rolle;
- konkreter Berechtigung;
- Datenschutzanforderungen.

Suche darf keine Informationen offenlegen, die ein Benutzer nicht sehen darf.

## 22. Audit

Audit und Projektgedächtnis sind getrennte Konzepte.

Audit dokumentiert nachweisrelevante Vorgänge.

Das Projektgedächtnis dokumentiert fachliches Wissen und Zusammenhänge.

Ein Wissenselement kann Auditnachweise referenzieren, und Audit kann auf Wissenselemente verweisen.

Änderungen an besonders relevanten Entscheidungen, Freigaben oder Evidenzstatus können auditpflichtig sein.

## 23. Offline-First

Projektwissen muss im vorgesehenen lokalen Betriebsumfang offline verfügbar sein können.

Dabei muss erkennbar bleiben:

- welcher Wissensstand lokal vorliegt;
- wann er zuletzt synchronisiert wurde;
- welche externen Quellen fehlen;
- ob ein Element möglicherweise veraltet ist;
- welche Konflikte bei Wiederverbindung bestehen.

## 24. Synchronisation

Synchronisation des Projektgedächtnisses darf Wissenskonflikte nicht stillschweigend überschreiben.

Konflikte können insbesondere entstehen bei:

- parallelen Entscheidungen;
- unterschiedlich aktualisierten Wissenselementen;
- geänderten Beziehungen;
- widersprüchlichen Evidenzständen;
- offline erzeugten Erkenntnissen.

Solche Konflikte müssen sichtbar und auflösbar bleiben.

## 25. Suche

Das Projektgedächtnis muss durchsuchbar sein.

Mindestens vorgesehen sind Suchen nach:

- Wissens-ID;
- Wissensart;
- Projekt;
- Domäne;
- Status;
- Verantwortlichem;
- Quelle;
- Entscheidung;
- Anforderung;
- betroffenem Objekt;
- Beziehung;
- Zeitraum;
- Evidenzstatus;
- Volltext;
- Tags, soweit verwendet.

Das konkrete Suchmodell wird später in `SEARCH_MODEL.md` definiert.

## 26. Z_Cockpit

Z_Cockpit soll das Projektgedächtnis als nachvollziehbaren Wissensgraphen und als gefilterte Arbeitsansichten darstellen können.

Vorgesehen sind insbesondere:

- wichtige aktuelle Entscheidungen;
- offene Fragen;
- Annahmen ohne ausreichende Evidenz;
- widersprüchliche Aussagen;
- relevante Erkenntnisse;
- betroffene Anforderungen;
- Umsetzung und Tests;
- Releasebezüge;
- Improvement-Verlauf;
- Quellen und Provenienz;
- historische Vorgänger und Nachfolger.

Das Cockpit ist nicht die Source of Truth für Projektwissen.

## 27. Wissenspfad

Eine zentrale Funktion soll die Nachverfolgung vollständiger Wissenspfade ermöglichen.

Beispiel:

```text
Warum wurde diese Implementierung so gebaut?

Implementierung
   ← umgesetzt aus Entscheidung ADR-0042
   ← Entscheidung löst Anforderung REQ-128
   ← Anforderung entstand aus Fehler BUG-31
   ← Fehler wurde in Test TEST-778 bestätigt
```

Ebenso soll die Gegenrichtung möglich sein:

```text
Was wurde aus dieser Entscheidung?

Entscheidung
   → Modell
   → Implementierung
   → Test
   → Release
```

## 28. Wissenslücken

ProjectOS soll Wissenslücken erkennen können.

Beispiele:

- Entscheidung ohne Begründung;
- Anforderung ohne Umsetzung;
- Implementierung ohne nachvollziehbare Anforderung;
- kritische Änderung ohne Test;
- Erkenntnis ohne Quelle;
- veraltete Entscheidung ohne Nachfolger;
- Improvement ohne Abschlussbezug.

Wissenslücken sind Hinweise und nicht automatisch Fehler.

## 29. Automatische Ableitungen

ProjectOS darf abgeleitete Wissenshinweise erzeugen, beispielsweise:

- möglicher Widerspruch;
- mögliche Dublette;
- fehlender Testbezug;
- veraltete Quelle;
- nicht mehr auflösbare Referenz;
- wiederkehrendes Fehlermuster.

Automatisch abgeleitete Hinweise müssen als abgeleitet gekennzeichnet sein und dürfen nicht ohne Bestätigung als freigegebene Entscheidung erscheinen.

## 30. Validierung

Ein Wissenselement ist mindestens darauf zu prüfen, dass:

1. eine eindeutige Wissens-ID vorhanden ist;
2. Wissensart bekannt ist;
3. Projekt- oder sonstiger Gültigkeitsbereich zulässig ist;
4. Herkunft nachvollziehbar ist;
5. Status und Evidenzstatus konsistent sind;
6. referenzierte Beziehungen gültige Typen verwenden;
7. aktuelle und historische Gültigkeit unterscheidbar bleiben;
8. automatische Ableitungen als solche gekennzeichnet sind;
9. Berechtigungs- und Datenschutzgrenzen eingehalten werden;
10. widersprüchliche Inhalte nicht stillschweigend überschrieben werden.

## 31. Invarianten

1. Das Projektgedächtnis ist kein Chatarchiv.
2. Das Projektgedächtnis ist keine zweite Source of Truth für fachliche Objekte.
3. Dauerhaft relevantes Wissen wird explizit modelliert oder referenziert.
4. Wissen besitzt nachvollziehbare Herkunft.
5. Unsicherheit bleibt sichtbar.
6. Widersprüche werden nicht stillschweigend überschrieben.
7. Historische Wissensstände bleiben nachvollziehbar.
8. Benutzergewichtung ersetzt keine Evidenz.
9. Audit und Projektgedächtnis bleiben getrennt.
10. Automatische Ableitungen werden als solche gekennzeichnet.
11. Z_Cockpit ist nicht die Source of Truth.
12. Offline-Konflikte werden nicht stillschweigend überschrieben.
13. Projektübergreifende Verallgemeinerung erfolgt nicht automatisch.
14. Suche respektiert Autorisierung und Datenschutz.
15. Wissensbeziehungen sind soweit relevant typisiert und nachvollziehbar.

## 32. Abgrenzung

Dieses Dokument definiert nicht:

- konkrete Datenbank- oder Graphdatenbanktechnologie;
- konkreten Suchindex;
- konkrete Embedding- oder KI-Technologie;
- konkrete Chat-Speicherung;
- vollständige Dokumentenverwaltung;
- technische Busprotokolle;
- konkrete GUI-Layouts;
- konkrete automatische Wahrheitsbewertung.

## 33. Folgemodelle

Auf diesem Modell bauen insbesondere auf:

- `BUS_MODEL.md`;
- `SEARCH_MODEL.md`;
- `CONFIGURATION_MODEL.md`;
- `IMPROVEMENT_SYSTEM.md`;
- spätere Wissensdienste;
- Z_Cockpit-Wissensansichten;
- Dokumentations- und Release-Nachverfolgung.

## 34. Abhängigkeiten

Dieses Dokument basiert insbesondere auf:

- `PLATFORM_MODEL.md`;
- `PROJECT_MODEL.md`;
- `WORKSPACE_MODEL.md`;
- `IDENTITY_MODEL.md`;
- `USER_WEIGHT_MODEL.md`;
- `AUTHORIZATION_MODEL.md`;
- `AUDIT_MODEL.md`;
- `RELATION_MODEL.md`;
- `Z_COCKPIT_IDENTITY_INTEGRATION.md`.

## 35. Ergebnis

ProjectOS besitzt ein eigenständiges Projektgedächtnismodell, das Anforderungen, Entscheidungen, Modelle, Implementierungen, Tests, Releases, Erkenntnisse und Verbesserungsvorschläge über typisierte Wissensbeziehungen nachvollziehbar verbindet.

Dauerhaft relevantes Wissen wird damit aus flüchtigen Chats und implizitem Kontext in referenzierbare Projektartefakte überführt, ohne bestehende fachliche Sources of Truth zu duplizieren.