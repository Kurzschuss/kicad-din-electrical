# Qualitätshandbuch für Bibliothekspakete

Stand: 10. August 2026

Dieses Dokument ist die verbindliche Qualitätsrichtlinie für neue und fachlich überarbeitete Gerätefamilien, Symbole, Footprints, Gerätekatalogeinträge und daraus erzeugte Bibliothekspakete im Projekt **KiCad DIN Electrical**.

**KiCad ist der technische Standard.** Projektspezifische Ergänzungen werden sichtbar und nachvollziehbar als `Z_`-Regeln, `Z_`-Metadaten oder versionierte Ausnahmen geführt. Dieses Handbuch ersetzt weder das KiCad-Dateiformat noch die spezialisierten Fachrichtlinien; es verbindet sie zu einem verbindlichen Paket- und Freigabeprozess.

## 1. Geltungsbereich und Quellenhierarchie

Für neue oder überarbeitete Inhalte gilt folgende Reihenfolge:

1. technisch erforderliche KiCad-Formate und offizielle KiCad-Konventionen;
2. aktive Regeln unter `rules/kicad/`, `rules/z/` und `rules/project/`;
3. dieses Qualitätshandbuch;
4. spezialisierte Projektleitfäden, insbesondere `docs/00_Project/SYMBOL_STYLE_GUIDE.md`;
5. versionierte Ausnahmen unter `rules/exceptions/`.

Widersprechen sich Dokumentation und ausführbarer Validator, darf der Widerspruch nicht stillschweigend übernommen werden. Er wird als Qualitätsproblem behandelt und die Regel- oder Dokumentationsquelle wird gemeinsam korrigiert.

## 2. Grundsatz: Geräte werden als Pakete entwickelt

Ein neues Gerät ist nicht nur eine Symbolgrafik. Ein Bibliothekspaket umfasst – soweit fachlich sinnvoll:

- Symbol oder Symbolfamilie;
- Footprint entsprechend der dokumentierten Footprint Policy;
- Gerätekatalogeintrag beziehungsweise generierte Gerätevarianten;
- Gerätefamilie und Taxonomiezuordnung;
- Symbolvorschau;
- gegebenenfalls Footprint- und 3D-Vorschau;
- technische Referenz- und Benutzerdokumentation;
- automatisierte Tests und Validatorprüfungen;
- Qualitätsstatus und Reifegrad;
- für `Praxisgetestet` zusätzlich ein dokumentiertes Beispielprojekt.

Nicht jeder Gerätetyp benötigt einen Footprint oder ein reales 3D-Modell. Die bewusste Nichtverwendung wird jedoch genauso dokumentiert wie eine vorhandene Zuordnung.

## 3. Benennung und Sprache

### 3.1 Primärsprache

Deutsch ist die verbindliche Primärsprache für:

- Benutzerdokumentation und Anleitungen;
- Menüs, sichtbare Fehlermeldungen und Qualitätsberichte;
- HTML- und Z_Cockpit-Anzeigen;
- Gerätefamiliennamen und fachliche Beschreibungen.

### 3.2 Technische Kennungen

Etablierte internationale Fachkürzel bleiben für stabile IDs und Dateinamen ausdrücklich erhalten, zum Beispiel `MCB`, `RCD`, `RCBO` und `SPD`.

Projektinterne Bibliotheken, Symbole, Footprints und eigene 3D-Artefakte verwenden das Präfix `Z_`. Bestehende technische IDs werden nicht allein aus sprachlichen Gründen umbenannt.

### 3.3 Zweisprachige Gerätemetadaten

Neue oder fachlich überarbeitete Gerätekatalogeinträge erhalten gemeinsam:

```json
{
  "name_de": "Leitungsschutzschalter B16, 1-polig",
  "name_en": "Miniature Circuit Breaker B16, 1-pole",
  "abbreviation": "MCB"
}
```

Dabei gilt:

- `name_de` ist die primäre sichtbare Bezeichnung;
- `name_en` dient internationaler Suche und späteren englischen Ausgaben;
- `abbreviation` ist ein etabliertes großgeschriebenes Fachkürzel;
- technische IDs werden nicht aus den Anzeigenamen erzeugt;
- werden zweisprachige Felder verwendet, müssen alle drei gemeinsam vorhanden sein.

## 4. Symbolstandard

Die Detailregeln stehen in `docs/00_Project/SYMBOL_STYLE_GUIDE.md`. Für die Paketfreigabe gelten mindestens folgende Grundsätze.

### 4.1 Struktur und Raster

- Projektinterne Symbolbibliotheken beginnen mit `Z_`.
- Der registrierte Bibliotheksname entspricht dem Dateinamen ohne `.kicad_sym`.
- Qualifizierte Symbol-IDs verwenden `Z_<Bibliothek>:<Symbol>`.
- Pins und wesentliche Anschlussgeometrie liegen grundsätzlich auf dem 100-mil-Raster.
- Grafische Details dürfen das dokumentierte 50-mil-Unteraster verwenden.
- Standard-Pinlänge ist 100 mil, sofern keine klassenspezifische Regel oder genehmigte Ausnahme etwas anderes festlegt.
- Der aktuelle `Z_`-Referenzregelsatz verwendet 10 mil Standardlinienbreite und 50 mil Primärtextgröße für `Reference` und `Value`.

Die numerischen Werte sind keine Einladung, bereits freigegebene Symbolgeometrien ohne fachlichen Grund neu zu zeichnen. Bestehende freigegebene Geometrie wird nur auf ausdrücklichen fachlichen Änderungsbedarf angepasst.

### 4.2 Pins und elektrische Bedeutung

- Anschlussnummern entsprechen der realen technischen Kennzeichnung.
- Neutralleiter, Schutzleiter und Hilfskontakte werden eindeutig benannt.
- Mehrpolige Varianten werden eigenständig modelliert, wenn sich Anschlusszahl oder Funktion unterscheiden.
- Elektrische Pin-Typen bilden die reale Funktion so präzise wie sinnvoll ab.
- Unsichtbare Pins sind nur zulässig, wenn KiCad-Verhalten und Dokumentation eindeutig bleiben.

### 4.3 Eigenschaften

Für neue beziehungsweise überarbeitete Symbole werden die üblichen KiCad-Eigenschaften und projektspezifischen Metadaten sauber getrennt. Typische Eigenschaften sind:

```text
Reference
Value
Manufacturer
Part Number
Footprint
Datasheet
Description
Z_Footprint_Policy
```

`Reference` und `Value` bleiben die primären sichtbaren Eigenschaften. Hersteller-, Bestell-, Datenblatt- und projektspezifische Metadaten werden nur sichtbar dargestellt, wenn dies für die Schaltplanlesbarkeit sinnvoll ist.

Fehlende Hersteller- oder Datenblattangaben können bei herstellerneutralen Vorlagen einen nicht blockierenden Validatorhinweis erzeugen. Solche Hinweise müssen vor einer Freigabe bewusst geprüft werden; sie dürfen nicht als erfundene Herstellerdaten „behoben“ werden.

## 5. Verbindliche Footprint Policy

Die kanonische Symboleigenschaft lautet:

```text
Z_Footprint_Policy
```

Zulässige Werte:

- `required`: ein konkreter Footprint ist für die Freigabe erforderlich;
- `optional`: ein Footprint kann zugeordnet werden, ist für die typische Verwendung aber nicht zwingend;
- `none`: das Symbol besitzt bewusst keinen Footprint.

Für neue oder fachlich überarbeitete Symbole muss `Z_Footprint_Policy` explizit vorhanden sein. Der Basisvalidator kann ältere Bestände mit dem historischen Feld `Footprint Policy` beziehungsweise ohne explizites Feld weiterhin lesen; diese Kompatibilität ist keine Vorlage für neue Inhalte.

Zusätzliche Regeln:

- bei `required` muss `Footprint` auf eine vorhandene qualifizierte ID zeigen;
- bei `none` darf kein Footprint eingetragen sein;
- bei `optional` darf das KiCad-Feld `Footprint` leer bleiben;
- Symbol- und Gerätekatalog-Policy müssen fachlich übereinstimmen.

## 6. Footprintstandard

### 6.1 Bibliotheksstruktur

- Footprintbibliotheken liegen unter `footprints/Z_*.pretty/`;
- der Footprintdateiname beginnt mit `Z_`, sofern es sich um ein projektspezifisches Footprint handelt;
- interner Footprintname und Dateiname ohne `.kicad_mod` stimmen überein;
- qualifizierte IDs verwenden `Z_<Bibliothek>:Z_<Footprint>`;
- die Repositorystruktur hält für projektinterne Symbolbibliotheken die vom Basisvalidator erwartete gleichnamige `.pretty`-Bibliothek bereit, auch wenn eine Geräteklasse aktuell keinen konkreten Footprint benötigt.

### 6.2 Geometrie und Präsentation

Aktive `ZFP-*`-Regeln und KiCad-Vorgaben sind maßgeblich. Der aktuelle Qualitätsadapter prüft unter anderem:

- KiCad-kompatiblen Footprintgenerator;
- vorhandene und geschlossene Courtyard-Kontur, wo die Regel für das Element gilt;
- dokumentierte Courtyard-Linienbreite;
- Referenz- und Werttext;
- vorhandene Fertigungsdarstellung (`F.Fab`/`B.Fab`), wenn für den Footprint vorgesehen;
- paket- oder footprintklassenspezifische Abmessungen, sofern dafür eine aktive Regel existiert.

Klassenspezifische Maße – beispielsweise die 18-mm-Modulbreite eines DIN-Modul-Footprints – dürfen nicht pauschal auf alle Footprints übertragen werden.

## 7. 3D-Modelle und 3D-Vorschauen

Ein reales 3D-Modell wird nur als vorhanden gewertet, wenn ein KiCad-Footprint eine auflösbare `model`-Referenz auf eine tatsächlich vorhandene Repositorydatei besitzt.

Unterstützte Repositoryformate sind derzeit `.step`, `.stp` und `.wrl`. Der vorgesehene Projektpfad ist:

```text
3dmodels/Z_3DModell.3dshapes/
```

Empfohlene Referenz:

```text
${KICAD_Z_3DMODEL_DIR}/Z_Beispiel.step
```

Eine aus vorhandener `F.Fab`-Geometrie erzeugte Hüllkörperansicht ist nur eine technische Vorschau und **kein** echtes Produktmodell. Es werden keine Gehäuseabmessungen, STEP-Dateien oder Herstellerdaten erfunden.

Fehlt ein reales 3D-Modell, blockiert dies ein Paket nur dann, wenn das Modell für die konkrete Geräteklasse ausdrücklich zum Paketumfang erklärt wurde. Vorhandene Modellreferenzen müssen dagegen auflösbar und prüfbar sein.

## 8. Gerätekatalog

Der technische Gerätekatalog unter `data/devices/` ist eine fachliche Datenquelle und keine freie Beschreibungssammlung.

### 8.1 Pflichtfelder

Der aktuelle Validator verlangt mindestens:

```text
id
manufacturer
series
part_number
device_type
function_group
symbol
footprint_policy
```

`id` muss eindeutig und maschinenlesbar sein. `function_group` muss auf eine vorhandene Familie aus `data/taxonomy/device_families.json` zeigen. `symbol` und gegebenenfalls `footprint` verwenden qualifizierte Bibliotheks-IDs.

### 8.2 Technische Werte

Numerische technische Werte müssen positiv und in den im Feldnamen dokumentierten Einheiten angegeben werden, zum Beispiel:

- `rated_current_a` in Ampere;
- `residual_current_ma` in Milliampere;
- `breaking_capacity_ka` in Kiloampere;
- `modules` als positive Modulbreite beziehungsweise Modulanzahl nach Datenmodell.

Unbekannte oder nicht belegte Produktwerte werden nicht geschätzt.

### 8.3 Quellenstatus

Für neue oder überarbeitete Einträge wird der Quellenstand bewusst gekennzeichnet. Der aktuelle Katalog kennt:

- `template`: herstellerneutrale Vorlage beziehungsweise Strukturbeispiel;
- `verified`: fachlich anhand belastbarer Quelle geprüft;
- `unverified`: Daten vorhanden, aber noch nicht ausreichend verifiziert.

`Generic` kennzeichnet herstellerneutrale Datensätze und darf nicht als realer Hersteller interpretiert werden.

## 9. Serien, Varianten und Generatoren

Gerätevarianten werden systematisch aus fachlich definierten Parametern aufgebaut. Varianten dürfen sich nur dort unterscheiden, wo ein technisches Merkmal tatsächlich variiert.

Für generierte Bestände gilt:

- die Generatorquelle ist Single Source of Truth;
- generierte Gerätedateien werden nicht manuell „zurechteditiert“;
- ID-Schemata bleiben stabil und maschinenlesbar;
- neue Variantenparameter benötigen Validator- und Testabdeckung;
- `python tools/generate_device_variants.py --check` muss den Repositorystand als aktuell bestätigen.

## 10. Dokumentation und Vorschauen

Ein `Geprüft`-Paket benötigt nachvollziehbare technische Dokumentation. Abhängig von der Geräteklasse gehören dazu:

- technische Referenz beziehungsweise Symbol-/Paketbeschreibung;
- nachvollziehbare Varianten- und Anschlussbeschreibung;
- aktuelle Symbolvorschau;
- Footprintdarstellung, falls ein Footprint fachlich Bestandteil des Pakets ist;
- 3D-Status, falls ein Modell oder eine technische Hüllvorschau vorhanden ist;
- Benutzerhinweise für Besonderheiten, die nicht aus Symbol oder Metadaten ersichtlich sind.

Vorschauen werden reproduzierbar aus den Repositoryquellen erzeugt. Manuell nachgezeichnete Bilder dürfen nicht als technische Referenz an die Stelle der KiCad-Quelle treten.

## 11. Qualitätsstatus und Reifegrad sind getrennte Begriffe

### 11.1 Maschinenlesbarer Qualitätsstatus

Die Quality Engine verwendet:

- `kicad_conform`: die ausgewerteten KiCad-Regeln sind erfüllt;
- `z_conform`: die ausgewerteten projektspezifischen `Z_`-Regeln sind erfüllt;
- `needs_rework`: mindestens eine nicht akzeptierte Abweichung erfordert Nacharbeit;
- `temporarily_accepted`: eine Abweichung ist durch eine versionierte, befristete Ausnahme sichtbar akzeptiert.

Ein Status beschreibt das Ergebnis der Regeln, nicht automatisch die Vollständigkeit des gesamten Gerätepakets.

### 11.2 Paket-Reifegrad

`data/Z_PACKAGE_PROGRESS.json` verwendet:

#### Entwurf

Das Paket befindet sich im Aufbau. Bestandteile, Nachweise oder Tests dürfen fehlen. `needs_rework` ist in diesem Reifegrad zulässig und sichtbar.

#### Geprüft

Mindestens folgende Paketbestandteile sind vorhanden und durch Referenzen nachvollziehbar:

- Symbol;
- Gerätedaten;
- Dokumentation;
- automatisierte Tests.

Zusätzlich gilt:

- der Qualitätsstatus darf nicht `needs_rework` sein;
- Footprint Policy und gegebenenfalls vorhandener Footprint sind konsistent;
- aktive Validator- und Qualitätsprüfungen sind erfolgreich oder eine zeitweilige Ausnahme ist ausdrücklich dokumentiert;
- relevante nicht blockierende Warnungen wurden fachlich bewertet;
- ein Praxisbeispiel darf noch fehlen.

Diese Mindestbedingungen werden durch `tools/generate_package_progress.py` geprüft.

#### Praxisgetestet

Alle Bedingungen von `Geprüft` sind erfüllt und zusätzlich:

- ein dokumentiertes Beispielprojekt ist vorhanden;
- das Paket wurde in diesem Projekt real oder realitätsnah verwendet;
- Anschlussbelegung, Symbollesbarkeit, Footprintzuordnung und Variantenwahl wurden dabei praktisch kontrolliert;
- gefundene Abweichungen wurden korrigiert oder als nachvollziehbare Ausnahme dokumentiert.

Der Paketfortschritt akzeptiert `Praxisgetestet` nur für vollständige Pakete mit Beispielnachweis.

## 12. Praktischer Nachweis

Ein Praxisnachweis ist reproduzierbar und nennt mindestens:

- Beispielprojekt beziehungsweise Repositorypfad;
- verwendete Geräte-/Symbol-IDs;
- getestete KiCad-Version;
- getestete Kernfunktionen, zum Beispiel Platzierung, Verdrahtung, ERC und Footprintzuordnung;
- festgestellte Auffälligkeiten und deren Ergebnis;
- Datum oder versionierten Commit/PR als Bezug.

Ein bloßer Hinweis „funktioniert bei mir“ reicht nicht für `Praxisgetestet`.

## 13. Regeln und Ausnahmen

Regeldateien enthalten keinen ausführbaren Fremdcode. Ein `check.type` verweist nur auf registrierte, getestete Prüftypen.

Versionierte Ausnahmen benötigen mindestens:

- eindeutige Ausnahme-ID;
- betroffene Regel-ID;
- betroffenes Element oder Muster;
- zulässigen temporären Status;
- fachliche Begründung;
- Referenz auf Richtlinie, Issue oder PR;
- Ablaufdatum oder verbindlichen Prüftermin.

Eine nicht dokumentierte Abweichung wird nicht durch einen Kommentar im Code oder das Abschalten eines Tests legitimiert.

## 14. Freigabeverfahren für ein Bibliothekspaket

Vor dem Wechsel auf `Geprüft` wird in dieser Reihenfolge kontrolliert:

1. Gerätefamilie und fachlicher Umfang sind eindeutig definiert.
2. Symbol und Anschlussbelegung sind fachlich geprüft.
3. `Z_Footprint_Policy` ist explizit und korrekt.
4. Ein erforderlicher Footprint existiert und erfüllt die aktiven Regeln.
5. Gerätekatalogfelder, Taxonomie, technische Werte und Quellenstatus sind plausibel.
6. Varianten sind vollständig und reproduzierbar generiert.
7. Dokumentation und technische Vorschauen entsprechen den aktuellen Quellen.
8. Automatisierte Tests und Validatoren sind erfolgreich.
9. `data/Z_PACKAGE_PROGRESS.json` enthält den belegbaren Stand und Referenzen.
10. Generierte Referenzen und Fortschrittsdateien sind aktuell.
11. Der PR enthält keine fachfremden Geometrieänderungen oder unerklärte Nebeneffekte.

Für `Praxisgetestet` kommt anschließend der dokumentierte praktische Nachweis hinzu.

## 15. Verbindliche Prüfkommandos

Je nach geändertem Paket sind mindestens die relevanten Prüfungen auszuführen. Der vollständige CI-Lauf bleibt die maßgebliche Endkontrolle.

```text
python tools/validate_libraries.py
python tools/validate_device_catalog.py
python tools/generate_device_variants.py --check
python tools/generate_symbol_previews.py --check
python tools/generate_3d_previews.py --check
python tools/generate_package_progress.py --check
python -m tools.project_validator
python -m pytest -q
```

Unter Windows und Unix stehen zusätzlich die Projekt-Teststarter `run_tests.bat` beziehungsweise `run_tests.sh` zur Verfügung.

Die Release-/CI-Profile der Quality Engine prüfen die aktivierten KiCad- und `Z_`-Regeln. Ein lokaler Einzeltest ersetzt nicht die vollständige CI-Prüfung des Pull Requests.

## 16. Nicht zulässig

Für freizugebende Pakete sind insbesondere nicht zulässig:

- erfundene Hersteller-, Datenblatt-, Produkt- oder 3D-Daten;
- manuelle Änderungen an generierten Varianten anstelle der Generatorquelle;
- unqualifizierte Symbol- oder Footprint-IDs;
- `required` ohne Footprint beziehungsweise `none` mit Footprint;
- neue Symbole ohne explizite `Z_Footprint_Policy`;
- verdeckte Abweichungen ohne Regel/Ausnahme;
- Hochstufung auf `Geprüft` trotz `needs_rework`;
- Hochstufung auf `Praxisgetestet` ohne dokumentiertes Beispiel;
- Statusänderungen nur zur „Kosmetik“, ohne prüfbaren Nachweis;
- Änderungen an bereits freigegebener Symbolgeometrie ohne fachlichen Anlass.

## 17. Referenzpakete

Aktuell dienen insbesondere folgende Pakete als nachvollziehbare Referenzen:

- `Z_MCB` – `Geprüft`, Qualitätsstatus `z_conform`;
- `Z_RCD` – `Geprüft`, Qualitätsstatus `z_conform`.

Der aktuelle Paketstand wird ausschließlich in `data/Z_PACKAGE_PROGRESS.json` gepflegt und daraus nach `docs/04_Reference/Z_PACKAGE_PROGRESS.md` erzeugt.

MCB und RCD sind Referenzen für Prozess und Nachweisstruktur. Ihre bestehende freigegebene Geometrie wird dadurch nicht zu einer universellen Schablone für andere Geräteklassen.

## 18. Definition of Done

Ein Bibliothekspaket ist für den Reifegrad `Geprüft` abgeschlossen, wenn sein fachlicher Umfang eindeutig ist, die erforderlichen Paketbestandteile vorhanden sind, alle relevanten Quellen nachvollziehbar sind, aktive Prüfungen keinen nicht akzeptierten Fehler enthalten und der Stand reproduzierbar aus dem Repository erzeugt werden kann.

`Praxisgetestet` bedeutet zusätzlich, dass diese Qualität in einem dokumentierten realen oder realitätsnahen KiCad-Anwendungsfall bestätigt wurde.

Damit ist Qualität im Projekt kein manuell vergebenes Etikett, sondern das Ergebnis aus **fachlicher Richtigkeit, nachvollziehbaren Daten, reproduzierbaren Generatoren, automatisierten Prüfungen, Dokumentation und – für die höchste Reifestufe – praktischer Verwendung**.
