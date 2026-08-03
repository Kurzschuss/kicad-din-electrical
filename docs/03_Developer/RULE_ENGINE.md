# Datengetriebene Qualitätsprüfung

Die Qualitätsprüfung trennt fachliche Regeln, technische Prüftypen und Berichte. **KiCad ist der Standard.** Eigene Ergänzungen und bewusst zugelassene Abweichungen werden ausschließlich über Regeln mit `Z_`-Bezug und passenden Regel-IDs beschrieben.

## Verzeichnisse

```text
rules/
├── kicad/       # nachvollziehbare offizielle KiCad-Regeln
├── z/           # projektspezifische Z_-Erweiterungen
├── project/     # Repository-, Generator- und Dokumentationsregeln
├── profiles/    # Aktivierung und CI-Wirkung
├── exceptions/  # begründete, sichtbare Ausnahmen
└── schema/      # formale JSON-Schemata
```

## Regel-IDs

- `KICAD-SYM-...` und `KICAD-FP-...`: offizielle KiCad-Vorgaben
- `ZSYM-...`, `ZFP-...`, `Z3D-...`: eigene dokumentierte Erweiterungen
- `PROJECT-...`: Repository-, Dokumentations- und Generatorregeln

Eine `Z_`-Regel darf eine offizielle KiCad-Regel nicht umbenennen oder stillschweigend ersetzen. Abweichungen müssen im Ergebnis sichtbar bleiben.

## Kontrollierte Prüftypen

Regeldateien enthalten keinen ausführbaren Python-, JavaScript- oder Shell-Code. Das Feld `check.type` wählt ausschließlich einen registrierten und getesteten Prüftyp. Unbekannte Prüftypen führen beim Laden zu einem Fehler.

Aktuell unterstützt:

- `field_prefix`: prüft einen verbindlichen Präfix, insbesondere `Z_`
- `field_equals`: prüft einen erwarteten Feldwert

Neue Prüftypen werden zuerst in der Registry implementiert und getestet. Erst danach dürfen Regeldateien sie verwenden.

## Ergebnisvertrag

Jedes Ergebnis enthält mindestens:

- Element
- Regel-ID und Titel
- Schweregrad
- Qualitätsstatus
- Sollwert
- Istwert
- verständliche Erklärung
- konkrete Empfehlung
- optionale Ausnahme-ID

Zulässige Qualitätsstatus:

- `kicad_conform`
- `z_conform`
- `needs_rework`
- `temporarily_accepted`

## Profile

Profile bestimmen, welche Regeln ausgeführt werden und wann CI fehlschlägt. Ergebnisse dürfen durch Profile weder ausgeblendet noch inhaltlich verändert werden.

- `development`: schrittweiser Ausbau; sichtbare Warnungen
- `compatibility`: Schwerpunkt auf KiCad-Kompatibilität
- `strict`: alle aktivierten Regeln streng auswerten
- `release`: Freigabekriterien für geprüfte Pakete

## Ausnahmen

Ausnahmen sind versionierte Daten, kein Testcode. Jede Ausnahme benötigt:

- eindeutige ID
- betroffene Regel
- Element oder Muster
- zulässigen Status
- fachliche Begründung
- Referenz auf Richtlinie, Issue oder PR
- Ablaufdatum oder verbindlichen Prüftermin

Nicht dokumentierte Abweichungen erhalten immer `needs_rework`.

## Formale Schemata

Die Dateien unter `rules/schema/` definieren die zulässigen Felder und Werte für Regeln, Profile und Ausnahmen. Die Python-Engine prüft zusätzlich semantische Bedingungen wie eindeutige Regel-IDs und bekannte Prüftypen.

## KiCad-Symboladapter

`tools/quality/kicad_symbol_adapter.py` extrahiert einen kleinen, auditierten Satz von Fakten direkt aus `.kicad_sym`-Dateien. Der Adapter führt keine Dateiinhalte aus und ersetzt nicht den KiCad-Parser.

Projektspezifische Metadaten werden ebenfalls ausdrücklich mit `Z_` gekennzeichnet. Die Footprint-Entscheidung wird als versteckte Eigenschaft `Z_Footprint_Policy` mit einem der Werte `required`, `optional` oder `none` gespeichert. Ein leeres Standardfeld `Footprint` ist bei der Policy `optional` oder `none` zulässig und wird nicht mit einer fehlenden Policy verwechselt.

## Referenzintegration

Das MCB-1P-Paket aus Issue #87 ist der erste vollständige Integrationsfall. `Z_MCB:MCB` verwendet `Z_Footprint_Policy=optional` und erfüllt den derzeit implementierten Regelsatz `ZSYM-001` bis `ZSYM-006` vollständig mit dem Status `z_conform`.

Die Ergebnisse werden anschließend in Issue #89 als Fortschritts- und Qualitätsdaten übernommen.
