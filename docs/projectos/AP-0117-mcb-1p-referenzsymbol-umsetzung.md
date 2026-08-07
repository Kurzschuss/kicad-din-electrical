# AP-0117 – MCB 1P Referenzsymbol umsetzen und absichern

## Ziel

Der in AP-0116 festgelegte fachliche und grafische Goldstandard wird im KiCad-Referenzsymbol `Z_MCB:MCB` umgesetzt und durch automatisierte Regressionstests abgesichert.

## Umsetzung

Das bisherige Symbol bestand aus einem rechteckigen Grundkörper und zwei passiven Pins. Der Grundkörper bleibt als klarer Symbolrahmen erhalten; innerhalb des Symbols wurde zusätzlich eine eindeutige Schalt-/Schutzgerätegrafik ergänzt.

Die neue Funktionsgrafik besteht aus zwei Linienzügen:

- einem sichtbaren Strompfad zwischen linker und rechter Symbolseite,
- einem zusätzlichen Betätigungs-/Schutzmerkmal am Schaltpfad.

Damit ist das Symbol nicht mehr nur ein generischer Zweipol im Rechteck, sondern als einpoliges Schutz-/Schaltgerät erkennbar.

## Pinvertrag

Der in AP-0116 definierte Pinvertrag wurde unverändert umgesetzt:

- genau zwei Pins,
- Pin `1`, Typ `passive`,
- Pin `2`, Typ `passive`,
- keine zusätzliche elektrische Richtungsvorgabe,
- keine Neutralleiter- oder Schutzleiterpins.

## Herstellerneutralität

Das Symbol bleibt herstellerneutral:

- Herstellerfeld leer,
- Artikelnummer leer,
- keine Logos,
- keine fest eingebrannten Variantendaten wie `B16`,
- `Z_Footprint_Policy = optional` bleibt erhalten.

## Automatisierte Absicherung

Neu ist `tests/test_z_mcb_goldstandard.py`. Der Test prüft:

1. exakt zwei passive Pins,
2. vorhandene Pin- und Namensnummern `1` und `2`,
3. Vorhandensein der neuen Funktionsgrafik,
4. leere Hersteller- und Artikelnummernfelder,
5. weiterhin optionale Footprint-Policy,
6. keine fest eingebrannte Beispielvariante `B16` im Symbol.

Die bestehenden Z_-Qualitätsregeln bleiben zusätzlich bestehen und prüfen Raster, Pinlänge, Linienbreite, Textgröße, Benennung und Footprint-Policy.

## Qualitätsstatus des Referenzprojekts

Die in AP-0115 festgestellte Inkonsistenz wurde bereinigt. Solange `symbol_placed`, `erc_checked` und `opened_in_kicad` noch nicht nachgewiesen sind, führt das Referenzprojekt den Status `Entwurf`.

Damit entspricht die Statuslogik jetzt dem in AP-0116 definierten Ablauf:

`Entwurf → Geprüft → Praxisgetestet`.

## Noch offen

AP-0117 macht noch keinen Praxisnachweis in KiCad. Insbesondere bleiben offen:

- Symbol tatsächlich im Referenzschaltplan platzieren,
- SVG-Vorschau auf die neue Grafik aktualisieren,
- KiCad-Projekt öffnen,
- ERC ausführen und dokumentieren,
- danach den Status anhand der nachgewiesenen Kriterien fortschreiben.

## Definition of Done

- MCB-1P-Symbol besitzt eine erkennbare Schalt-/Schutzgerätegrafik,
- Pinvertrag ist im Symbol umgesetzt,
- Herstellerneutralität bleibt gewahrt,
- Goldstandard-Regressionsprüfung ist vorhanden,
- Referenzprojekt steht bis zum Praxisnachweis korrekt auf `Entwurf`,
- Praxisvalidierung ist als nächstes Arbeitspaket eindeutig abgegrenzt.
