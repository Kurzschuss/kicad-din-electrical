# QElectroTech-Adapter für ProjectOS

## Ziel

QElectroTech (QET) wird als möglicher zweiter Ausgabeadapter neben KiCad untersucht. ProjectOS bleibt die Single Source of Truth; QET-Dateien werden aus ProjectOS-Objekten erzeugt und nicht als führende Datenquelle verwendet.

## Technischer Befund

QElectroTech speichert elektrische Elemente als `.elmt`-Dateien im XML-Format. Auch QET-Projekte verwenden XML. QET unterscheidet unter anderem eine gemeinsame Sammlung, eine benutzereigene Sammlung und eine projektbezogene Sammlung.

Die dokumentierte Elementstruktur enthält unter anderem:

- `definition` als Wurzelelement,
- sprachabhängige Namen unter `names`,
- eine grafische `description`,
- grafische Primitive wie Linien, Rechtecke, Kreise und Polygone,
- `terminal`-Elemente als elektrische Anschlusspunkte,
- optionale editierbare Textfelder.

Damit ist eine automatische Ableitung aus dem ProjectOS-Geräte- und Anschlussmodell grundsätzlich möglich.

## Architekturregel

```text
ProjectOS-Geräteobjekt
        |
        +-- KiCad-Adapter -> .kicad_sym
        |
        +-- QElectroTech-Adapter -> .elmt
        |
        +-- Dokumentation / Katalog / 3D
```

KiCad- und QET-Dateien sind Zielartefakte. Änderungen an einem Zielartefakt dürfen nicht stillschweigend die fachliche ProjectOS-Quelle überschreiben.

## MCB-1P-Mapping

Für den aktuellen Goldstandard `MCB 1P` gilt als erster Mapping-Spike:

| ProjectOS | QElectroTech |
|---|---|
| Gerätefamilie `MCB` | Elementname `MCB 1P` |
| Anschluss `1` | erstes `terminal` |
| Anschluss `2` | zweites `terminal` |
| zwei passive KiCad-Pins | zwei QET-Anschlusspunkte |
| herstellerneutral | keine Herstellerdaten im Element |
| Funktionsgrafik | Linien/Polygone in `description` |

QET kennt dabei nicht notwendigerweise dieselbe Pin-Elektriktyp-Semantik wie KiCad. Der ProjectOS-KiCad-Pinvertrag bleibt daher ein eigener Zielvertrag; QET erhält die fachliche Anschlussidentität aus ProjectOS.

## Lizenz

Die QElectroTech-Anwendung steht unter GNU/GPL. Die offizielle Elementsammlung ist ein separates Artefakt und darf nicht automatisch als ProjectOS-eigene Symbolquelle behandelt werden. Für ProjectOS erzeugte QET-Elemente sollen aus unseren eigenen fachlichen Daten und eigenen Grafiken generiert werden.

## Verifikation

Vor einer Freigabe des Adapters sind mindestens erforderlich:

1. erzeugte `.elmt`-Datei ist wohlgeformtes XML,
2. QElectroTech 0.100 kann die Datei öffnen,
3. beide MCB-Anschlüsse sind im Elementeditor als Terminals vorhanden,
4. Platzierung und Verdrahtung im QET-Schaltplan funktionieren,
5. Rotation und Spiegelung verhalten sich erwartungsgemäß,
6. keine Herstellerdaten werden in das neutrale Element eingebrannt.

## Status

`experimentell`

Die Machbarkeit ist bestätigt; eine echte QET-0.100-Praxisvalidierung steht noch aus.

## Quellen

- Offizielle QElectroTech-Dokumentation: Dateiformate für Projekte und Elemente sind XML.
- Offizielle QElectroTech-Dokumentation: XML-Struktur der Elemente mit `definition`, `description` und `terminal`.
- Offizielle QElectroTech-Seite: GNU/GPL-Lizenz.
- Offizielle QElectroTech-Elementsammlung auf GitHub.
