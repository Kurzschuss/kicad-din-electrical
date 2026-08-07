# Z_MCB-Referenzprojekt

Dieses KiCad-Projekt dokumentiert die erste reproduzierbare Verwendung des herstellerneutralen Symbols `Z_MCB:MCB`.

## Zweck

Das Projekt dient als kontrollierte Ausgangsbasis für den MCB-Goldstandard aus Issue #87. Es zeigt die vorgesehene Bibliotheksanbindung und legt die fachlichen Randbedingungen für einen einfachen einpoligen Endstromkreis fest.

## Referenzaufbau

- Einspeisung: 230 V AC, L/N/PE
- Schutzgerät: einpoliger Leitungsschutzschalter `Z_MCB:MCB`
- neutrale Beispielwerte: Kennlinie B, 16 A
- Abgang: allgemeiner einphasiger Verbraucher
- Footprint-Zuordnung: bewusst optional; Schaltplan- und Schaltschrankdokumentation bleiben getrennt

## Bibliotheken

Die lokale `sym-lib-table` bindet die Projektbibliothek als `Z_MCB` über einen relativen Pfad ein. Damit bleibt das Beispiel nach dem Klonen des Repositorys reproduzierbar.

## Aktueller Status

Das Projekt ist ein vorbereitetes Referenzgerüst. Der Paketstatus bleibt `Entwurf`, solange die reale KiCad-Praxisvalidierung nicht vollständig nachgewiesen ist.

Die Datei `Z_PROJECT_MANIFEST.json` ist die verbindliche maschinenlesbare Statusquelle. Die Felder `symbol_placed`, `erc_checked` und `opened_in_kicad` dürfen nur nach tatsächlich ausgeführter Prüfung auf `true` gesetzt werden.

## Praxisvalidierung in KiCad

Die Prüfung wird bewusst nicht durch Textänderungen im Repository simuliert. Sie muss in einer realen KiCad-Sitzung erfolgen.

1. `Z_MCB_reference.kicad_pro` in KiCad öffnen.
2. Prüfen, dass die lokale Bibliothek `Z_MCB` ohne fehlende Referenzen geladen wird.
3. `Z_MCB:MCB` im Schaltplan platzieren.
4. Pin `1` und Pin `2` in einen einfachen einphasigen Teststrompfad einbinden.
5. Prüfen, dass Referenzpräfix `Q`, Wert `MCB` und die neue Funktionsgrafik korrekt dargestellt werden.
6. Electrical Rules Checker ausführen.
7. Alle für das Referenzprojekt relevanten ERC-Befunde beheben oder nachvollziehbar dokumentieren.
8. Erst danach die entsprechenden Validierungsfelder im Manifest aktualisieren.

## Freigaberegel

- `Entwurf`: Praxisnachweise sind unvollständig.
- `Geprüft`: Goldstandard, automatisierte Prüfungen, aktuelle Vorschau und reale Symbolplatzierung sind nachgewiesen.
- `Praxisgetestet`: Zusätzlich wurden Öffnung in KiCad und ERC-Prüfung vollständig dokumentiert.

Ein Status darf nicht allein aufgrund einer erfolgreichen CI-Prüfung hochgestuft werden.

## Verbindlicher Grundsatz

KiCad ist der Standard. Projektspezifische Erweiterungen sind konsequent mit `Z_` gekennzeichnet. Automatisierte Vorschauen und Tests unterstützen die Freigabe, ersetzen aber keine reale KiCad-Praxisprüfung.
