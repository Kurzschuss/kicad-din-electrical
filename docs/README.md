# Dokumentation

Diese Dokumentation wird schrittweise ausgebaut und richtet sich sowohl an KiCad-Einsteiger als auch an Mitwirkende des Projekts.

## Benutzeranleitungen

- [Schnellstart: erstes Symbol verwenden](02_User/QUICKSTART.md)
- [Bibliotheken in KiCad einbinden](02_User/INSTALL.md)
- [Technischen Gerätekatalog verwenden](02_User/DEVICE_CATALOG.md)
- [Lokale Tests ausführen](02_User/TESTING.md)
- [Häufig gestellte Fragen](02_User/FAQ.md)
- [Glossar](02_User/GLOSSARY.md)

## Mitwirken und Entwicklung

- [Am Projekt mitwirken](../CONTRIBUTING.md)
- [Entwicklerleitfaden](03_Developer/DEVELOPER.md)
- [Bibliotheksreferenz automatisch erzeugen](03_Developer/REFERENCE_GENERATOR.md)
- [Bibliotheks-Validator](03_Developer/LIBRARY_VALIDATOR.md)
- [Automatischer Qualitätsbericht](03_Developer/QUALITY_REPORT.md)
- [HTML-Bibliotheksreferenz erzeugen](03_Developer/HTML_REFERENCE.md)
- [Automatische Symbolvorschauen](03_Developer/SYMBOL_PREVIEWS.md)
- [Gerätekatalog](03_Developer/DEVICE_CATALOG.md)
- [Geräteserien und Varianten](03_Developer/DEVICE_SERIES.md)
- [Gerätefamilien und Funktionsgruppen](03_Developer/DEVICE_TAXONOMY.md)
- [Z_Cockpit erzeugen und testen](03_Developer/Z_COCKPIT.md)
- [Z_Cockpit Benutzerverwaltung](03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md)
- [Z_Cockpit Berechtigungen und Whitelists](03_Developer/Z_COCKPIT_BERECHTIGUNGEN.md)
- [Z_Cockpit Issue- und Fehlermeldung](03_Developer/Z_COCKPIT_FEHLERMELDUNG.md)
- [Z_Cockpit 3D-Vorschauen und Modellabdeckung](03_Developer/Z_COCKPIT_3D_VORSCHAUEN.md)
- [Z_Cockpit direkte KiCad-Editoraufrufe](03_Developer/Z_COCKPIT_KICAD_EDITORAUFRUFE.md)
- [ProjectOS-Ausbau: Benutzer, Whitelist und Fehlermeldungen](projectos/Z_COCKPIT_AUSBAU_BENUTZER_WHITELIST_ISSUES.md)

## Bibliotheksreferenz und Werkzeuge

- [Durchsuchbare HTML-Übersicht](site/index.html)
- [Technischer Gerätekatalog](site/devices.html)
- [Durchsuchbare Symbolvorschau-Galerie](site/symbol-previews/index.html)
- [Z_Cockpit-Tabellenprototyp](site/z-cockpit-prototyp.html)
- [Symbolbibliotheken](04_Reference/SYMBOL_INDEX.md)
- [Footprintbibliotheken](04_Reference/FOOTPRINT_INDEX.md)
- [Bibliotheks-Qualitätsbericht](04_Reference/QUALITY_REPORT.md)
- [Z_DIN_Control](04_Reference/Z_DIN_Control.md)
- [Z_DIN_Module_18mm](04_Reference/Z_DIN_Module_18mm.md)

## Projektgrundlagen

- [Vision](00_Project/VISION.md)
- [Manifest](00_Project/MANIFESTO.md)
- [Projektprinzipien](00_Project/PRINCIPLES.md)
- [Qualitätshandbuch für Bibliothekspakete](00_Project/LIBRARY_GUIDELINES.md)
- [EE-WERKZEUG-0001: Tabellenoberfläche für Z_Cockpit](00_Project/entwurfsentscheidungen/EE-WERKZEUG-0001_Z_Cockpit_Tabellenoberflaeche.md)

## Planung und Nachvollziehbarkeit

- [Projekt-Roadmap](01_Roadmap/PROJECT_ROADMAP.md)
- [Suite- und Z_Cockpit-Konzept](01_Roadmap/SUITE_AND_COCKPIT_CONCEPT.md)
- [Ideensammlung](01_Roadmap/IDEAS.md)
- [Entscheidungsprotokoll](01_Roadmap/DECISIONS.md)
- [Projektprotokoll](01_Roadmap/PROJECT_LOG.md)

## Aktueller ProjectOS-Ausbau

Der festgelegte dreistufige Z_Cockpit-Ausbau ist vollständig umgesetzt:

- Benutzerverwaltung;
- Whitelist- und Berechtigungsverwaltung;
- Issue- und Fehlermeldungsworkflow.

Zusätzlich sind die **3D-Vorschauen und die Modellabdeckung** angebunden. Das Cockpit unterscheidet echte KiCad-3D-Modelle von technischen Hüllkörperansichten aus vorhandener `F.Fab`-Geometrie. Hüllkörper werden nicht als echte Modelle gezählt und fehlende Produktgeometrien werden nicht erfunden.

Die **direkten KiCad-Editoraufrufe** sind ebenfalls angebunden. Unter Windows registriert der Cockpit-Starter das lokale `kicad-z:`-Protokoll im aktuellen Benutzerprofil. Zugeordnete Footprints können direkt im Footprint Editor geöffnet werden; beim Symbolaufruf wird der KiCad Symbol Editor geöffnet und die geprüfte technische Symbolreferenz in die Zwischenablage gelegt.

Der Bereich `Fehler melden` erzeugt einen lokalen, überprüfbaren Markdown-Bericht und kann bei zulässigem Repositoryzustand das offizielle GitHub-Issue-Formular vorbereiten. Das Issue wird nicht automatisch abgesendet.

ProjectOS-Benutzer-Whitelist und Repository-Entwickler-Whitelist bleiben getrennte Sicherheitsquellen. Benutzer-/Berechtigungsbestände, Tokens, Schlüssel und Zugangsdaten werden nicht automatisch in Fehlerberichte übernommen.

Im zentralen Projektmodell ist derzeit keine normale `planned`- oder `in_progress`-Aufgabe offen. Als technischer Folgepunkt bleibt die Persistenzanbindung der Laufzeitdiagnosen. Der GitHub-Ruleset bleibt separat blockiert und benötigt eine eigene Freigabe.

Weitere ältere Roadmap-Punkte werden in den jeweiligen Fach- und Übergabedokumenten fortgeführt.

Die Dokumentation soll besonders für KiCad-Einsteiger verständlich sein und zugleich die technischen Entscheidungen des Projekts dauerhaft nachvollziehbar machen.
