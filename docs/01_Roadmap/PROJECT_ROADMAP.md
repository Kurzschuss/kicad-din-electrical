# Projekt-Roadmap

Diese Roadmap ordnet die langfristigen Ziele des Projekts. Sie ist ein lebendes Dokument und wird bei neuen Erkenntnissen angepasst.

## Phase A – Projektfundament

- [x] Vision und Manifest dokumentieren
- [x] Projektprinzipien festhalten
- [x] Ideen- und Entscheidungsprotokoll beginnen
- [x] zentrale Dokumentationsnavigation ergänzen
- [x] KiCad-konforme Verzeichnisstruktur herstellen
- [x] Bibliotheksvalidatoren und CI-Prüfungen einführen
- [x] Symbol-, Footprint- und Qualitätsreferenzen erzeugen
- [x] Gerätekatalog, Geräteserien und Taxonomie einführen
- [x] HTML-Referenzen und Symbolvorschauen bereitstellen
- [x] Qualitätshandbuch `docs/00_Project/LIBRARY_GUIDELINES.md` vollständig ausarbeiten

## Phase B – Benutzerdokumentation

- [x] Schnellstart
- [x] ausführliche Installationsanleitung für eine Standard-KiCad-Installation
- [x] Symbol- und Footprintbibliotheken einbinden
- [x] FAQ und Fehlerbehebung
- [x] Testanleitung für Windows, Linux und macOS
- [x] technischen Gerätekatalog erklären
- [ ] weitere verständliche Screenshots ergänzen
- [ ] Beispielprojekte Schritt für Schritt dokumentieren

## Phase C – Verbindliches Paketprinzip

Neue Geräte werden nicht als einzelne Symbole, sondern als möglichst vollständige Bibliothekspakete entwickelt.

Ein vollständiges Paket umfasst – soweit fachlich sinnvoll:

- Symbol
- optionalen Footprint
- Gerätekatalogeintrag
- Geräteserie oder Varianten
- SVG-Vorschau
- HTML-Dokumentation
- Benutzerdokumentation
- Beispielprojekt
- automatisierte Tests
- Qualitätsstatus

Ein Gerät gilt erst dann als abgeschlossen, wenn das Paket vollständig dokumentiert und geprüft ist. Damit sollen viele halbfertige Einträge vermieden und stattdessen schrittweise verlässliche Komponenten aufgebaut werden.

## Phase D – Qualitätsstufen

Für Bibliothekspakete werden folgende Qualitätsstufen eingeführt:

| Status | Bedeutung |
|---|---|
| Entwurf | Struktur vorhanden, Paket noch im Aufbau |
| Geprüft | Symbol, Dokumentation, Katalogdaten und Tests vollständig |
| Praxisgetestet | zusätzlich in einem realen oder realitätsnahen Projekt eingesetzt |

Die Kriterien werden verbindlich im Qualitätshandbuch festgelegt und später auch in HTML-Referenz und Gerätekatalog angezeigt.

## Phase E – Priorisierter Bibliotheksausbau

Die Gerätefamilien werden nacheinander als vollständige Pakete ausgebaut.

1. [ ] MCB – Leitungsschutzschalter
2. [ ] RCD – Fehlerstrom-Schutzeinrichtung
3. [ ] RCBO – kombinierter FI/LS
4. [ ] Hauptschalter
5. [ ] Lasttrennschalter
6. [ ] Schütze
7. [ ] Hilfsschalter
8. [ ] Reihenklemmen
9. [ ] Netzteile
10. [ ] Relais
11. [ ] Motorschutz
12. [ ] Überspannungsschutz
13. [ ] Sicherungen
14. [ ] Transformatoren
15. [ ] Messgeräte
16. [ ] Meldegeräte
17. [ ] SPS-Komponenten

### Erster fachlicher Meilenstein: MCB

Der Leitungsschutzschalter wird als erstes vollständiges Paket umgesetzt:

- [ ] Symbol fachlich und grafisch prüfen
- [ ] sinnvolle Varianten festlegen
- [ ] Footprint-Entscheidung dokumentieren
- [ ] Gerätekatalog und Serien vervollständigen
- [ ] SVG- und HTML-Dokumentation ergänzen
- [ ] Benutzeranleitung erstellen
- [ ] Beispielprojekt anlegen
- [ ] Tests ergänzen
- [ ] Qualitätsstatus vergeben

Erst nach Abschluss dieses Pakets folgt RCD, danach RCBO und die weiteren Gerätefamilien.

## Phase F – Beispielprojekte und Vorlagen

Beispielprojekte sollen reale Planungsaufgaben zeigen und keine künstlichen Demonstrationsschaltungen sein.

### Einsteigerbeispiele

- [ ] erstes Symbol
- [ ] erstes Gerät
- [ ] erste Verbindung
- [ ] Beschriftung und Referenzkennzeichen
- [ ] ERC ausführen und Ergebnisse einordnen

### Installation

- [ ] Lichtschaltung
- [ ] Steckdosenstromkreis
- [ ] Wechselschaltung
- [ ] Kreuzschaltung
- [ ] Tasterschaltung

### Unterverteilung und Energieverteilung

- [ ] kleine Unterverteilung
- [ ] Unterverteilung mit FI/LS
- [ ] Unterverteilung mit mehreren RCD-Gruppen
- [ ] Reservefelder und Erweiterungsplanung
- [ ] Garagenverteilung
- [ ] Gartenverteilung
- [ ] Zähleranlage Einfamilienhaus
- [ ] Baustromverteiler

### Schaltschrank und Steuerung

- [ ] Schützschaltung
- [ ] Motorstarter
- [ ] Zeitrelais
- [ ] Netzteil
- [ ] SPS-Grundaufbau
- [ ] Klemmenplan

### Zukunftsprojekte

- [ ] Wärmepumpe
- [ ] Wallbox
- [ ] PV-Vorbereitung
- [ ] Netzwerkverteiler
- [ ] Kleinsteuerung

Jedes Beispiel erhält ein eigenes `README.md` mit Ziel, Voraussetzungen, Arbeitsschritten, verwendeten Bibliotheken und Hinweisen für Anfänger.

## Phase G – Referenz und Wissensplattform

- [x] Symbolkatalog
- [x] Footprintkatalog
- [x] durchsuchbare HTML-Übersicht
- [x] technischer Gerätekatalog
- [x] Symbolvorschauen
- [ ] Normen- und Symbolreferenz
- [ ] Beschreibungen und typische Einsatzgebiete je Symbol
- [ ] dokumentierte Symbol-zu-Footprint-Zuordnungen
- [ ] Beispielschaltungen je Gerätefamilie
- [ ] Qualitätsstatus in HTML und Gerätekatalog
- [ ] Footprintvorschauen

## Phase H – Kompatibilität und Veröffentlichung

- [ ] Kompatibilitätsmatrix für unterstützte KiCad-Versionen
- [ ] Statusmatrix für Symbol, Footprint, Generator, HTML und Tests
- [ ] GitHub Pages einrichten
- [ ] Dokumentation online veröffentlichen
- [ ] Downloadbereich
- [ ] Release-Automatisierung
- [ ] automatische Aktualisierung durch GitHub Actions

## Phase I – Langfristige Werkzeuge

- [ ] Komponenten- und Wissensdatenbank ausbauen
- [ ] optionaler KiCad-Installationsassistent oder Plugin
- [ ] Projektassistent für typische Anlagen
- [ ] automatische Material- und Stücklisten aus dem Gerätekatalog
- [ ] Hersteller- und Datenblattlisten

## Phase J – Ausbildung

- [ ] Übungen und Beispielaufgaben
- [ ] Musterlösungen
- [ ] Arbeitsblätter
- [ ] Tutorials für Einsteiger
- [ ] Material für Schulen und Ausbildungsstätten

## Geplante Meilensteine

- **0.5 – Projektfundament**
- **0.6 – Benutzerdokumentation**
- **0.7 – Bibliotheksreferenz und Gerätekatalog**
- **0.8 – Beispielprojekte und erstes vollständiges MCB-Paket**
- **0.9 – weitere vollständige Gerätepakete und Website**
- **1.0 – erste stabile Veröffentlichung**
