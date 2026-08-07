# ADR-0008 – Python als ProjectOS-Kernruntime

**Status:** Angenommen  
**Datum:** 2026-08-06  
**Bezug:** AP-0021

## Kontext

Das bestehende Repository verwendet bereits Python und pytest für Werkzeuge, Qualitätsprüfungen und automatisierte Tests. Eine zweite Programmiersprache würde Build, Wartung und Offline-Betrieb unnötig verkomplizieren.

## Entscheidung

Die erste ausführbare ProjectOS-Kernimplementierung verwendet Python.

Verbindlich sind:

- Kompatibilität mit der im Repository vorhandenen Python-Testumgebung,
- pytest als Testframework,
- Standardbibliothek als bevorzugte Grundlage,
- typisierte und dokumentierte öffentliche Schnittstellen,
- unveränderliche Kernwertobjekte, soweit fachlich sinnvoll,
- keine zwingende Netzwerkabhängigkeit,
- keine neue Paket- oder Build-Toolchain ohne gesonderte ADR.

## Konsequenzen

### Vorteile

- direkte Integration in die bestehende Toolchain,
- vorhandene Entwickler- und CI-Abläufe bleiben nutzbar,
- schneller Start der Implementierung,
- geringe zusätzliche Abhängigkeiten,
- gute Eignung für KiCad-nahe Werkzeuge, Validierung und Simulation.

### Nachteile

- Laufzeitfehler müssen durch Typprüfungen und Tests konsequent begrenzt werden,
- leistungsintensive Teilbereiche benötigen später eventuell optimierte Adapter.

## Abgrenzung

Diese Entscheidung legt nicht fest:

- welches UI-Framework verwendet wird,
- welcher eingebettete Datenspeicher eingesetzt wird,
- ob einzelne spätere Adapter in anderen Sprachen implementiert werden dürfen.
