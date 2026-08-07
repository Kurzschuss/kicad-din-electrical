# AP-0115 – MCB 1P Bestandsaufnahme und fachlich-grafische Validierung

## Ziel

Der vorhandene Stand des MCB-1P-Referenzpakets wird gegen das Sprintziel aus Issue #87 geprüft. Dieses Arbeitspaket verändert noch nicht das Referenzsymbol, sondern schafft einen belastbaren Ausgangspunkt für die nachfolgenden Korrekturen.

## Vorhandene Artefakte

Für den MCB-1P-Goldstandard sind bereits wesentliche Bausteine vorhanden:

- KiCad-Symbolbibliothek `symbols/Z_MCB.kicad_sym` mit Symbol `Z_MCB:MCB`,
- SVG-Vorschau unter `docs/site/symbol-previews/Z_MCB/MCB.svg`,
- Referenzprojekt `projects/Z_MCB_reference`,
- Projektmanifest `projects/Z_MCB_reference/Z_PROJECT_MANIFEST.json`,
- Qualitätsstatus `docs/04_Reference/Z_MCB_QUALITY_STATUS.md`,
- Dokumentation und Indexeinträge für Symbol, Katalog und Geräteansicht.

## Technischer Symbolstand

Das vorhandene Symbol besitzt:

- Referenzpräfix `Q`,
- Wert `MCB`,
- zwei passive Pins mit den Nummern `1` und `2`,
- eine explizite `Z_Footprint_Policy` mit dem Wert `optional`,
- 100-mil-Pinlänge,
- 100-mil-Anschlussraster,
- dokumentierte Standardlinien- und Textgrößen.

Die vorhandene Z_-Qualitätsprüfung bewertet alle derzeit implementierten Symbolregeln `ZSYM-001` bis `ZSYM-006` als `z_conform`.

## Fachlich-grafische Einordnung

Das Symbol ist technisch konsistent und maschinenprüfbar, stellt derzeit grafisch jedoch nur einen rechteckigen Grundkörper mit zwei Anschlüssen dar. Für den geplanten Goldstandard muss deshalb im nächsten Schritt ausdrücklich geprüft werden, ob die Darstellung als fachlich eindeutiges MCB-Symbol für Elektroplanung und KiCad-Nutzung ausreicht oder ob eine normnähere Schutzgerätegrafik erforderlich ist.

Die Pinbelegung `1`/`2` ist als einfacher einpoliger Strompfad plausibel, aber noch nicht als verbindlicher Schutzgerätevertrag des Goldstandards dokumentiert. Diese Festlegung muss vor weiteren Polvarianten erfolgen.

## Referenzprojekt

Das Referenzprojekt ist als reproduzierbares Gerüst vorhanden und verwendet:

- 230 V AC,
- einpoligen MCB,
- neutrales Beispiel B16,
- optionale Footprint-Zuordnung.

Das Projektmanifest zeigt jedoch noch offene Praxisvalidierung:

- `symbol_placed: false`,
- `erc_checked: false`,
- `opened_in_kicad: false`.

Damit ist das Referenzprojekt noch kein vollständig praktisch validierter Goldstandard.

## Festgestellte Statusabweichung

Issue #87 verlangt den Qualitätsstatus zunächst `Entwurf` und erst nach Erfüllung aller Goldstandard-Kriterien `Geprüft`.

Das aktuelle Projektmanifest führt bereits `quality_level: "Geprüft"`, obwohl Platzierung, ERC und Öffnung in KiCad noch nicht bestätigt sind. Diese Statuslogik ist für Sprint 006 zu bereinigen oder ausdrücklich gegen das bestehende Qualitätsstufenmodell abzugrenzen.

## Ergebnis

Der MCB-1P-Stand ist eine gute technische Ausgangsbasis, aber noch nicht als Goldstandard abgeschlossen. Für die nächsten Arbeitspakete werden folgende Punkte verbindlich:

1. fachliche und grafische Symboldefinition des MCB 1P festlegen,
2. Pinvertrag für den einpoligen MCB dokumentieren,
3. Qualitätsstatus und Freigabekriterien eindeutig vereinheitlichen,
4. Referenzprojekt mit echter Symbolplatzierung und ERC-Nachweis vervollständigen,
5. danach Dokumentation, Katalog, Vorschau und automatisierte Tests auf den finalen Goldstandard ausrichten.

## Definition of Done

- vorhandene MCB-Artefakte sind erfasst,
- Z_-Qualitätsstatus ist bewertet,
- offene Praxisvalidierungen sind dokumentiert,
- Statusabweichung zwischen Issue #87 und Projektmanifest ist erkannt,
- nächste fachliche Entscheidung ist eindeutig abgegrenzt.
