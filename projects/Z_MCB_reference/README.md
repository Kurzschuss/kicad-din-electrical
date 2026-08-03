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

## Status

Das Projekt ist zunächst ein validiertes Referenzgerüst. Der Paketstatus bleibt `Geprüft`, bis der Schaltplan in KiCad geöffnet, das Symbol tatsächlich platziert, ERC geprüft und das Ergebnis dokumentiert wurde. Erst danach darf `Praxisgetestet` vergeben werden.

## Verbindlicher Grundsatz

KiCad ist der Standard. Projektspezifische Erweiterungen sind konsequent mit `Z_` gekennzeichnet.
