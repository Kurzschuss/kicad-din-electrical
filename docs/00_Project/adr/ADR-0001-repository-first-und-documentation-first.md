# ADR-0001: Repository-First und Documentation-First

**Dokument-ID:** ADR-0001  
**Titel:** Repository-First und Documentation-First als verbindliche Arbeitsweise  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** A  
**Entscheidungsart:** Grundlegende Projektentscheidung  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Kontext

Während der ersten Projektphase wurden Vision, Grundprinzipien, Architekturideen und mögliche Systembestandteile überwiegend in Gesprächen und Chatverläufen entwickelt.

Diese Arbeitsweise war für die Ideenfindung geeignet. Mit zunehmendem Projektumfang entstehen jedoch Risiken:

- Wichtige Entscheidungen können ausschließlich in Chatverläufen enthalten sein.
- Zusammenhänge sind später nur schwer auffindbar.
- Begriffe können unterschiedlich verwendet werden.
- Neue Entscheidungen können älteren Entscheidungen widersprechen.
- Der tatsächliche und freigegebene Projektstand ist nicht eindeutig erkennbar.
- Diskutierte Ideen können irrtümlich als verbindliche Architektur angesehen werden.

Das Projekt benötigt deshalb einen klaren Übergang von einer diskussionsgetriebenen zu einer artefaktgetriebenen Arbeitsweise.

## 2. Problemstellung

Das Projekt benötigt eine verbindliche Regelung für folgende Fragen:

- Wo befindet sich der maßgebliche Projektstand?
- Wann gilt eine Entscheidung als verbindlich?
- Welche Bedeutung besitzen Chatverläufe?
- Wann darf mit einer Implementierung begonnen werden?
- Wie werden Entscheidungen nachvollziehbar festgehalten?
- Wie wird verhindert, dass Architektur nur implizit im Quellcode entsteht?
- Wie wird Projektwissen langfristig erhalten?

Ohne eine solche Regelung können Chat, Dokumentation, Implementierung und persönliche Annahmen voneinander abweichen.

## 3. Entscheidung

Das Projekt führt die Prinzipien **Repository-First** und **Documentation-First** als verbindliche Arbeitsweise ein.

### 3.1 Repository-First

Das Repository ist die maßgebliche und verbindliche Quelle des Projekts.

Eine Information wird erst dann Bestandteil des Projekts, wenn sie als versioniertes, referenzierbares und überprüfbares Artefakt im Repository vorliegt.

Chatverläufe, mündliche Absprachen, persönliche Notizen und temporäre Entwürfe besitzen keine normative Wirkung. Sie können zur Vorbereitung dienen, ersetzen jedoch kein Repository-Artefakt.

### 3.2 Documentation-First

Grundlegende Modelle, Regeln, Anforderungen, Schnittstellen und Architekturentscheidungen werden vor oder spätestens gemeinsam mit ihrer Implementierung dokumentiert.

Eine Implementierung darf keine wesentlichen fachlichen oder architektonischen Regeln einführen, die nicht in einem maßgeblichen Artefakt beschrieben wurden.

Stellt sich während der Implementierung heraus, dass eine erforderliche Regel oder Entscheidung fehlt, wird die Implementierung unterbrochen. Zuerst wird das zuständige Dokument oder ADR erstellt beziehungsweise geändert. Erst anschließend wird die Implementierung fortgesetzt.

### 3.3 Verbindlichkeit

Eine Entscheidung gilt nur dann als verbindlich, wenn sie:

- in einem zuständigen Repository-Artefakt dokumentiert ist;
- einen erkennbaren Status besitzt;
- nachvollziehbar versioniert ist;
- geprüft wurde;
- keine höherrangige Regel verletzt;
- committed wurde.

### 3.4 Rolle des Chats

Der Chat bleibt ein Werkzeug für Analyse, Ideensammlung, Entwurf, Vergleich von Alternativen, Vorbereitung von Dokumenten, Reviews, Fehlersuche und Erläuterungen.

Der Chat ist jedoch nicht die dauerhafte Wissensbasis des Projekts. Relevante Ergebnisse müssen in das Repository überführt werden.

### 3.5 Reihenfolge der Arbeit

Für grundlegende Änderungen gilt grundsätzlich folgende Reihenfolge:

```text
Bedarf
  → Analyse
  → Entscheidung
  → Dokumentation
  → Review
  → Implementierung
  → Validierung
  → Commit
```

Bei kleineren Änderungen kann der Umfang reduziert werden. Die Grundrichtung bleibt bestehen.

### 3.6 Begrenzung neuer Architekturideen

Während der Aufbauphase der grundlegenden Projektdokumentation werden keine neuen umfangreichen Architekturkonzepte entwickelt, sofern sie nicht zur Fertigstellung eines aktuell bearbeiteten Artefakts erforderlich sind.

Neue Ideen werden zunächst als nicht verbindliche Hinweise erfasst und erst im zuständigen Arbeitspaket bearbeitet.

## 4. Begründung

### 4.1 Nachvollziehbarkeit

Das Repository ermöglicht die dauerhafte und chronologische Nachverfolgung von Änderungen. Jede relevante Änderung kann einem Commit, Dokument und gegebenenfalls einer Entscheidung zugeordnet werden.

### 4.2 Unabhängigkeit von Personen

Das Projekt darf nicht davon abhängig sein, dass einzelne Beteiligte frühere Gespräche kennen oder sich an Entscheidungen erinnern.

Eine fachkundige Person soll den Projektstand allein anhand des Repositorys verstehen können.

### 4.3 Vermeidung impliziter Architektur

Ohne Documentation-First entstehen Architekturregeln häufig unbeabsichtigt im Quellcode. Solche Regeln sind schwer erkennbar, überprüfbar und veränderbar.

Die vorherige Dokumentation zwingt dazu, Zweck, Verantwortung und Auswirkungen bewusst zu formulieren.

### 4.4 Konsistenz

Eine zentrale, versionierte Wissensbasis verringert das Risiko widersprüchlicher Definitionen. Begriffe, Modelle und Verantwortlichkeiten können eindeutig referenziert werden.

### 4.5 Prüfbarkeit

Repository-Artefakte können manuell und später teilweise automatisiert geprüft werden, beispielsweise auf Dokumentköpfe, eindeutige Kennungen, Verweise, Versionsangaben, Statusangaben, Abhängigkeiten, Architekturregeln und Tests.

### 4.6 Langfristige Wartbarkeit

Das Projekt ist langfristig angelegt. Deshalb ist eine dauerhafte Wissens- und Entscheidungsstruktur wichtiger als kurzfristige Geschwindigkeit.

## 5. Betrachtete Alternativen

### 5.1 Chat-First

Der Chat bleibt die primäre Arbeits- und Wissensquelle.

**Vorteile:** schnelle Diskussion, geringe formale Hürden, flexible Ideenentwicklung.

**Nachteile:** eingeschränkte Auffindbarkeit, keine zuverlässige Versionierung, unklarer Freigabestatus, geringe langfristige Nachvollziehbarkeit und starke Abhängigkeit vom Gesprächskontext.

**Ergebnis:** verworfen.

### 5.2 Code-First

Es wird zuerst implementiert und anschließend dokumentiert.

**Vorteile:** schnelle sichtbare Ergebnisse und frühe technische Erkenntnisse.

**Nachteile:** Architektur entsteht implizit, fachliche Regeln werden mit technischen Entscheidungen vermischt, Dokumentation bleibt häufig unvollständig und Prototypen werden unbeabsichtigt zur dauerhaften Architektur.

**Ergebnis:** für grundlegende Architektur- und Modellentscheidungen verworfen. Klar gekennzeichnete technische Experimente bleiben zulässig.

### 5.3 Externes Wiki als führende Quelle

Eine externe Dokumentationsplattform wird zur maßgeblichen Wissensquelle.

**Vorteile:** komfortable Bearbeitung, Navigation und Zusammenarbeit.

**Nachteile:** Trennung von Code und Dokumentation, zusätzliche Abhängigkeit, erschwerte gemeinsame Versionierung und mögliches Auseinanderlaufen von Repository und Wiki.

**Ergebnis:** als primäre Quelle verworfen. Ein Wiki kann später als abgeleitete Darstellung verwendet werden.

### 5.4 Mehrere gleichwertige Quellen

Chat, Wiki, Repository und weitere Systeme sind gleichwertig.

**Vorteile:** hohe Flexibilität.

**Nachteile:** keine eindeutige Wahrheit, Widersprüche, hoher Synchronisierungsaufwand und unklare Verantwortlichkeiten.

**Ergebnis:** verworfen.

## 6. Konsequenzen

### 6.1 Positive Konsequenzen

- Entscheidungen werden dauerhaft nachvollziehbar.
- Projektwissen bleibt unabhängig von einzelnen Personen erhalten.
- Architektur und Implementierung können getrennt geprüft werden.
- Widersprüche werden früher sichtbar.
- Dokumente, Code und Tests können gemeinsam versioniert werden.
- Reviews erhalten eine klare Grundlage.
- Der tatsächliche Projektstand wird eindeutig.
- Spätere Automatisierungen werden möglich.

### 6.2 Negative Konsequenzen

- Die Erstellung von Artefakten benötigt zusätzliche Zeit.
- Vor einer Implementierung entsteht mehr formaler Aufwand.
- Unvollständige Ideen können nicht sofort als verbindliche Architektur behandelt werden.
- Dokumente müssen kontinuierlich gepflegt werden.
- Änderungen können langsamer erscheinen.

Diese Nachteile werden bewusst akzeptiert.

### 6.3 Risiken

Es besteht das Risiko einer übermäßigen Bürokratisierung. Deshalb gilt das Prinzip der Verhältnismäßigkeit:

> Der Umfang von Dokumentation, Review und Nachweis richtet sich nach Bedeutung, Risiko, Reichweite und Dauerhaftigkeit einer Änderung.

Dokumente müssen einen konkreten Zweck erfüllen und dürfen nicht allein zur Erfüllung eines Prozesses entstehen.

## 7. Ausnahmen

Ausnahmen sind für kurzfristige technische Experimente, Wegwerfprototypen, lokale Untersuchungen, isolierte Fehlersuche und Machbarkeitsprüfungen zulässig.

Ausnahmen müssen als solche gekennzeichnet sein. Ein experimentelles Ergebnis wird nicht automatisch Bestandteil der Architektur.

Soll ein Experiment übernommen werden, müssen die erforderlichen Dokumente, Entscheidungen und Prüfungen nachgeholt werden.

Grundlegende Sicherheits-, Identitäts-, Eigentums- oder Datenintegritätsregeln dürfen nicht durch eine Ausnahme umgangen werden.

## 8. Auswirkungen auf den Entwicklungsprozess

Nach Annahme dieses ADR gelten folgende Regeln:

1. Es wird jeweils ein klar abgegrenztes Arbeitspaket bearbeitet.
2. Das zuständige Artefakt wird vor der Implementierung identifiziert.
3. Fehlende Grundsatzentscheidungen werden durch ADRs dokumentiert.
4. Dokumente erhalten eindeutige Kennungen, Versionen und Statusangaben.
5. Änderungen werden geprüft.
6. Implementierungen müssen auf maßgebliche Dokumente zurückführbar sein.
7. Tests und Validierungen werden dem Arbeitspaket zugeordnet.
8. Ein Commit enthält möglichst nur eine logisch zusammengehörige Änderung.
9. Nicht dokumentierte Chatentscheidungen gelten nicht als verbindlich.
10. Der nächste Arbeitsschritt richtet sich nach dem Repository-Stand und nicht nach der Menge diskutierter Ideen.

## 9. Auswirkungen auf bestehende Inhalte

Die bisher im Chat entwickelten Inhalte gelten als Rohmaterial.

Sie müssen geprüft, konsolidiert und in zuständige Repository-Artefakte überführt werden. Dabei wird nicht automatisch jede diskutierte Idee übernommen.

Jeder Inhalt wird danach eingeordnet, ob er ein dauerhaftes Prinzip, eine Architekturentscheidung, ein Modell, eine Spezifikation, einen Prozess, eine spätere Idee oder eine verworfene Alternative darstellt.

## 10. Abhängigkeiten

Dieses ADR steht in Beziehung zu:

- `../PROJECT_CONSTITUTION.md`
- `../PROJECT_PRINCIPLES.md`
- `../DEVELOPMENT_PROCESS.md`
- `../ARCHITECTURE_VISION.md`
- allen zukünftigen ADRs
- allen normativen Modellen und Spezifikationen

Die Projektverfassung besitzt Vorrang vor diesem ADR.

## 11. Prüfbare Akzeptanzkriterien

Dieses ADR gilt als umgesetzt, wenn:

- `PROJECT_CONSTITUTION.md` im Repository vorhanden ist;
- dieses ADR im Repository vorhanden ist;
- ein definierter Dokumentstatus verwendet wird;
- grundlegende Entscheidungen über ADRs dokumentiert werden;
- der Chat nicht als verbindliche Projektquelle behandelt wird;
- neue grundlegende Implementierungen auf dokumentierte Artefakte verweisen;
- ein Entwicklungsprozess für Review, Validierung und Commit definiert ist;
- die grundlegenden Projektdokumente in deutscher Sprache geführt werden.

## 12. Entscheidungsergebnis

Das Projekt arbeitet ab sofort Repository-First und Documentation-First.

Das Repository ist die verbindliche Projektquelle. Der Chat unterstützt die Projektarbeit, besitzt aber keine eigenständige normative Autorität.

Architektur, Modelle und wesentliche Regeln werden dokumentiert, bevor sie dauerhaft implementiert werden.
