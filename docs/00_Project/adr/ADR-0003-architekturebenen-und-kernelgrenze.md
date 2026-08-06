# ADR-0003: Architekturebenen und Kernelgrenze

**Dokument-ID:** ADR-0003  
**Titel:** Trennung von Meta-, Core-, Plattform- und Domänenebene  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** A  
**Entscheidungsart:** Grundlegende Architekturentscheidung  
**Erstellt:** 6. August 2026  
**Zuletzt geändert:** 6. August 2026

---

## 1. Kontext

Die bisherige Architektur unterscheidet Governance, Objektmodell, Plattformdienste und Fachdomänen. Während der Ausarbeitung wurde deutlich, dass mehrere Begriffe unterschiedlichen Ebenen angehören und deshalb nicht gleichrangig modelliert werden dürfen.

Insbesondere sind Projekt, Workspace, Projektgedächtnis und Bus keine universellen Voraussetzungen jedes Objekts. Sie verwenden den Kernel, gehören aber selbst zur Plattform.

Gleichzeitig muss zwischen der Identität eines Objekts und einer fachlichen oder sicherheitsbezogenen Akteursidentität unterschieden werden.

## 2. Problemstellung

Ohne eine ausdrückliche Schichtung entstehen folgende Risiken:

- Plattformkonzepte werden fälschlich als Kernelbestandteile behandelt;
- Fachdomänen erweitern den Kernel unkontrolliert;
- Identität wird mehrdeutig verwendet;
- Abhängigkeiten verlaufen in beide Richtungen;
- neue Modelle werden ohne klare Zuständigkeit eingeführt;
- der Kernel wächst mit jeder neuen Domäne.

## 3. Entscheidung

Die Architektur wird in vier Ebenen gegliedert:

```text
Meta
  ↓
Core
  ↓
Plattform
  ↓
Domäne
```

Abhängigkeiten verlaufen grundsätzlich nur von unten nach oben in dieser Darstellung: Eine nachgelagerte Ebene darf die vorgelagerte Ebene verwenden, die vorgelagerte Ebene kennt die nachgelagerte Ebene jedoch nicht.

### 3.1 Meta-Ebene

Die Meta-Ebene definiert Regeln, Sprache, Governance und Entscheidungen des Projekts.

Dazu gehören insbesondere:

- Projektverfassung;
- Projektprinzipien;
- Projektglossar;
- Entwicklungsprozess;
- Architecture Decision Records.

### 3.2 Core-Ebene

Die Core-Ebene enthält ausschließlich universelle, domänenunabhängige Konzepte, die zur Beschreibung und Verwaltung beliebiger Objekte erforderlich sind.

Der vorläufige Kern besteht aus:

- Objekt;
- Objektidentität;
- Eigenschaft;
- Schema;
- Beziehung;
- Ereignis;
- Version;
- Lebenszyklus.

Ein neues Core-Konzept darf nur eingeführt werden, wenn nachgewiesen ist, dass es:

- für mehrere unabhängige Plattform- oder Domänenmodelle erforderlich ist;
- nicht als Eigenschaft, Beziehung oder Spezialisierung eines bestehenden Core-Konzepts ausgedrückt werden kann;
- keine Abhängigkeit zu einem konkreten Plattformdienst oder einer Fachdomäne erzeugt.

### 3.3 Plattformebene

Die Plattformebene verwendet den Core und stellt allgemeine Dienste und fachübergreifende Modelle bereit.

Dazu gehören beispielsweise:

- Projekt;
- Workspace;
- Projektgedächtnis;
- Projektbus;
- Benutzer;
- Konten;
- Authentifizierung;
- Autorisierung;
- Rollen;
- Berechtigungen;
- Organisationen;
- Sitzungen;
- Delegation;
- Audit;
- Konfiguration;
- Plugins;
- Suche und Speicherung.

### 3.4 Domänenebene

Die Domänenebene enthält konkrete Fachmodelle, beispielsweise MCB, RCD, SPD, Relais, Schütze, PV oder Wallboxen.

Domänen verwenden Core- und Plattformmodelle. Sie dürfen diese nicht stillschweigend verändern.

## 4. Identitätsbegriffe

Dieses ADR unterscheidet zwei Bedeutungen:

### 4.1 Objektidentität

Jedes Objekt besitzt eine stabile Objektidentität. Sie gehört zum Core und wird in `OBJECT_MODEL.md` und `OBJECT_INTERFACE.md` definiert.

### 4.2 Akteursidentität

Eine Akteursidentität bezeichnet einen menschlichen oder technischen Akteur, dem Handlungen, Verantwortlichkeiten oder Berechtigungen zugeordnet werden können.

Akteursidentitäten und die zugehörigen Dienste gehören zur Plattform und werden durch ADR-0002 sowie nachgeordnete Modelle definiert.

Damit wird nicht jede Akteursidentität zu einem neuen universellen Core-Konzept. Sie ist ein Objekttyp, der die Core-Regeln verwendet.

## 5. Kernelgrenze

Der Kernel darf keine Kenntnisse über folgende Konzepte besitzen:

- Projekte;
- Benutzer;
- Konten;
- Organisationen;
- Rollen;
- Berechtigungen;
- KiCad;
- MCB oder andere Fachgeräte;
- konkrete Speicher- oder Kommunikationstechnologien.

Der Kernel definiert nur die universellen Regeln, auf denen diese Konzepte aufbauen.

## 6. Abhängigkeitsregel

Es gelten folgende Regeln:

1. Meta-Artefakte dürfen alle Ebenen regeln, enthalten aber keine Implementierungslogik.
2. Core-Modelle dürfen weder Plattform- noch Domänenmodelle referenzieren.
3. Plattformmodelle dürfen Core-Modelle referenzieren, aber keine konkrete Fachdomäne voraussetzen.
4. Domänenmodelle dürfen Core und Plattform verwenden.
5. Eine Domäne darf den Core oder die Plattform nicht durch implizite Sonderregeln erweitern.
6. Erfordert eine Domäne eine allgemeine Erweiterung, wird diese zunächst unabhängig von der Domäne spezifiziert und freigegeben.

## 7. Betrachtete Alternativen

### 7.1 Ein gemeinsamer Kernel aus Core und Plattform

Diese Alternative wurde verworfen, weil Projekt-, Benutzer- und Kommunikationsdienste nicht für jedes Objekt erforderlich sind und den Kernel unnötig vergrößern würden.

### 7.2 Identitätsplattform vollständig im Core

Diese Alternative wurde verworfen. Die stabile Objektidentität gehört zum Core. Benutzer-, Geräte-, Dienst- und Akteursidentitäten sind dagegen Plattformobjekte mit zusätzlichen fachlichen und sicherheitsbezogenen Regeln.

### 7.3 Domänenspezifische Erweiterungen des Kernels

Diese Alternative wurde verworfen, weil sie den Kernel von der ersten implementierten Domäne abhängig machen würde.

## 8. Konsequenzen

### Positive Konsequenzen

- kleiner und stabiler Kernel;
- eindeutige Abhängigkeitsrichtung;
- klare Trennung von Objektidentität und Akteursidentität;
- Plattformdienste bleiben domänenunabhängig;
- neue Domänen können denselben Unterbau nutzen;
- Kerneländerungen werden seltener und bewusster.

### Negative Konsequenzen

- zusätzliche Architekturdisziplin erforderlich;
- manche Anforderungen müssen zunächst der richtigen Ebene zugeordnet werden;
- gemeinsame Funktionen können mehrere getrennte Modelle benötigen;
- bestehende Dokument-IDs und Ordnernamen bilden die endgültige Schichtung noch nicht vollständig ab.

## 9. Auswirkungen auf bestehende Dokumente

- `OBJECT_MODEL.md`, `OBJECT_INTERFACE.md` und `OBJECT_SERVICE.md` bleiben Core-Artefakte.
- `ADR-0002` bleibt gültig; seine Identitätsplattform wird der Plattformebene zugeordnet.
- `PROJECT_MODEL.md`, `PROJECT_MEMORY.md` und `PROJECT_BUS.md` werden der Plattformebene zugeordnet.
- `CORE_MODEL.md` wird als Übersicht und Grenzbeschreibung des Kernels angelegt.
- `SCHEMA_MODEL.md` und `RELATION_MODEL.md` werden als nächste Core-Modelle vorgesehen.

## 10. Nicht festgelegt

Dieses ADR legt noch nicht fest:

- endgültige Ordnernamen;
- endgültige Präfixe aller Dokument-IDs;
- konkrete Implementierung der Ebenen;
- konkrete Ereignis-, Eigenschafts-, Versions- oder Lebenszyklusmodelle;
- technische Modulgrenzen.

## 11. Entscheidungsergebnis

Die Architektur verwendet die Ebenen Meta, Core, Plattform und Domäne.

Der Core bleibt klein, domänenunabhängig und frei von Plattformdiensten. Objektidentität gehört zum Core. Menschliche und technische Akteursidentitäten sowie Authentifizierung, Autorisierung, Konten, Rollen und Berechtigungen gehören zur Plattform.
