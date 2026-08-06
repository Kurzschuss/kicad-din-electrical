# Projektprinzipien

**Dokument-ID:** GOV-0002  
**Titel:** Verbindliche Projektprinzipien  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** A  
**Autoritätsebene:** Projektprinzipien  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Zweck

Dieses Dokument konkretisiert die Projektverfassung durch verbindliche Leitprinzipien für Architektur, Dokumentation, Entwicklung und Betrieb.

Die Projektverfassung besitzt Vorrang. Dieses Dokument erläutert, wie deren Grundsätze im Projekt angewendet werden.

`VISION.md` beschreibt das fachliche Ziel der KiCad DIN Electrical Library. `MANIFESTO.md` beschreibt den Anspruch und das Arbeitsverständnis. Dieses Dokument definiert die übergreifenden Projektprinzipien.

## 2. Repository-First

Das Repository ist die verbindliche Quelle des Projekts.

Eine Entscheidung, Regel oder Spezifikation gilt erst dann als Projektbestandteil, wenn sie als versioniertes und überprüfbares Artefakt im Repository vorliegt.

Chatverläufe, mündliche Absprachen und lokale Notizen dienen ausschließlich der Vorbereitung.

## 3. Documentation-First

Wesentliche fachliche und architektonische Regeln werden vor oder gemeinsam mit ihrer Implementierung dokumentiert.

Quellcode darf nicht zur einzigen Quelle einer fachlichen Regel werden.

Fehlt während einer Umsetzung eine grundlegende Entscheidung, wird zunächst das zuständige Modell, die Spezifikation oder ein ADR ergänzt.

## 4. Single Source of Truth

Für jedes normative Thema gibt es genau eine maßgebliche Quelle.

Andere Dokumente verweisen darauf, statt konkurrierende Definitionen zu erzeugen.

Wiederholungen müssen als nicht maßgeblich gekennzeichnet sein und auf die verbindliche Quelle verweisen.

## 5. Object-First

Objekte bilden die primären fachlichen Einheiten der Plattform.

Ein Objekt besitzt eine stabile Identität, die nicht von Dateipfad, Anzeigename, Speicherort oder technischer Darstellung abhängt.

Die vollständige Definition erfolgt in `OBJECT_MODEL.md`.

## 6. Domain Ownership

Jedes fachliche Konzept besitzt genau eine zuständige Domäne.

Die zuständige Domäne definiert Bedeutung, Lebenszyklus, Validierungsregeln und Änderungsregeln.

Andere Domänen verwenden das Konzept über dokumentierte Schnittstellen, Beziehungen, Ereignisse oder Dienste.

## 7. Explizit vor implizit

Wesentliches Verhalten, wichtige Standardwerte, Abhängigkeiten und Nebenwirkungen werden ausdrücklich beschrieben.

Nicht dokumentierte Annahmen dürfen keine Grundlage für sicherheits-, identitäts-, daten- oder berechtigungsrelevantes Verhalten sein.

## 8. Modelle vor Technologien

Fachliche Modelle werden unabhängig von konkreten Programmiersprachen, Frameworks, Datenbanken, Protokollen und Herstellern beschrieben.

Technologien setzen Modelle um, definieren sie aber nicht.

## 9. Offline-First

Grundlegende Projektfunktionen und maßgebliche Projektdaten sollen ohne permanente Verbindung zu externen Diensten nutzbar bleiben.

Externe Dienste dürfen erweitern, aber nicht ohne dokumentierte Entscheidung zur einzigen Quelle zentraler Identitäten, Modelle, Konfigurationen oder Historien werden.

## 10. Simulation-First

Verhalten mit wesentlichen Auswirkungen auf reale Geräte, Datenintegrität, Sicherheit, Berechtigungen oder irreversible Zustände soll vor der realen Ausführung kontrolliert prüfbar sein.

Simulationen verwenden soweit möglich dieselben fachlichen Modelle und Verträge wie die reale Ausführung.

Bekannte Abweichungen werden dokumentiert.

## 11. Sicherheit durch Architektur

Sicherheit wird bereits während Modellierung und Spezifikation berücksichtigt.

Authentifizierung, Autorisierung, fachliche Eigentümerschaft und Sitzungsverwaltung sind getrennte Verantwortungsbereiche.

Es gelten insbesondere minimale Berechtigungen, sichere Standardwerte, nachvollziehbare Änderungen und kontrollierte Vertrauensgrenzen.

## 12. Identität vor Darstellung

Eine fachliche Identität bleibt unabhängig von ihrer technischen oder visuellen Repräsentation bestehen.

Umbenennen, Verschieben, Migrieren oder ein Wechsel des Dateiformats dürfen eine Identität nicht stillschweigend zerstören.

## 13. Beziehungen als fachliche Konzepte

Bedeutungsvolle Beziehungen werden ausdrücklich modelliert.

Sie besitzen definierte Typen, zulässige Beteiligte, Richtung oder Symmetrie sowie Validierungs- und gegebenenfalls Lebenszyklusregeln.

## 14. Modularität

Komponenten und Domänen besitzen klar begrenzte Verantwortlichkeiten.

Interne Details werden nicht unbeabsichtigt zu öffentlichen Verträgen.

Module sollen soweit sinnvoll unabhängig verständlich, testbar, versionierbar und austauschbar sein.

## 15. Kontrollierte Erweiterbarkeit

Neue Funktionen erweitern das Projekt über dokumentierte Schnittstellen, Schemata, Beziehungen, Ereignisse, Dienste oder Plugin-Mechanismen.

Erweiterungen dürfen Kernregeln zu Identität, Berechtigungen, Validierung, Versionierung und Nachvollziehbarkeit nicht umgehen.

## 16. Einfachheit

Bevorzugt wird die einfachste Lösung, die Anforderungen erfüllt und die architektonische Integrität erhält.

Neue Abstraktionen und Sonderfälle werden nur eingeführt, wenn sie ein konkretes Problem lösen.

## 17. Nachvollziehbarkeit

Wesentliche Änderungen sollen von ihrem Zweck über Entscheidung, Modell und Implementierung bis zu Test und Freigabe nachvollziehbar sein.

Der erforderliche Umfang richtet sich nach Risiko, Tragweite und Dauerhaftigkeit.

## 18. Prüfbarkeit

Wichtige Regeln werden so formuliert, dass ihre Einhaltung durch Tests, Simulationen, automatisierte Prüfungen oder strukturierte Reviews nachgewiesen werden kann.

Nicht automatisierbare Regeln müssen dennoch eindeutig und konsistent prüfbar sein.

## 19. Menschen- und Maschinenlesbarkeit

Maßgebliche Artefakte müssen für Menschen verständlich sein.

Wo automatisierte Verarbeitung einen erkennbaren Nutzen schafft, werden Strukturen zusätzlich maschinenlesbar bereitgestellt.

Bei mehreren Darstellungen muss ihre normative Beziehung ausdrücklich festgelegt sein.

## 20. Rückwärtskompatibilität

Änderungen an bestehenden Objekten, Schemata, Schnittstellen und Arbeitsabläufen berücksichtigen Kompatibilität, Migration und Rückkehrmöglichkeiten.

Bewusste Kompatibilitätsbrüche werden dokumentiert, versioniert und freigegeben.

## 21. Qualität vor Quantität

Eine größere Anzahl von Symbolen, Footprints, Funktionen oder Dokumenten ist kein Selbstzweck.

Neue Inhalte müssen verständlich, konsistent, geprüft, dokumentiert und langfristig wartbar sein.

Dieser Grundsatz konkretisiert `VISION.md` und `MANIFESTO.md`.

## 22. Anwendernutzen

Änderungen sollen einen nachvollziehbaren Nutzen für Anwender, Mitwirkende oder die langfristige Projektintegrität schaffen.

Technische Komplexität ohne klaren Nutzen wird vermieden.

## 23. Kontinuierliche Verbesserung

Fehler, Review-Ergebnisse, Simulationen, Tests und praktische Nutzung dienen der systematischen Verbesserung.

Verbesserungen werden nachvollziehbar dokumentiert und dürfen höherrangige Regeln nicht stillschweigend verändern.

## 24. Verhältnismäßigkeit

Der Umfang von Dokumentation, Review und Prüfung richtet sich nach Bedeutung, Risiko, Reichweite und Dauerhaftigkeit einer Änderung.

Das Projekt vermeidet sowohl unkontrollierte Änderungen als auch unnötige Bürokratie.

## 25. Definition eines abgeschlossenen Ergebnisses

Ein Ergebnis ist erst abgeschlossen, wenn die für seinen Umfang erforderlichen Dokumentationen, Implementierungen, Tests, Simulationen, Reviews und Verweise vollständig und konsistent vorliegen.

Eine vorhandene Datei oder funktionierende Einzelimplementierung allein genügt nicht.

## 26. Verhältnis zu bestehenden Dokumenten

- `PROJECT_CONSTITUTION.md` besitzt den höchsten normativen Rang.
- `PROJECT_PRINCIPLES.md` konkretisiert die Projektverfassung.
- `VISION.md` definiert das fachliche Ziel der KiCad DIN Electrical Library.
- `MANIFESTO.md` beschreibt Anspruch, Haltung und Anwenderorientierung.
- ADRs dokumentieren einzelne grundlegende Entscheidungen und deren Begründung.
- Modelle und Spezifikationen konkretisieren die fachliche und technische Architektur.

Bei Widersprüchen gilt die normative Rangordnung der Projektverfassung.
