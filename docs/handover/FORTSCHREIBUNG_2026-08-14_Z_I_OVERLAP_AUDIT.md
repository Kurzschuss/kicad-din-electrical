# Fortschreibung 14.08.2026 – Z_I Overlap-Audit

## Zweck

Diese Fortschreibung dokumentiert den ersten systematischen Vergleich der in `main` integrierten Importbibliothek `Z_I_ElectricalComponents` mit den bereits bestehenden kanonischen `Z_`-Bibliotheken des Projekts.

Ausgangspunkt ist die erfolgreich gemergte v14 aus PR #247. Die vorherige Merge-Fortschreibung bleibt für Upload-, CI- und Merge-Historie maßgeblich.

## Repository- und CI-Stand

- Bibliothek in `main`: `symbols/Z_I_ElectricalComponents.kicad_sym`
- Z_I-Symbole: 52 Top-Level-Symbole
- KiCad-Pindefinitionen: 254
- PR #247: gemergt
- Squash-Merge: `bc7d74c4d8cba31bfbf22ae644c64e6d3e1dc29a`
- PR-CI: `ProjectOS complete test suite` Run #698: SUCCESS
- nachgelagerte Main-CI nach Handover-Fortschreibung: Run #701: SUCCESS

Damit ist der Repositoryzustand technisch grün. Der Overlap-Audit ist ausdrücklich eine fachliche Qualitätsprüfung und kein Ersatz für die CI.

## Verbindlicher Bewertungsmaßstab

Der Projekt-Style-Guide fordert für neue und überarbeitete Symbole insbesondere:

- Pins und wesentliche Anschlussgeometrie auf dem 100-mil-Raster;
- grafische Details dürfen das 50-mil-Unteraster verwenden;
- Standard-Pinlänge 100 mil;
- Pinabstand 100 mil oder ganzzahliges Vielfaches;
- präzise elektrische Pin-Typen, sofern die reale Funktion eindeutig bekannt ist;
- `1P+N` und `3P+N` sollen fachlich von rein numerischen Polvarianten unterschieden werden;
- rein logische/virtuelle Elemente können `Z_Footprint_Policy = none` erhalten.

Die Z_I-Bibliothek ist dagegen bewusst quelltreu aus den gelieferten SVG/JS-Symbolen abgeleitet. Diese Quelltreue ist wertvoll, bedeutet aber nicht automatisch Konformität zur kanonischen Z_-Symbolgeometrie.

## Kernergebnis

Von den 52 Z_I-Symbolen wurden im aktuellen Repository folgende Klassen identifiziert:

- **8 direkte Funktionsüberlappungen** mit bereits vorhandenen kanonischen Symbolen;
- **3 strukturelle/gerätebezogene Überlappungen** mit dem bestehenden Schützpaket;
- **41 Symbole ohne direktes kanonisches Gegenstück im aktuellen Repository**.

Wichtig: "ohne direktes kanonisches Gegenstück" bedeutet nur, dass im aktuellen Projektbestand keine entsprechende Z_-Bibliothek vorhanden ist. Es bedeutet nicht automatisch, dass das Symbol bereits produktionsreif oder normativ vollständig geprüft ist.

## 1. Direkte Funktionsüberlappungen

| Z_I-Symbol | vorhandenes kanonisches Symbol | Bewertung | Entscheidung |
|---|---|---|---|
| `Terminal_FeedThrough` | `Z_Terminal_Block:Terminal_Block` | gleiche Grundfunktion einer zweipoligen Durchgangs-/Reihenklemme | kanonisches Symbol vorerst beibehalten; Z_I bleibt Quellenreferenz |
| `Fuse` | `Z_FUSE:FUSE` | gleiche Geräteklasse und Anschlüsse 1/2 | `Z_FUSE` bleibt kanonisch; Z_I nicht automatisch ersetzen |
| `MCB_1P` | `Z_MCB:MCB` | gleiche 1-polige MCB-Funktion | `Z_MCB` bleibt kanonisch |
| `MCB_3P` | `Z_MCB:MCB_3P` | gleiche 3-polige MCB-Funktion und Anschlussnummern 1…6 | `Z_MCB` bleibt kanonisch |
| `MotorProtection_3P` | `Z_Motor_Protection:Motor_Protection` | gleiche 3-polige Motorschutzfunktion | kanonisches Symbol ist semantisch stärker durch L1/L2/L3 und T1/T2/T3 |
| `RCD_2P` | `Z_RCD:RCD` | gleiche 1P+N-/2-polige RCD-Funktion | `Z_RCD` bleibt kanonisch |
| `RCD_4P` | `Z_RCD:RCD_4P` | gleiche 3P+N-/4-polige RCD-Funktion | `Z_RCD` bleibt kanonisch; zusätzlich existiert mit `Z_FI_RCD_4P:FI_RCD_4P` bereits ein älterer einfacher 4P-FI/RCD-Bestand |
| `RCBO_2P` | `Z_RCBO_1P_N:RCBO_1P_N` | Z_I zeigt `1-2 / N-N`, also fachlich 1P+N; der kanonische Name ist präziser | `Z_RCBO_1P_N` bleibt kanonisch; Z_I-Name `RCBO_2P` nicht als kanonische Benennung übernehmen |

### Warum die kanonischen Varianten vorerst stärker sind

Die bestehenden kanonischen Geräte enthalten teilweise deutlich reichere Gerätemetadaten. Beispiele:

- `Z_CONTACTOR:CONTACTOR` führt unter anderem Polzahl, Hauptkontaktart, Nennstrom, AC-3-Nutzungskategorie, Spulenanschlüsse und Norm.
- `Z_RCD:RCD` / `RCD_4P` führen Polzahl, Nennstrom, Fehlerstrom, RCD-Typ, Kurzschluss-/Schaltvermögen und Prüftasterstatus.
- `Z_RCBO_1P_N:RCBO_1P_N` führt unter anderem `1P+N`-Semantik, geschützte Pole, Nennstrom, Kennlinie, Fehlerstrom, RCD-Typ und Ausschaltvermögen.
- `Z_Motor_Protection:Motor_Protection` benennt die Leistungsanschlüsse als `L1/L2/L3` und `T1/T2/T3`.

Die Z_I-Varianten bewahren dagegen primär die gelieferten Quellgrafiken und deren sichtbare Anschlussbeschriftung.

## 2. Strukturelle Überlappung mit `Z_CONTACTOR`

Drei Z_I-Symbole sind keine einfachen Dubletten, überschneiden sich aber klar mit dem bestehenden Schützpaket:

| Z_I-Symbol | Verhältnis zu `Z_CONTACTOR:CONTACTOR` | Bewertung |
|---|---|---|
| `Contactor_Coil` | entspricht dem Spulenteil A1/A2 des kanonischen Schützes | sinnvoll als getrennte Darstellungsform, aber nicht als Ersatz für `Z_CONTACTOR` |
| `Contactor_MainContacts_3P` | entspricht den drei Hauptkontakten des kanonischen Schützes | sinnvoll für verteilte Schaltplandarstellung; benötigt vor Promotion Z_-Raster-/Metadaten-Normalisierung |
| `Contactor_3P_1NO_1NC` | erweitert die Schützfunktion um vier Units: Spule, 3P-Hauptkontakte, 1NO, 1NC | funktional breiter als `Z_CONTACTOR`; guter Kandidat für eine spätere kanonische Multi-Unit-Erweiterung, aber nicht unverändert übernehmen |

Für `Contactor_3P_1NO_1NC` bleibt die in v4 definierte Gerätebelegung maßgeblich:

- Unit 1: `A1/A2`
- Unit 2: Hauptkontakte `1-6`
- Unit 3: NO `13-14`
- Unit 4: NC `21-22`

## 3. 41 Symbole ohne direktes kanonisches Gegenstück

### Verbindungen / Verweise

- `Arrow_Input`
- `Arrow_Output`

`Terminal_FeedThrough` ist hier nicht enthalten, da es mit `Z_Terminal_Block` überlappt.

### Potentiale

- `Potential_L1`
- `Potential_L1_L2`
- `Potential_L1_L2_L3`

Diese sind **keine Busbar-Dubletten**. Die Z_I-Potentiale sind virtuelle, nicht in BOM/PCB geführte Darstellungselemente. Die vorhandenen Busbar-Symbole repräsentieren physische Verteilkomponenten.

### Elektronik / Steuerung

- `Resistor`
- `Potentiometer`
- `LDR`
- `Capacitor`
- `Diode`
- `LED`
- `Transistor_NPN`
- `Transistor_PNP`
- `TRIAC`
- `DIAC`
- `IC_Blank_4Pin`
- `IC_Blank_6Pin`
- `IC_Blank_8Pin`
- `IC_Blank_10Pin`
- `Arduino_Uno`
- `Arduino_R4`
- `Arduino_Nano`
- `PowerSupply_ACDC`
- `Relay_Module_PCB`
- `Buzzer`
- `TerminalBlock_PCB_2P`

### Schutzgeräte – neue Polvarianten

- `MCB_2P`
- `RCBO_4P`

`RCBO_4P` ist als 3P+N-Funktion zu verstehen; eine spätere kanonische Benennung sollte deshalb eher `RCBO_3P_N` beziehungsweise eine projekteinheitliche `3P+N`-Benennung verwenden als nur `4P`.

### Verbraucher / Antriebe

- `Converter_ACAC`
- `Converter_ACDC_Rectifier`
- `PowerSupply_ACDC_PE`
- `Motor_3Ph`
- `Motor_Dahlander_6T`
- `Lamp`
- `Motor_DC`
- `Motor_AC_1Ph`
- `Heater_Resistive`

### Schaltgeräte / Kontakte

- `PushButton`
- `Switch`
- `AuxContact_NO`
- `AuxContact_NC`

`Switch` wird **nicht** als Dublette zu `Z_MAIN_SWITCH` gewertet. Das Z_I-Symbol ist ein generischer Schalter; `Z_MAIN_SWITCH` beschreibt ausdrücklich einen Haupt-/Lasttrennschalter nach eigener Geräteklasse.

## 4. Wichtige Qualitätsabweichungen der Z_I-Importgeometrie

### 4.1 Raster und Pinlängen

Der Style-Guide verlangt 100-mil-Raster für Pins/wesentliche Anschlussgeometrie und 100-mil-Standard-Pinlänge.

In Z_I sind zahlreiche SVG-abgeleitete Werte vorhanden, beispielsweise:

- Pinpositionen wie `1.778 mm`, `4.318 mm`, `-2.667 mm`;
- Pinlänge häufig `1.27 mm` = 50 mil.

Beispiele sind unter anderem die Z_I-MCB- und Schutzgeräte-Symbole.

**Folge:** Die Z_I-Geometrie ist als Quellen-/Importgeometrie zulässig und nachvollziehbar, aber sie darf nicht allein aufgrund der grünen CI als `z_conform` oder als kanonischer Ersatz betrachtet werden. Für eine Promotion in eine kanonische Z_-Bibliothek ist eine Raster-Normalisierung erforderlich, sofern keine dokumentierte Ausnahme beschlossen wird.

### 4.2 Elektrische Pin-Typen

Die Z_I-Konvertierung verwendet bewusst überwiegend `passive`, weil die sechs JS/SVG-Quellen keine belastbare KiCad-ERC-Semantik liefern.

Das bleibt für die quelltreue Importbibliothek nachvollziehbar. Für eine kanonische Promotion müssen jedoch insbesondere bei komplexeren Elektronik-/Versorgungssymbolen die elektrischen Pin-Typen fachlich geprüft werden. Es werden weiterhin keine ERC-Typen geraten.

### 4.3 Footprint Policy virtueller Symbole

Bei der Repository-Normalisierung wurde `Z_Footprint_Policy = optional` einheitlich ergänzt. Für die fünf eindeutig virtuellen Elemente

- `Arrow_Input`
- `Arrow_Output`
- `Potential_L1`
- `Potential_L1_L2`
- `Potential_L1_L2_L3`

ist nach dem aktuellen Style-Guide fachlich eher `Z_Footprint_Policy = none` passend, da sie nicht in BOM/PCB geführt werden.

Dies wird als **offener Nacharbeitspunkt** dokumentiert. Die große Bibliotheksdatei wird nicht allein für diese Metadatenänderung ungeprüft umgeschrieben; die Korrektur soll zusammen mit der nächsten Z_I-Normalisierungsrunde erfolgen.

## 5. Namens- und Suchkonflikte

Qualified IDs verhindern technische Kollisionen, beispielsweise:

- `Z_MCB:MCB_3P`
- `Z_I_ElectricalComponents:MCB_3P`

Trotzdem entsteht für Benutzer in der Symbolsuche eine fachliche Mehrdeutigkeit. Deshalb gilt bis zum Abschluss der Promotion-/Bereinigungsrunde:

- kanonische Gerätebibliotheken bleiben die bevorzugte Quelle für bereits vorhandene Geräteklassen;
- `Z_I_ElectricalComponents` wird als Import-/Quellbibliothek behandelt;
- Z_I-Dubletten werden nicht in Gerätepakete oder Kataloge übernommen, solange keine explizite Promotion entschieden wurde.

## 6. Promotionsempfehlung

### Nicht promoten / kanonisches Symbol beibehalten

- `Terminal_FeedThrough`
- `Fuse`
- `MCB_1P`
- `MCB_3P`
- `MotorProtection_3P`
- `RCD_2P`
- `RCD_4P`
- `RCBO_2P`

Diese bleiben in Z_I als Quellenreferenz erhalten.

### Als Erweiterung prüfen

- `Contactor_Coil`
- `Contactor_MainContacts_3P`
- `Contactor_3P_1NO_1NC`

Hier ist eine spätere Zusammenführung mit `Z_CONTACTOR` fachlich sinnvoller als eine parallele zweite kanonische Schützfamilie.

### Neue Kandidaten – vor Promotion normalisieren

Die übrigen 41 Symbole können als Kandidaten für neue kanonische Pakete betrachtet werden. Vor jeder Promotion sind mindestens zu prüfen:

1. Projekt-/Taxonomie-Scope;
2. 100-mil-Pin- und Anschlussraster;
3. 100-mil-Pinlänge beziehungsweise begründete Ausnahme;
4. Benennung (`1P+N`, `3P+N` usw.);
5. ERC-Pintypen;
6. Footprint Policy;
7. Referenzkennzeichen;
8. Dokumentation und Vorschau;
9. mögliche Überschneidung mit offiziellen KiCad-Standardbibliotheken, falls ein Symbol als allgemeines Elektronik-Basissymbol vorgesehen ist.

## 7. Nächster Arbeitsblock

Der nächste verbindliche Schritt ist jetzt **nicht** mehr der generelle Overlap-Audit; dieser ist auf Repository-Ebene abgeschlossen.

Als Nächstes:

1. lokaler KiCad-Ladetest von `Z_I_ElectricalComponents` in einer echten KiCad-Installation;
2. insbesondere prüfen:
   - alle 52 Top-Level-Symbole auswählbar;
   - `Contactor_3P_1NO_1NC` mit allen vier Units;
   - Potentiale;
   - sichtbare Texte und manuell gezeichnete Pinbeschriftungen;
   - Anschlussfangpunkte auf dem KiCad-Raster;
3. danach eine **Z_I-Normalisierungsrunde v15** planen, nicht direkt blind durchführen;
4. v15 zuerst auf die eindeutig neuen Kandidaten und die fünf virtuellen Symbole fokussieren;
5. bestehende kanonische Dubletten nicht neu zeichnen, solange kein konkreter fachlicher Vorteil dokumentiert ist.

## Kurzfassung

**Overlap-Audit abgeschlossen:** 8 direkte Funktionsdubletten, 3 strukturelle Schütz-Overlaps, 41 im aktuellen Repository neue Symbolabdeckungen. Z_I bleibt vorerst Import-/Quellbibliothek. Die neue Abdeckung ist wertvoll, aber wegen SVG-abgeleitetem Raster, 50-mil-Pinlängen, konservativen ERC-Typen und fünf zu korrigierenden virtuellen Footprint-Policies noch nicht pauschal als kanonisch freigegeben. Nächster Schritt: echter KiCad-Ladetest, danach gezielte v15-Normalisierungsplanung.