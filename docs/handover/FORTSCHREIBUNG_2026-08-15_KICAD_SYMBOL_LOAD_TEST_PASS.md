# Fortschreibung 2026-08-15 – lokaler KiCad-Symbol-Ladetest PASS

## Ergebnis

Der echte lokale KiCad-Ladetest wurde unter Windows erfolgreich mit einer lokal installierten KiCad-CLI ausgeführt.

Automatischer Gesamtstatus: **PASS**.

Geprüft wurden:

- `Z_RCBO_1P_N.kicad_sym`: 1 logisches Symbol, 1/1 SVG-Rendering erfolgreich;
- `Z_I_ElectricalComponents.kicad_sym`: 52 logische Top-Level-Symbole;
- KiCad exportiert daraus 55 Unit-SVGs, weil `Contactor_3P_1NO_1NC` mehrere Units besitzt;
- Re-Save-Test über `kicad-cli sym upgrade --force` für RCBO und Z_I erfolgreich;
- erneuter Export der von KiCad neu gespeicherten Bibliothekskopien erfolgreich;
- `Contactor_3P_1NO_1NC`: 4/4 Units strukturell vorhanden.

## Gefundene und behobene Probleme

Während des echten Parser-Tests wurden zwei Test-/Formatprobleme entdeckt und im Branch `agent/kicad-local-symbol-load-test` korrigiert:

1. PowerShell-Parserfehler im Testskript durch `"$Label:"`; korrigiert auf `"${Label}:"`.
2. `Z_RCBO_1P_N.kicad_sym` enthielt freie `; ...`-Kommentarzeilen zwischen KiCad-S-Expressions. Der Repository-Validator hatte diese nicht beanstandet, der echte KiCad-Parser verweigerte jedoch das Laden. Die Kommentarzeilen wurden entfernt; Geometrie, Pins und Eigenschaften blieben unverändert.

Zusätzlich wurde die erwartete Z_I-Renderingzahl korrigiert: 52 logische Symbole ergeben 55 SVG-Dateien wegen der Mehrfacheinheiten des Schützes.

## Visuelle Diagnoseansicht

Die erzeugte `VISUAL_CHECK.html` ist eine Diagnoseansicht. Der CLI-Export wurde bewusst mit `--include-hidden-pins` und `--include-hidden-fields` erzeugt. Deshalb erscheinen dort zusätzliche kleine Pin-/Feldtexte, die in einer normalen KiCad-Schaltplanansicht verborgen sein können.

Die Diagnoseansicht ist für Parser-, Pin- und Vollständigkeitsprüfung geeignet, aber nicht allein maßgeblich für die endgültige optische Beurteilung.

## Noch manuell offen

Vor Abschluss des Prüfbranches sind noch folgende echte KiCad-GUI-Prüfungen vorgesehen:

1. RCBO im Schaltplan platzieren und Fangpunkte sowie sichtbare Klemmenbezeichnungen `1 / 3 N / 2 / 4 N` prüfen;
2. `Contactor_3P_1NO_1NC` im Symbolwähler mit Units A–D einzeln anzeigen;
3. Potential-/Pfeilsymbole auf Fangpunkte prüfen;
4. bei allen 52 Z_I-Symbolen auf Textrotation, abgeschnittene Texte und unplausible Pinpositionen achten.

## Branch

```text
agent/kicad-local-symbol-load-test
```

Der Branch enthält zugleich die für echte KiCad-Kompatibilität notwendige RCBO-Bereinigung und den reproduzierbaren Windows-Testlauf.
