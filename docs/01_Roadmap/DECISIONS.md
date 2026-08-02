# Entscheidungsprotokoll

Dieses Dokument hält wichtige technische und organisatorische Entscheidungen mit Begründung fest.

## 2026-08-02 – Projektfokus

**Entscheidung:** Das Projekt entwickelt keine allgemeine Elektronikbibliothek.

**Begründung:** Der Schwerpunkt liegt bewusst auf Gebäudeinstallation, Energieverteilung, Zähleranlagen, Verteilungen, Schaltschrankbau und Steuerungstechnik.

## 2026-08-02 – Projektziel

**Entscheidung:** Das Projekt wird langfristig als Plattform aus Bibliotheken, Dokumentation, Beispielen, Vorlagen, Referenz und Werkzeugen entwickelt.

**Begründung:** Anwender benötigen nicht nur Symbole, sondern einen nachvollziehbaren Weg von der Installation bis zum fertigen Plan.

## 2026-08-02 – Sprache der Projektidentität

**Entscheidung:** Der zentrale Projekttitel und die grundlegende Zielsetzung werden zunächst auf Deutsch formuliert.

**Formulierung:**

> Professionelle Open-Source-Bibliotheken für die Elektroplanung mit KiCad
>
> Aufbau der umfassendsten frei verfügbaren Bibliothek für Gebäudeinstallation, Energieverteilung und Schaltschrankbau.

## 2026-08-02 – Persönlicher Hintergrund

**Entscheidung:** Hinweise auf den persönlichen oder beruflichen Hintergrund des Initiators werden vorerst nicht in die Projektbeschreibung aufgenommen.

**Begründung:** Die Projektqualität und Zielsetzung sollen zunächst für sich sprechen. Eine spätere Ergänzung bleibt möglich.

## 2026-08-02 – Präfix `Z_`

**Entscheidung:** Projektinterne Symbolbibliotheken, Footprintbibliotheken und zugehörige Dateien verwenden das Präfix `Z_`.

**Begründung:** Das Präfix bündelt die Einträge in KiCad alphabetisch und reduziert Namenskollisionen mit anderen Bibliotheken.

## 2026-08-02 – Symbolbibliotheksstruktur

**Entscheidung:** `.kicad_sym`-Dateien liegen unter `symbols/DIN_Electrical_Symbols/`.

**Begründung:** Die gemeinsame Ablage erleichtert Übersicht, Installation und automatisierte Prüfungen.

## 2026-08-02 – Footprintbibliotheksstruktur

**Entscheidung:** Footprints liegen direkt in `.pretty`-Bibliotheken unter `footprints/`. Eine `.pretty`-Bibliothek darf mehrere `.kicad_mod`-Dateien enthalten.

**Begründung:** Eine Symbolbibliothek kann mehrere Symbole enthalten; entsprechend muss eine zugehörige Footprintbibliothek mehrere Footprints aufnehmen können.

## 2026-08-02 – Footprint-IDs

**Entscheidung:** Qualifizierte Footprint-IDs verwenden das Format `<Bibliothek>:<Footprint>`. Beide Namen müssen nicht identisch sein.

**Begründung:** Mehrere unterschiedlich benannte Footprints können in derselben `.pretty`-Bibliothek liegen.

## 2026-08-02 – Dokumentation

**Entscheidung:** Dokumentation besitzt denselben Stellenwert wie Bibliotheksdateien.

**Begründung:** Die Bibliotheken sollen auch von KiCad-Einsteigern installiert, verstanden und verwendet werden können.

## 2026-08-02 – Qualitätssicherung

**Entscheidung:** Struktur, Namen, interne Bezeichner, Referenzen und Dokumentationsbeispiele werden soweit sinnvoll durch CI geprüft.

**Begründung:** Automatische Tests verhindern, dass spätere Änderungen die festgelegte Struktur unbemerkt beschädigen.

## 2026-08-02 – Umgang mit Ideen

**Entscheidung:** Neue Ideen werden zuerst dokumentiert und nicht verworfen, nur weil sie kurzfristig nicht umgesetzt werden.

**Begründung:** Dadurch bleibt die langfristige Vision erhalten, ohne die aktuelle Entwicklung zu überladen.