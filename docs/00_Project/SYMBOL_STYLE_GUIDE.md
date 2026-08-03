# Verbindliche Symbol-Designrichtlinie

Diese Richtlinie gilt für alle neuen und überarbeiteten Symbolbibliotheken des Projekts. **KiCad ist der Standard.** Projektinterne Ergänzungen oder bewusst abweichende Regeln werden ausschließlich als dokumentierte `Z_`-Erweiterungen geführt.

## 1. Priorität der Regeln

1. Offizielle KiCad-Konventionen und technisch erforderliche KiCad-Formate.
2. Diese dokumentierte `Z_`-Richtlinie für projektspezifische Ergänzungen.
3. Begründete, versionierte Ausnahmen mit Regel-ID und Ablauf- oder Prüftermin.

Eine Abweichung von KiCad darf niemals stillschweigend erfolgen. Ohne dokumentierte `Z_`-Regel oder genehmigte Ausnahme erhält das Element den Status `needs_rework`.

## 2. Raster und Maße

- Symbolursprung, Pins und wesentliche Anschlussgeometrie liegen auf dem KiCad-Standardraster von 100 mil.
- Für grafische Details ist ein 50-mil-Unteraster zulässig, sofern Anschluss- und Ausrichtbarkeit nicht beeinträchtigt werden.
- Kleinere Raster sind nur für technisch notwendige Details und mit dokumentierter Regel oder Ausnahme zulässig.
- Standard-Pinlänge: 100 mil.
- Standard-Pinabstand: 100 mil oder ein ganzzahliges Vielfaches davon.
- Symbole werden so kompakt wie möglich und so groß wie für eindeutige Lesbarkeit nötig aufgebaut.

## 3. Linien und Grundformen

- Elektrische Funktionsgrafik verwendet die KiCad-Standardlinienbreite, sofern keine Symbolklasse eine dokumentierte `Z_`-Abweichung benötigt.
- Gehäuseumrisse, Funktionszeichen und Betätigungselemente müssen optisch unterscheidbar bleiben.
- Dekorative Elemente ohne fachliche Aussage sind zu vermeiden.
- Gefüllte Flächen werden nur verwendet, wenn sie für die normgerechte oder eindeutige Darstellung erforderlich sind.

## 4. Pins

- Pins werden bevorzugt horizontal oder vertikal ausgerichtet.
- Eingänge liegen nach Möglichkeit links oder oben, Ausgänge rechts oder unten; bei Installationsgeräten hat die übliche Stromfluss- und Einbaulogik Vorrang.
- Pin-Nummern entsprechen der technischen Anschlusskennzeichnung des Geräts.
- Pin-Namen verwenden etablierte Kurzbezeichnungen wie `L`, `N`, `PE`, `A1`, `A2`, `13`, `14`.
- Elektrische Pin-Typen müssen die reale Funktion abbilden; passive Anschlüsse dürfen nicht pauschal verwendet werden, wenn eine präzisere KiCad-Klassifikation möglich ist.
- Unsichtbare Pins sind nur zulässig, wenn KiCad-Verhalten und Dokumentation dadurch eindeutig bleiben.

## 5. Texte und Eigenschaften

- Referenz und Wert bleiben die primären sichtbaren Eigenschaften.
- Hersteller-, Bestell- und Katalogdaten werden als zusätzliche Eigenschaften geführt und standardmäßig ausgeblendet, sofern sie den Schaltplan überladen würden.
- Eigenschaftsnamen sind stabil, eindeutig und maschinenlesbar.
- Empfohlene Reihenfolge:
  1. `Reference`
  2. `Value`
  3. `Footprint`
  4. `Datasheet`
  5. `Description`
  6. projektspezifische Metadaten
- Texte dürfen keine grafischen Anschlüsse oder Funktionszeichen überdecken.

## 6. Benennung

- Jede projektinterne Symbolbibliotheksdatei beginnt mit `Z_`.
- Der registrierte Bibliotheksname entspricht dem Dateinamen ohne Endung.
- Qualifizierte Symbol-IDs verwenden `Z_<Bibliothek>:<Symbol>`.
- Symbolnamen sind kurz, fachlich eindeutig und ohne Herstellerbindung, sofern das Symbol eine neutrale Geräteklasse beschreibt.
- Herstellerbezogene Varianten erhalten eine nachvollziehbare Variantenkennung und bleiben von neutralen Basissymbolen getrennt.
- Die Kennzeichnung `Z_` darf nicht für offizielle KiCad-Bibliotheken oder unveränderte KiCad-Inhalte verwendet werden.

## 7. Gerätevarianten und Polzahlen

- Einpolige, mehrpolige und Neutralleiter-Varianten werden als fachlich eigenständige Varianten modelliert, wenn sich Anschlüsse oder Darstellung unterscheiden.
- Zulässige Variantenkennungen sind unter anderem `1P`, `2P`, `3P`, `4P`, `1P+N` und `3P+N`.
- `1P+N` und `3P+N` dürfen nicht als rein numerische Polvarianten behandelt werden; Neutralleiteranschlüsse müssen eindeutig benannt und dargestellt sein.
- Mehrteilige Symbole verwenden KiCad-Units nur, wenn dies die reale Gerätegliederung oder Schaltplanverwendung verbessert.
- Austauschbare Units müssen tatsächlich austauschbar sein; andernfalls werden sie als unterschiedliche Units modelliert.

## 8. Herstellerneutralität

- Das Basissymbol beschreibt die elektrische Funktion, nicht die äußere Produktgestaltung.
- Herstellername, Baureihe, Bestellnummer und technische Daten gehören in Eigenschaften, Gerätekatalog und Variantenbeschreibung.
- Herstellergeometrien werden nur übernommen, wenn sie für Anschlussbelegung oder Funktion notwendig sind.

## 9. Footprint Policy

Jedes Symbol erhält genau einen dokumentierten Wert:

- `required`: Das Symbol ist ohne konkreten Footprint nicht sinnvoll freigabefähig.
- `optional`: Ein Footprint kann zugeordnet werden, ist für die typische Schaltplanverwendung aber nicht zwingend.
- `none`: Das Symbol besitzt bewusst keinen Footprint, beispielsweise bei rein logischen oder externen Elementen.

Ein leeres Footprint-Feld ohne dokumentierte Policy ist nicht zulässig.

## 10. Vorschauen und Dokumentation

- SVG-Vorschauen werden aus der aktuellen Symbolquelle reproduzierbar erzeugt.
- Vorschauen dürfen keine manuell nachgezeichnete, vom KiCad-Symbol abweichende Geometrie enthalten.
- Jede Dokumentationsabbildung nennt Bibliotheks-ID, Symbolname und Qualitätsstatus.
- Änderungen an der Symbolgeometrie erfordern eine Aktualisierung der Vorschau.

## 11. Qualitätsstatus

Ein Symbol darf den Paketstatus `Geprüft` erst erhalten, wenn:

- alle aktivierten KiCad- und `Z_`-Regeln ausgeführt wurden,
- keine nicht dokumentierte Abweichung besteht,
- alle Ergebnisse Regel-ID, Sollwert, Istwert, Begründung und Empfehlung enthalten,
- Footprint Policy, Eigenschaften und Varianten geprüft sind,
- Vorschau und Dokumentation aktuell sind.

Die maschinenlesbaren Statuswerte sind:

- `kicad_conform`
- `z_conform`
- `needs_rework`
- `temporarily_accepted`

## 12. Referenzsymbol

Das MCB-1P-Paket aus Issue #87 ist die erste verbindliche Referenzimplementierung. Neue Symbolklassen müssen dieselben Qualitätsnachweise liefern, dürfen aber dokumentierte klassenspezifische `Z_`-Regeln ergänzen.
