# AP-0074 – Automatisierte KiCad-Qualitätsgrenzen und Freigabeentscheidung

## Ziel

Persistierte KiCad-Validierungsläufe werden anhand einer expliziten Qualitätsrichtlinie deterministisch bewertet. Das Ergebnis ist eine strukturierte Freigabeentscheidung und ersetzt keine fachliche oder rechtliche Prüfung.

## Komponenten

- `KiCadQualityPolicy`
- `KiCadQualityGateService`
- `KiCadQualityGateResult`
- `KiCadQualityGateFinding`
- `KiCadReleaseDecision`

## Entscheidungen

- `APPROVED`: Alle konfigurierten Grenzen sind eingehalten.
- `REJECTED`: Mindestens eine Qualitätsgrenze ist verletzt.
- `INSUFFICIENT_DATA`: Es liegen weniger als die geforderten Validierungsläufe vor.

## Unterstützte Qualitätsgrenzen

- Mindestanzahl gespeicherter Läufe
- optional erforderlicher gültiger letzter Lauf
- maximale Fehlerzahl im jüngsten Lauf
- optionale maximale Warnungszahl
- optionale maximale Zahl dokumentierter KiCad-Ausnahmen
- optionale Mindestgültigkeitsquote über die Historie
- verbotene Finding-Codes im jüngsten Lauf

Die Standardrichtlinie verlangt mindestens einen Lauf, einen gültigen jüngsten Lauf und null Fehler. Warnungen und dokumentierte Ausnahmen sind standardmäßig nicht begrenzt.

## KiCad-Standard zuerst

Dokumentierte Ausnahmen bleiben zulässig, solange die Richtlinie sie nicht begrenzt oder verbietet. Damit werden begründete Sonderfälle sichtbar gehalten, ohne sie pauschal als Fehler zu behandeln.

## Fehlerkennungen

- `ERR-KICAD-0063`: Ungültige Mindestanzahl von Läufen
- `ERR-KICAD-0064`: Negative maximale Fehlerzahl
- `ERR-KICAD-0065`: Negative Qualitätsgrenze
- `ERR-KICAD-0066`: Ungültige Mindestgültigkeitsquote
- `ERR-KICAD-0067`: Unzureichende Datenbasis
- `ERR-KICAD-0068`: Jüngster Lauf ist ungültig
- `ERR-KICAD-0069`: Fehlergrenze überschritten
- `ERR-KICAD-0070`: Warnungsgrenze überschritten
- `ERR-KICAD-0071`: Ausnahmegrenze überschritten
- `ERR-KICAD-0072`: Mindestgültigkeitsquote unterschritten
- `ERR-KICAD-0073`: Verbotener Finding-Code vorhanden

## Grenzen

AP-0074 erzeugt eine technische Freigabeempfehlung. Eine tatsächliche Projekt-, Produkt- oder Normfreigabe benötigt weiterhin die dafür zuständige Rolle und gegebenenfalls zusätzliche Prüfungen.
