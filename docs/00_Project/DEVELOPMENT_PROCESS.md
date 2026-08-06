# Entwicklungsprozess

**Dokument-ID:** GOV-0003  
**Titel:** Verbindlicher Entwicklungsprozess  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Governance  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Zweck

Dieses Dokument beschreibt, wie aus einer Idee ein verbindliches Projektartefakt entsteht.

Es konkretisiert die Projektverfassung, die Projektprinzipien und ADR-0001. Es gilt für Dokumentation, Modelle, Spezifikationen, Quellcode, Tests, Simulationen und andere versionierte Projektartefakte.

## 2. Grundsatz

Das Projekt arbeitet artefaktgetrieben.

Eine Diskussion, Idee oder technische Untersuchung wird erst dann Bestandteil des Projekts, wenn ihr Ergebnis als versioniertes, referenzierbares und überprüfbares Artefakt im Repository vorliegt.

Der Umfang des Verfahrens richtet sich nach Tragweite, Risiko und Dauerhaftigkeit der Änderung.

## 3. Arbeitspakete

Zusammengehörige Änderungen werden als Arbeitspaket geführt.

Ein Arbeitspaket besitzt mindestens:

- eine eindeutige AP-ID;
- einen Titel;
- einen Zweck;
- einen abgegrenzten Geltungsbereich;
- erwartete Artefakte;
- bekannte Abhängigkeiten;
- Akzeptanzkriterien;
- einen Status.

Ein Arbeitspaket kann mehrere Artefakte erzeugen. Dokument-ID und Arbeitspaket-ID sind voneinander unabhängig.

## 4. Ablauf

Für wesentliche Änderungen gilt grundsätzlich:

```text
Bedarf oder Idee
    ↓
Analyse
    ↓
Entscheidung oder Spezifikation
    ↓
Erstellung des Artefakts
    ↓
Review
    ↓
Validierung
    ↓
Commit
    ↓
Freigabe oder Release
```

Kleine, risikoarme Änderungen dürfen ein vereinfachtes Verfahren verwenden, sofern Nachvollziehbarkeit und Qualität erhalten bleiben.

## 5. Artefaktarten

Das Projekt unterscheidet mindestens:

- Governance-Artefakte;
- Architecture Decision Records;
- Architekturmodelle;
- Fachmodelle;
- Spezifikationen;
- Referenzdokumente;
- Quellcode;
- Tests und Prüfnachweise;
- Simulationen;
- Konfigurationen;
- generierte Ergebnisse.

Jedes Artefakt besitzt einen eindeutigen Zweck. Es darf keine maßgebliche Definition duplizieren, die bereits einem anderen Artefakt zugeordnet ist.

## 6. Statusmodell

Dokumente und vergleichbare Artefakte verwenden, soweit anwendbar, folgende Statuswerte:

- **Entwurf:** Inhalt wird erstellt und ist nicht verbindlich.
- **In Review:** Inhalt wird fachlich oder technisch geprüft.
- **Freigegeben:** Inhalt wurde angenommen und ist verbindlich.
- **Aktiv:** Artefakt wird im laufenden Projektbetrieb verwendet.
- **Veraltet:** Artefakt soll nicht mehr für neue Arbeiten verwendet werden.
- **Archiviert:** Artefakt bleibt aus historischen Gründen erhalten.

Ein Artefakt darf nur durch einen dokumentierten Übergang seinen Status ändern.

## 7. Review

Vor der Freigabe eines wesentlichen Artefakts werden mindestens geprüft:

- Zweck und Geltungsbereich;
- Vollständigkeit;
- Widerspruchsfreiheit;
- Vereinbarkeit mit höherrangigen Artefakten;
- Terminologie und Glossar;
- Referenzen und Abhängigkeiten;
- Sicherheits- und Berechtigungsauswirkungen;
- Kompatibilitätsauswirkungen;
- Prüfbarkeit und Akzeptanzkriterien.

Ein Review soll konkrete Feststellungen und erforderliche Änderungen enthalten.

## 8. Validierung

Die Validierung weist nach, dass das Artefakt seinen Zweck erfüllt.

Je nach Artefakt kann sie umfassen:

- manuelle Dokumentprüfung;
- Schema- und Referenzprüfung;
- Architekturprüfung;
- Unit-, Integrations- oder Systemtests;
- Simulation;
- Konsistenzprüfung;
- Kompatibilitätsprüfung;
- Sicherheitsprüfung.

Nicht automatisierbare Regeln müssen so formuliert sein, dass ein reproduzierbares menschliches Review möglich ist.

## 9. Commit-Regeln

Ein Commit bildet eine logisch zusammengehörige Änderung.

Er soll:

- genau einen erkennbaren Zweck besitzen;
- keine sachfremden Mischänderungen enthalten;
- eine verständliche Commit-Nachricht verwenden;
- betroffene Dokumentation und Tests einschließen;
- auf ein Arbeitspaket oder eine Entscheidung verweisen, wenn dies für die Nachvollziehbarkeit erforderlich ist.

Unabhängige Artefakte werden in getrennten Commits angelegt oder geändert.

## 10. Freigabe

Ein Artefakt darf freigegeben werden, wenn:

- sein Zweck erfüllt ist;
- das erforderliche Review abgeschlossen ist;
- festgestellte Blocker behoben sind;
- notwendige Validierungen erfolgreich waren;
- abhängige Artefakte berücksichtigt wurden;
- bekannte Einschränkungen dokumentiert sind.

Die formelle Freigabeverantwortung wird in einem späteren Governance-Artefakt oder in der Repository-Konfiguration konkretisiert.

## 11. Definition of Done

Eine Änderung ist abgeschlossen, wenn alle für ihren Umfang relevanten Bedingungen erfüllt sind:

- Ziel und Geltungsbereich sind eindeutig;
- erforderliche Entscheidungen sind dokumentiert;
- maßgebliche Artefakte sind vollständig;
- Terminologie und Referenzen sind konsistent;
- Implementierung ist abgeschlossen, sofern vorhanden;
- Tests oder andere Validierungen sind erfolgreich;
- Sicherheits- und Kompatibilitätsauswirkungen sind geprüft;
- bekannte Einschränkungen sind dokumentiert;
- Änderungen sind logisch getrennt committed;
- der Status des Arbeitspakets ist aktualisiert.

Fertiggestellter Quellcode allein erfüllt die Definition of Done nicht.

## 12. Experimente und Prototypen

Technische Experimente und Wegwerfprototypen sind zulässig.

Sie müssen klar als nicht verbindlich gekennzeichnet sein und dürfen nicht stillschweigend zur Architektur oder produktiven Implementierung werden.

Vor einer Übernahme in das Projekt sind die erforderlichen Modelle, Spezifikationen, Entscheidungen, Tests und Dokumentationen nachzuholen.

## 13. Umgang mit neuen Ideen

Neue Ideen, die nicht zum aktuell bearbeiteten Arbeitspaket gehören, werden nicht ungeplant umgesetzt.

Sie werden als Hinweis, Issue, Roadmap-Eintrag oder späteres Arbeitspaket erfasst.

Dadurch bleiben laufende Arbeitspakete begrenzt und überprüfbar.

## 14. Verhältnis zu anderen Dokumenten

Dieses Dokument konkretisiert:

- `PROJECT_CONSTITUTION.md`;
- `PROJECT_PRINCIPLES.md`;
- `ADR-0001-repository-first-und-documentation-first.md`.

Das Projektglossar ist für die verwendete Terminologie maßgeblich.

Bei einem Widerspruch gilt das höherrangige Artefakt.