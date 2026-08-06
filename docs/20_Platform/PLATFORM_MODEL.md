# Plattformmodell

**Dokument-ID:** PLT-0001  
**Titel:** Grundlegendes Plattformmodell  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Zweck

Dieses Dokument definiert Verantwortung, Umfang und Grenzen der Plattformebene.

Die Plattform verwendet die Core-Konzepte, um domänenübergreifende Modelle und Dienste bereitzustellen. Sie ist weder Kernel noch Fachdomäne.

Dieses Dokument beschreibt keine konkrete Programmiersprache, Datenbank, Benutzeroberfläche, Cloud-Plattform oder Kommunikationsimplementierung.

## 2. Stellung in der Architektur

Die Plattform liegt zwischen Core und Domänen:

```text
Meta
  ↓
Core
  ↓
Plattform
  ↓
Domänen
```

Die Plattform darf Core-Modelle verwenden. Sie darf den Core jedoch nicht stillschweigend erweitern.

Domänen dürfen Plattformdienste verwenden. Die Plattform darf keine konkrete Fachdomäne voraussetzen.

## 3. Definition

Die Plattform ist die domänenunabhängige Ebene, die gemeinsame Modelle, Dienste, Verträge und Betriebsfunktionen für Projekte, Akteure, Wissen, Kommunikation, Konfiguration, Erweiterungen, Suche, Audit und Speicherung bereitstellt.

Sie schafft einen einheitlichen Rahmen, in dem unterschiedliche Fachdomänen dieselben grundlegenden Mechanismen verwenden können.

## 4. Verantwortungsbereiche

Die Plattform umfasst mindestens folgende Verantwortungsbereiche:

- Projektverwaltung;
- Workspace- und Arbeitskontextverwaltung;
- Akteurs- und Identitätsverwaltung;
- Konten, Authentifizierung und Sitzungen;
- Autorisierung, Rollen und Berechtigungen;
- Organisationen, Teams und Zugehörigkeiten;
- Projektgedächtnis und Wissensbeziehungen;
- fachliche Kommunikation und Ereignisverteilung;
- Konfiguration;
- Erweiterbarkeit und Plugins;
- Suche und Auffindbarkeit;
- Audit und Nachweis;
- Speicherung und Referenzauflösung;
- gemeinsame Plattformdienste.

Jeder Verantwortungsbereich erhält bei Bedarf ein eigenes Modell und einen eigenen Dienstvertrag.

## 5. Modelle und Dienste

Die Plattform trennt fachliche Struktur und Verhalten:

- Ein **Modell** beschreibt, was ein Plattformkonzept ist.
- Ein **Dienst** beschreibt, welche fachlichen Operationen darauf zulässig sind.
- Eine **Implementierung** beschreibt die technische Umsetzung.

Beispiel:

```text
PROJECT_MODEL.md
  ↓
PROJECT_SERVICE.md
  ↓
technische Implementierung
```

Modelle dürfen keine versteckten technischen Implementierungsentscheidungen enthalten.

## 6. Plattformobjekte

Plattformkonzepte werden als Objekte modelliert, wenn sie dauerhaft identifizierbar, referenzierbar, versionierbar oder historisierbar sein müssen.

Beispiele:

- Projekt;
- Workspace;
- Benutzer;
- Konto;
- Akteursidentität;
- Organisation;
- Rolle;
- Berechtigung;
- Sitzung;
- Delegation;
- Audit-Eintrag;
- Konfigurationsobjekt;
- Plugin;
- Wissenselement;
- Suchprofil.

Sie verwenden `OBJECT_MODEL.md`, `OBJECT_INTERFACE.md`, `OBJECT_SERVICE.md`, `SCHEMA_MODEL.md` und `RELATION_MODEL.md`.

## 7. Projektverwaltung

Die Plattform stellt ein fachliches Projektmodell und dazugehörige Dienste bereit.

Ein Projekt ist kein Repository, Ordner oder Workspace.

Ein Projekt bildet einen fachlichen und organisatorischen Bezugsrahmen für:

- Ziele;
- Artefakte;
- Domänen;
- Verantwortlichkeiten;
- Mitglieder;
- Versionen;
- Releases;
- Historie;
- Berechtigungs- und Auditkontexte.

Die Detaildefinition erfolgt in `PROJECT_MODEL.md`.

## 8. Workspace und Arbeitskontext

Ein Workspace beschreibt einen Arbeitskontext und ist vom Projekt zu trennen.

Ein Workspace kann:

- mehrere Projekte referenzieren;
- persönliche oder gemeinsame Ansichten enthalten;
- lokale Arbeitszustände verwalten;
- temporäre Auswahl- und Navigationszustände enthalten;
- benutzerspezifische oder gerätespezifische Einstellungen referenzieren.

Ein Projekt darf in mehreren Workspaces verwendet werden. Ein Workspace darf mehrere Projekte enthalten.

## 9. Akteurs- und Identitätsverwaltung

Die Plattform verwaltet menschliche und technische Akteure als eigenständige Akteursidentitäten.

Dazu gehören insbesondere:

- Benutzer;
- Geräte;
- Dienste;
- Servicekonten;
- API-Clients;
- Automatisierungen;
- definierte Systemprozesse;
- externe Identitäten.

Objektidentität aus dem Core und Akteursidentität der Plattform bleiben getrennte Begriffe.

Die Detailmodelle folgen ADR-0002.

## 10. Authentifizierung und Autorisierung

Die Plattform trennt:

- Authentifizierung als Nachweis einer behaupteten Identität;
- Autorisierung als Entscheidung über eine konkrete Handlung in einem konkreten Geltungsbereich.

Rollen, Berechtigungen, Eigentum, Verantwortung und Zugehörigkeit werden nicht gleichgesetzt.

Der Core erhält bei geschützten Operationen nur einen Autorisierungskontext oder eine bereits ermittelte Entscheidung gemäß ADR-0004.

## 11. Organisationen und Zugehörigkeiten

Organisationen, Teams, Gruppen und andere organisatorische Einheiten sind Plattformobjekte.

Zugehörigkeiten werden als Beziehungen modelliert.

Eine Zugehörigkeit kann Grundlage für Rollen oder Berechtigungen sein, ist aber selbst keine Berechtigungsentscheidung.

## 12. Projektgedächtnis

Die Plattform bewahrt dauerhaftes Projektwissen als referenzierbare Wissenselemente und Beziehungen.

Zum Projektgedächtnis können gehören:

- Entscheidungen;
- Anforderungen;
- Modelle;
- Spezifikationen;
- Implementierungen;
- Tests;
- Releases;
- Erkenntnisse;
- bekannte Einschränkungen;
- historische Zusammenhänge.

Das Projektgedächtnis ist keine konkrete Datenbank. Sein fachliches Modell wird separat definiert.

## 13. Kommunikation

Die Plattform stellt einen fachlichen Kommunikationsmechanismus für Ereignisse und andere ausdrücklich definierte Nachrichten bereit.

Der Plattformbus beschreibt keine konkrete Technologie.

Er muss mindestens unterscheiden können zwischen:

- eingetretener fachlicher Tatsache;
- Änderungsanforderung oder Befehl;
- Anfrage;
- Antwort;
- technischer Zustellinformation.

Domänenereignisse werden von Domänen definiert, aber über gemeinsame Plattformverträge transportiert.

## 14. Konfiguration

Konfigurationen werden als versionierbare, validierbare und referenzierbare Plattformobjekte behandelt, wenn sie fachlich oder betrieblich relevant sind.

Konfiguration darf keine versteckten Fachregeln erzeugen.

Es muss unterscheidbar bleiben zwischen:

- projektweiter Konfiguration;
- Workspace-Konfiguration;
- benutzerspezifischer Konfiguration;
- Systemkonfiguration;
- domänenspezifischer Konfiguration;
- geheimen oder sicherheitsrelevanten Werten.

## 15. Erweiterbarkeit und Plugins

Die Plattform darf Erweiterungen über dokumentierte Verträge zulassen.

Plugins dürfen:

- neue Plattformfunktionen ergänzen;
- neue Domänenmodelle bereitstellen;
- vorhandene Erweiterungspunkte verwenden.

Plugins dürfen nicht:

- Core-Invarianten umgehen;
- Identitäts- oder Berechtigungsprüfungen umgehen;
- unbekannte versteckte Fachregeln einführen;
- bestehende Modelle stillschweigend umdeuten;
- Sicherheits- oder Auditgrenzen aufheben.

## 16. Suche

Suche ist eine Plattformfunktion und keine bloße Benutzeroberflächenhilfe.

Sie soll Objekte und Wissenselemente mindestens anhand folgender Kriterien auffindbar machen können:

- Objektidentität;
- Typ;
- Schema;
- Eigenschaften;
- Beziehungen;
- Lebenszyklusstatus;
- Version;
- Verantwortlichkeit;
- Projekt- oder Organisationskontext;
- Volltext oder Tags, soweit zulässig.

Suche muss Berechtigungs- und Sichtbarkeitsgrenzen beachten.

## 17. Audit

Audit dokumentiert sicherheits-, verantwortungs- oder nachweisrelevante Vorgänge.

Audit ist von der fachlichen Objekthistorie zu unterscheiden:

- Historie beschreibt die Entwicklung eines Objekts.
- Audit beschreibt einen Vorgang, seinen Akteur, Kontext, Berechtigungsbezug und sein Ergebnis.

Audit-Einträge dürfen nicht stillschweigend nachträglich in ihrer Bedeutung verändert werden.

## 18. Speicherung und Referenzauflösung

Die Plattform stellt Dienste für dauerhafte Speicherung, Laden, Suche und Auflösung opaker Referenzen bereit.

Die Plattform darf unterschiedliche Speichertechnologien verwenden, muss jedoch die Core-Garantien erhalten:

- stabile Identität;
- Versionierung;
- Validierung;
- Referenzintegrität;
- Historie;
- Fehlertransparenz;
- Offline-Fähigkeit gemäß Betriebsmodus.

## 19. Offline-First

Grundlegende Plattformfunktionen sollen ohne permanente Verbindung zu externen Diensten nutzbar bleiben, soweit der konkrete Betriebsmodus dies vorsieht.

Dazu können gehören:

- lokale Projekte;
- lokale Akteursidentitäten und Konten;
- lokale Autorisierungsentscheidungen;
- notwendige Schemata;
- Objekt- und Referenzauflösung;
- lokale Suche;
- lokale Konfiguration;
- lokale Audit- und Historienerfassung.

Synchronisation ist ein eigener kontrollierter Vorgang und darf Konflikte nicht stillschweigend überschreiben.

## 20. Plattformgrenzen

Die Plattform definiert ausdrücklich nicht:

- konkrete MCB-, RCD-, SPD- oder andere Elektrofachmodelle;
- KiCad-spezifische Symbole, Footprints oder Schaltplandetails;
- konkrete Datenbanken, Broker oder Suchindizes;
- konkrete GUI-Frameworks;
- konkrete Authentifizierungsanbieter;
- konkrete Programmiersprachen oder Deployment-Plattformen.

Diese Themen gehören in Domänen-, Implementierungs- oder Betriebsartefakte.

## 21. Abhängigkeitsregeln

Für Plattformmodelle gelten:

1. Sie verwenden Core-Konzepte und halten deren Invarianten ein.
2. Sie dürfen den Core nicht stillschweigend erweitern.
3. Sie dürfen keine konkrete Fachdomäne voraussetzen.
4. Gemeinsame Plattformfunktionalität wird nicht in einer einzelnen Domäne versteckt.
5. Domänenspezifische Anforderungen werden nur dann in die Plattform übernommen, wenn ihre allgemeine Notwendigkeit nachgewiesen ist.
6. Modelle, Dienste und Implementierungen bleiben getrennt.

## 22. Plattforminvarianten

1. Die Plattform ist domänenunabhängig.
2. Der Core bleibt von Plattformmodellen unabhängig.
3. Jedes Plattformkonzept besitzt eine eindeutige Verantwortung.
4. Authentifizierung und Autorisierung bleiben getrennt.
5. Historie und Audit bleiben getrennt.
6. Projekt und Workspace bleiben getrennt.
7. Berechtigungsgrenzen gelten auch für Suche, Bus, Plugins und Referenzauflösung.
8. Plattformdienste dürfen keine ungültigen Core-Objekte als erfolgreich verarbeitet melden.
9. Externe Dienste werden nicht stillschweigend zur einzigen maßgeblichen Quelle grundlegender Plattformdaten.
10. Technische Implementierungen dürfen die fachliche Bedeutung eines Plattformmodells nicht bestimmen.

## 23. Geplante Plattformmodelle

Auf Grundlage dieses Dokuments sind zunächst vorgesehen:

1. `PROJECT_MODEL.md`;
2. `PROJECT_SERVICE.md`;
3. `WORKSPACE_MODEL.md`;
4. `IDENTITY_MODEL.md`;
5. `IDENTITY_SERVICE.md`;
6. weitere Modelle gemäß ADR-0002;
7. Modelle für Projektgedächtnis, Bus, Suche, Audit, Konfiguration und Plugins.

Die Reihenfolge kann durch Abhängigkeiten angepasst werden, ohne die Plattformgrenze zu verändern.

## 24. Abhängigkeiten

Dieses Dokument konkretisiert:

- `PROJECT_CONSTITUTION.md`;
- `PROJECT_PRINCIPLES.md`;
- `ADR-0002-identitaet-als-plattformkonzept.md`;
- `ADR-0003-architekturebenen-und-kernelgrenze.md`;
- `ADR-0004-core-referenzen-und-schema-bootstrap.md`;
- `CORE_MODEL.md`;
- die Core-Objekt-, Schema- und Beziehungsmodelle.

## 25. Ergebnis

Die Plattform bildet die domänenunabhängige Betriebs- und Diensterweiterung des Kernels.

Sie stellt gemeinsame Projekt-, Arbeitskontext-, Identitäts-, Wissens-, Kommunikations-, Konfigurations-, Erweiterungs-, Such-, Audit- und Speicherfunktionen bereit, ohne den Kernel oder eine konkrete Fachdomäne zu ersetzen.