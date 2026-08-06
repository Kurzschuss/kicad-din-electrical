# Kernmodell

**Dokument-ID:** ARC-0004  
**Titel:** Übersicht und Grenze des Kernels  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** A  
**Autoritätsebene:** Architekturmodell  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Zweck

Dieses Dokument definiert Umfang, Verantwortung und Grenze des architektonischen Kernels.

Es ist die Landkarte der universellen Core-Konzepte. Es ersetzt nicht die jeweiligen Detailmodelle.

Der Kernel soll klein, stabil, domänenunabhängig und unabhängig von konkreten Plattformdiensten bleiben.

## 2. Grundsatz

Der Kernel enthält nur Konzepte, die zur Beschreibung und Verwaltung beliebiger dauerhaft identifizierbarer Objekte erforderlich sind.

Ein Konzept gehört nicht allein deshalb zum Kernel, weil es häufig verwendet wird.

Ein Konzept gehört nur dann zum Kernel, wenn nachgewiesen ist, dass es:

- für mehrere unabhängige Plattform- oder Domänenmodelle erforderlich ist;
- keine konkrete Fachdomäne voraussetzt;
- keinen konkreten Plattformdienst voraussetzt;
- nicht sinnvoll als Eigenschaft, Beziehung oder Spezialisierung eines bestehenden Core-Konzepts ausgedrückt werden kann.

## 3. Bestandteile des Kernels

Der vorläufige Kernel besteht aus:

```text
Core
├── Objekt
├── Objektidentität
├── Eigenschaft
├── Schema
├── Beziehung
├── Ereignis
├── Version
└── Lebenszyklus
```

### 3.1 Objekt

Das Objekt ist die grundlegende fachliche Einheit mit stabiler Identität, Typ, Zustand, Schema und Beziehungen.

Maßgebliche Dokumente:

- `OBJECT_MODEL.md`;
- `OBJECT_INTERFACE.md`;
- `OBJECT_SERVICE.md`.

### 3.2 Objektidentität

Die Objektidentität bezeichnet genau ein fachliches Objekt und bleibt unabhängig von Name, Speicherort, Darstellung und Zustand stabil.

Sie ist von Akteursidentitäten der Plattform zu unterscheiden.

### 3.3 Eigenschaft

Eine Eigenschaft beschreibt einen benannten und validierbaren Bestandteil des Zustands eines Objekts oder einer Beziehung.

Eigenschaften können Kern- oder Fachattribute repräsentieren.

Das detaillierte Eigenschaftsmodell ist noch nicht festgelegt.

### 3.4 Schema

Ein Schema definiert die zulässige Struktur, Pflichtangaben, Datentypen, Beziehungen, Statuswerte und Validierungsregeln eines Objekttyps oder einer anderen schemagebundenen Struktur.

Das detaillierte Modell wird in `SCHEMA_MODEL.md` festgelegt.

### 3.5 Beziehung

Eine Beziehung beschreibt eine typisierte, fachlich bedeutsame Verbindung zwischen Objekten.

Das detaillierte Modell wird in `RELATION_MODEL.md` festgelegt.

### 3.6 Ereignis

Ein Ereignis beschreibt eine eingetretene, fachlich relevante Tatsache.

Es ist von einem Befehl, einer Absicht oder einer technischen Nachricht zu unterscheiden.

Das detaillierte Ereignismodell ist noch nicht festgelegt.

### 3.7 Version

Eine Version kennzeichnet einen bestimmten, nachvollziehbaren Entwicklungs- oder Zustandsstand eines Objekts, Schemas, einer Beziehung oder eines anderen versionierten Artefakts.

Das detaillierte Versionsmodell ist noch nicht festgelegt.

### 3.8 Lebenszyklus

Ein Lebenszyklus definiert zulässige Zustände und Zustandsübergänge eines Objekts oder eines anderen lebenszyklusgebundenen Konzepts.

Das detaillierte Lebenszyklusmodell ist noch nicht festgelegt.

## 4. Nicht Bestandteil des Kernels

Folgende Konzepte gehören ausdrücklich nicht zum Kernel:

- Projekt;
- Workspace;
- Benutzer;
- Benutzerkonto;
- Akteursidentität;
- Authentifizierung;
- Autorisierung;
- Rolle;
- Berechtigung;
- Organisation;
- Sitzung;
- Delegation;
- Audit;
- Projektgedächtnis;
- Projektbus;
- Plugin;
- Konfiguration;
- Suche;
- Speicherung;
- KiCad-spezifische Modelle;
- MCB und andere Fachgeräte.

Diese Konzepte verwenden den Kernel, definieren ihn jedoch nicht.

## 5. Abhängigkeitsrichtung

Core-Modelle dürfen keine Plattform- oder Domänenmodelle voraussetzen oder referenzieren.

Plattformmodelle dürfen den Core verwenden.

Domänenmodelle dürfen Core und Plattform verwenden.

Ein Core-Modell darf technische Implementierungen beschreiben, aber nicht von einer konkreten Implementierung abhängig gemacht werden.

## 6. Trennung von Objektidentität und Akteursidentität

Jedes Objekt besitzt eine Objektidentität.

Eine Akteursidentität ist dagegen ein Plattformobjekt, das einen menschlichen oder technischen Akteur repräsentiert.

Beispiele für Akteursidentitäten sind:

- Benutzer;
- Gerät;
- Dienst;
- API-Client;
- Automatisierung;
- Systemprozess.

Akteursidentitäten verwenden die Core-Regeln für Objekte und Objektidentitäten. Sie erweitern den Core nicht um eine zweite allgemeine Identitätsart.

## 7. Kernel-Invarianten

Für den Kernel gelten mindestens folgende Regeln:

1. Der Kernel kennt keine konkrete Fachdomäne.
2. Der Kernel kennt keinen konkreten Plattformdienst.
3. Jedes Core-Konzept besitzt eine eindeutige Verantwortung.
4. Core-Konzepte dürfen sich nicht gegenseitig widersprüchlich definieren.
5. Neue Core-Konzepte benötigen eine dokumentierte Begründung und grundsätzlich ein ADR.
6. Domänenspezifische Sonderfälle werden nicht in den Kernel aufgenommen, solange keine unabhängige allgemeine Notwendigkeit nachgewiesen ist.
7. Technische Darstellungen dürfen die fachliche Bedeutung eines Core-Konzepts nicht bestimmen.
8. Die Abhängigkeitsrichtung vom Core zur Plattform oder Domäne ist unzulässig.

## 8. Erweiterungsverfahren

Ein Vorschlag für ein neues Core-Konzept muss mindestens beantworten:

- Welches allgemeine Problem wird gelöst?
- Welche unabhängigen Plattform- oder Domänenmodelle benötigen das Konzept?
- Warum genügt kein bestehendes Core-Konzept?
- Warum genügt keine Eigenschaft, Beziehung oder Spezialisierung?
- Welche bestehenden Core-Modelle sind betroffen?
- Welche Kompatibilitäts- und Migrationsfolgen entstehen?
- Wie kann das Konzept validiert werden?

Ohne diese Nachweise verbleibt das Konzept in der Plattform- oder Domänenebene.

## 9. Geplante Detailmodelle

Auf Grundlage dieses Kernmodells sind zunächst vorgesehen:

1. `SCHEMA_MODEL.md`;
2. `RELATION_MODEL.md`.

Eigenschaft, Ereignis, Version und Lebenszyklus erhalten eigene Detailmodelle erst dann, wenn ihre Trennung von den bestehenden Objekt-, Schema- und Beziehungsmodellen fachlich erforderlich ist.

## 10. Abhängigkeiten

Dieses Dokument konkretisiert:

- `PROJECT_CONSTITUTION.md`;
- `PROJECT_PRINCIPLES.md`;
- `ADR-0003-architekturebenen-und-kernelgrenze.md`;
- `OBJECT_MODEL.md`;
- `OBJECT_INTERFACE.md`;
- `OBJECT_SERVICE.md`.

## 11. Ergebnis

Der Kernel ist die kleinste stabile Grundlage der Plattform.

Er definiert universelle Objekt-, Struktur-, Beziehungs-, Zustands- und Änderungsbegriffe. Projekte, Identitätsdienste, Benutzer, Konten, Kommunikation und Fachdomänen bauen darauf auf, gehören aber nicht selbst zum Kernel.
