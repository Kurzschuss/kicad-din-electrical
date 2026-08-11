# Arbeitsstand / Tagesabschluss – 12. August 2026

Stand: 12. August 2026, 00:31 CEST  
Repository: `Kurzschuss/kicad-din-electrical`  
Maßgebliche Quelle: `main`  
Fachlicher `main`-Stand vor diesem Dokument: `6612911fdd351b33f60545791a43f3ee06e76e93` (Merge von PR #213)  
Letzter vollständiger Main-Lauf: `ProjectOS complete test suite #617 = SUCCESS`

## Zweck dieses Handovers

Dieses Dokument ist der **maßgebliche Fortsetzungsstand nach dem Arbeitsblock vom 10./11. August bis zum lokalen Tagesbeginn 12.08.2026**. Es ergänzt den bisherigen Gesamt-Handover vom 10.08.2026 und dokumentiert vor allem den weiteren Ausbau der Gerätebibliotheken, die neue Hersteller-Stammdatenbasis und den exakten nächsten Einstiegspunkt.

Für die nächste Sitzung gilt:

- `main` ist weiterhin die Single Source of Truth.
- Zuerst `docs/handover/README.md` und anschließend dieses Dokument lesen.
- Bei einem Widerspruch zwischen diesem Handover und einem später veränderten `main` gilt immer der aktuelle Repositorystand.
- Der Handover vom 10.08.2026 bleibt für ProjectOS-/Z_Cockpit-Governance, Sicherheitsmodell, Projektdateien, 3D, KiCad-Editorintegration und die früheren UI-Baselines maßgeblich, soweit diese hier nicht ausdrücklich aktualisiert werden.
- Bereits freigegebene MCB- und RCD-Symbolgeometrien werden nicht ohne ausdrücklichen Änderungswunsch verändert.
- Der GitHub-Ruleset bleibt separat blockiert und ist **kein** automatischer nächster Arbeitspunkt.

---

# 1. Unverändert zu respektierende Baselines

## 1.1 MCB

Freigegebene technische IDs:

```text
Z_MCB:MCB
Z_MCB:MCB_3P
```

Die 1P-/3P-Geometrie ist weiterhin visuell freigegeben und eingefroren. Keine Arbeit dieses Blocks hat die MCB-Geometrie verändert.

## 1.2 RCD 2P

Freigegebene technische ID:

```text
Z_RCD:RCD
```

Die am 10.08. freigegebene Geometrie bleibt eingefroren. Insbesondere Testzweig, Kontaktlagen, mechanische Kopplung, Kreuzkasten, Summenstromwandler/Auslöseeinheit, schwarzer Sensorkern und die freigegebene untere Erfassungslinie dürfen nicht beiläufig neu gezeichnet werden.

## 1.3 RCD 4P / 3+N

Freigegebene technische ID:

```text
Z_RCD:RCD_4P
```

Auch diese Geometrie bleibt unverändert. Erweiterungen dieses Arbeitsblocks betrafen nur Gerätedaten, Tests, Katalogsichtbarkeit und Dokumentation.

## 1.4 Z_Cockpit-Bibliotheksansicht

Die am 10.08. freigegebene Bibliotheksansicht bleibt die Layoutbasis. Kein grundlegendes Redesign ohne ausdrücklichen Benutzerwunsch.

---

# 2. Änderungen seit dem Handover vom 10.08.2026

Der vorige maßgebliche Tagesabschluss wurde mit PR #204 eingebracht. Danach wurden PR #205 bis #213 gemergt.

| PR | Inhalt | Ergebnis |
|---|---|---|
| #205 | Windows-Pfadprüfung im Projektvalidator plattformneutral korrigieren | gemergt |
| #206 | Z_Cockpit-Benutzerverwaltung vollständig vertikal scrollbar machen | gemergt |
| #207 | RCD 2P: Typ B und B+ herstellerneutral ergänzen | gemergt |
| #208 | RCD-Katalog: `RCD-Typ` und `IΔn` in Katalog und Z_Cockpit anzeigen/filtern | gemergt |
| #209 | RCD 4P: Typ F ergänzen | gemergt |
| #210 | RCBO 1P+N technisch vervollständigen | gemergt |
| #211 | Hauptschalter 2P/4P technisch vervollständigen | gemergt |
| #212 | Verifizierte Hersteller-Stammdatenbasis ergänzen | gemergt |
| #213 | Schütz 3P AC-3 technisch vervollständigen | gemergt |

---

# 3. RCD – aktueller Datenstand

## 3.1 RCD 2P

Bestehende A/F-Serie:

- 4 Nennströme: 16, 25, 40, 63 A;
- 4 Bemessungsdifferenzströme: 10, 30, 300, 500 mA;
- Typ A und F;
- 6 kA und 10 kA Kurzschlusswert;
- 1,5 kA Schließ-/Ausschaltvermögen;
- insgesamt 64 Varianten.

Mit PR #207 kam eine separate konservative B/B+-Serie hinzu:

- 16, 25, 40, 63 A;
- 30 und 300 mA;
- Typ B und B+;
- insgesamt 16 Varianten;
- bewusst **keine** pauschal erfundenen Kurzschluss- oder Schließ-/Ausschaltwerte.

Aktueller datengetriebener 2P-RCD-Gesamtstand:

```text
80 Varianten
```

Die bestehende A/F-Serie blieb unverändert; B/B+ liegt separat.

## 3.2 RCD 4P / 3+N

Die bestehende 72er-Matrix A/B/B+ blieb unverändert.

Mit PR #209 kam eine separate Typ-F-Serie hinzu:

- 25, 40, 63 A;
- 30, 300, 500 mA;
- 9 Varianten;
- keine ungesicherten pauschalen Kurzschluss-/Schaltvermögenswerte.

Aktueller datengetriebener 4P-RCD-Gesamtstand:

```text
81 Varianten
```

## 3.3 Katalog und Z_Cockpit

Seit PR #208 werden RCD-Eigenschaften über die gemeinsame Gerätekatalog-Datenkette geführt.

Technischer Katalog und Z_Cockpit besitzen jetzt getrennte Felder/Filter für:

```text
RCD-Typ
IΔn
```

MCB-`Charakteristik` bleibt davon unabhängig.

Z_Cockpit-Version nach dieser Erweiterung:

```text
Z_Cockpit 1.2
```

---

# 4. RCBO – jetzt Geprüft

Kanonische technische ID:

```text
Z_RCBO_1P_N:RCBO_1P_N
```

Der vorherige Platzhalter wurde mit PR #210 zu einer kombinierten FI/LS-Funktionsdarstellung ausgebaut.

Wesentliche Eigenschaften:

- vier Anschlüsse 1/2/3/4;
- N-Kennzeichnung;
- Prüffunktion;
- Fehlerstromfunktion;
- Überstromfunktion;
- bestehende Bibliotheksnamen bleiben erhalten.

Nicht als konkurrierende Gerätebibliotheken umgebaut:

```text
Z_RCBO.kicad_sym
Z_RCBO_Busbar_1P_N.kicad_sym
```

Gerätebasis:

### Typ A

14 herstellerneutrale Varianten:

```text
6 / 10 / 16 / 20 / 25 / 32 / 40 A
× B / C
× 30 mA
× 6 kA
```

### Typ F

2 konservative Zusatzvarianten auf belegter Basis.

Gesamt:

```text
16 datengetriebene RCBO-Varianten
```

Paketstatus:

```text
quality_status: z_conform
quality_level: Geprüft
```

Für `Praxisgetestet` fehlt weiterhin ein dokumentiertes Beispielprojekt.

---

# 5. Hauptschalter / Lasttrennschalter – jetzt Geprüft

Kanonische Symbole:

```text
Z_MAIN_SWITCH:MAIN_SWITCH
Z_MAIN_SWITCH:MAIN_SWITCH_4P
```

Bedeutung:

- `MAIN_SWITCH` = 2P / L+N;
- `MAIN_SWITCH_4P` = 4P / 3P+N.

Der frühere `HS`-Platzhalter wurde durch echte gekoppelte Schaltkontakte ersetzt. Die Neutralleiterkennzeichnung ist eindeutig.

Herstellerneutrale Geräteserien:

```text
2P: 16 / 25 / 40 / 63 A
4P: 16 / 25 / 40 / 63 A
```

Gesamt:

```text
8 Varianten
```

Alle Varianten sind bewusst `Generic` / `source_status: template`; konkrete Herstellerbreiten und Gehäusedaten werden nicht behauptet.

Paketstatus:

```text
quality_status: z_conform
quality_level: Geprüft
```

## Wichtige Roadmap-Abgrenzung: Lasttrennschalter

Die Taxonomie und das Hauptschalterpaket führen Haupt- und Lastschalter bereits gemeinsam unter:

```text
switching.main_switch
```

`Z_MAIN_SWITCH` ist ausdrücklich als Hauptschalter-/Lasttrennschalter-Paket dokumentiert. Deshalb darf beim nächsten Roadmap-Durchlauf **nicht automatisch ein zweites konkurrierendes Lasttrennschalter-Paket erzeugt werden**.

Nur wenn später ein fachlich klar abweichender Gerätetyp benötigt wird, soll dafür nach Prüfung eine eigene ID eingeführt werden.

---

# 6. Hersteller-Stammdaten – neue kanonische Basis

Mit PR #212 wurde ein echtes Herstellerregister eingeführt:

```text
data/manufacturers/manufacturers.json
```

Die Herstellerseite im Z_Cockpit vereinigt jetzt:

```text
Hersteller-Stammdaten
+
vorhandene technische Gerätedaten
```

Dadurch werden Hersteller bereits angezeigt, auch wenn für sie noch keine konkrete Produktserie im Gerätekatalog existiert.

## 6.1 Aktuell angelegte Hersteller

16 Stammdateneinträge:

1. ABB
2. Siemens
3. Hager
4. Eaton
5. Schneider Electric
6. Doepke
7. Siedle
8. Shelly
9. Theben
10. Eltako
11. Klöckner-Moeller
12. LCN / Issendorff KG
13. Phoenix Contact
14. WAGO
15. Weidmüller
16. Pollmann

Jeder Eintrag besitzt unter anderem:

- stabile ProjectOS-Hersteller-ID;
- Katalogname;
- offiziellen Firmen-/Rechtsnamen;
- Land;
- Website;
- offizielle Prüfquelle;
- Quellenstatus;
- Aktivstatus;
- Suchalias.

## 6.2 Wichtige Sonderfälle

### Klöckner-Moeller

Wird bewusst historisch geführt:

```text
status: INACTIVE
```

Aliase umfassen unter anderem:

```text
Klöckner-Möller
Moeller
Klockner-Moeller
```

Der Eintrag dokumentiert die historische Umbenennung/Übernahme und verhindert, dass alte Gerätebestände unter einem erfundenen aktuellen Hersteller dupliziert werden.

### LCN / Issendorff

Kanonischer Hersteller:

```text
Issendorff KG
Katalogname: LCN
```

Suchalias umfassen auch die häufig verwendete Schreibweise:

```text
LCN Issendorf
```

Die offizielle Schreibweise `Issendorff` mit zwei `f` bleibt kanonisch.

### Phoenix Contact

Kanonischer Name:

```text
Phoenix Contact
```

`Phönix Kontakt` ist als Suchalias berücksichtigt.

## 6.3 Regel für den weiteren Herstellerausbau

Die `Generic`-Serien bleiben bestehen und werden **nicht** durch Herstellerdaten ersetzt.

Neue Herstellerartikel werden als eigene, belegte Hersteller-/Produktserien ergänzt. Artikelnummern, Spulenspannungen, Abmessungen, Ausschaltwerte usw. dürfen nur aus belastbaren Herstellerquellen übernommen werden.

Herstellerstammdaten sind nicht automatisch Produktdaten.

---

# 7. Schütze – jetzt Geprüft

Kanonische technische ID:

```text
Z_CONTACTOR:CONTACTOR
```

Der vorherige Kastenplatzhalter wurde mit PR #213 durch eine echte dreipolige Schütz-Funktionsdarstellung ersetzt.

Anschlusslogik bleibt:

```text
1/L1 – 2/T1
3/L2 – 4/T2
5/L3 – 6/T3
A1 – A2
```

Dargestellt werden:

- drei Hauptschließer;
- mechanische Kopplung der Hauptkontakte;
- eigener Spulenfunktionsblock;
- Referenzkennzeichen `K`.

Herstellerneutrale AC-3-Planungsserie:

```text
9 A
12 A
18 A
25 A
32 A
```

Gemeinsame technische Daten:

```text
poles: 3
main_contacts_no: 3
utilization_category: AC-3
symbol: Z_CONTACTOR:CONTACTOR
footprint_policy: optional
source_status: template
```

Bewusst **nicht** pauschalisiert:

- Spulenspannung;
- AC/DC-Spulenart;
- konkrete Modul-/Gehäusebreite;
- konkrete Hilfskontaktbestückung;
- Herstellerartikelnummern.

Die neutrale Basis wurde gegen aktuelle Schützfamilien von Schneider Electric, Siemens, ABB und Eaton plausibilisiert.

## 7.1 Gerätekatalogschema erweitert

Für Schütze wurden folgende technische Felder im zentralen Gerätekatalogvertrag freigegeben:

```text
main_contacts_no
main_contacts_nc
utilization_category
```

Kontaktanzahlen müssen positive Ganzzahlen sein. Eine nicht vorhandene Kontaktart wird durch **Feldabwesenheit** dargestellt, nicht durch einen künstlichen Wert `0`.

Paketstatus:

```text
quality_status: z_conform
quality_level: Geprüft
```

Für `Praxisgetestet` fehlt weiterhin ein dokumentiertes Beispielprojekt.

---

# 8. Aktueller Paketfortschritt

Kanonische Quelle:

```text
data/Z_PACKAGE_PROGRESS.json
```

Aktuell sind folgende Kernpakete vollständig auf `Geprüft`:

| Paket | Status | Reifegrad | Praxisbeispiel |
|---|---|---|---|
| `Z_MCB` | `z_conform` | Geprüft | fehlt |
| `Z_RCD` | `z_conform` | Geprüft | fehlt |
| `Z_RCBO` | `z_conform` | Geprüft | fehlt |
| `Z_MAIN_SWITCH` | `z_conform` | Geprüft | fehlt |
| `Z_CONTACTOR` | `z_conform` | Geprüft | fehlt |

Damit ist die frühere Aussage aus dem Handover vom 10.08., RCBO und Hauptschalter seien noch `Entwurf`, **überholt**.

---

# 9. CI- und Qualitätsstand

Fachlicher Ausgangscommit vor diesem Handover:

```text
6612911fdd351b33f60545791a43f3ee06e76e93
```

Mergeinhalt:

```text
PR #213 – Schütz: 3P-AC-3-Paket technisch vervollständigen
```

Letzter Main-Lauf:

```text
ProjectOS complete test suite #617
status: completed
conclusion: success
```

Erfolgreich waren unter anderem:

- Repository Health Check;
- vollständige Pytest-Suite;
- Python-Syntaxcheck;
- `Z_` Quality Release Profile;
- KiCad-Bibliotheksvalidator;
- Gerätevarianten-Aktualitätscheck;
- Gerätekatalogvalidator;
- Bibliotheksreferenz;
- Qualitätsbericht;
- Symbolvorschauen;
- 3D-Vorschauen;
- HTML-Bibliotheksreferenz;
- HTML-Gerätekatalog;
- ProjectOS-Projektvalidator;
- Z_Cockpit-Erzeugung.

Der aktuelle fachliche `main` ist damit vollständig grün.

---

# 10. Was beim nächsten Mal **nicht** erneut gemacht werden soll

Nicht ohne ausdrücklichen Benutzerwunsch:

1. MCB-Geometrie neu zeichnen oder „optimieren“.
2. RCD-2P- oder RCD-4P-Geometrie verändern.
3. Z_Cockpit-Bibliotheksansicht grundlegend redesignen.
4. `Generic`-Serien durch Herstellerartikel ersetzen.
5. Herstellerwerte aus Marktüblichkeit oder Erinnerung erfinden.
6. Ein konkurrierendes Lasttrennschalter-Paket erzeugen, obwohl `Z_MAIN_SWITCH` diese Funktion bereits abdeckt.
7. GitHub-Ruleset bearbeiten oder aktivieren; dieser Punkt bleibt separat blockiert.
8. Ein Paket als `Praxisgetestet` markieren, solange kein dokumentiertes Praxis-/Beispielprojekt existiert.

---

# 11. Nächster normaler Einstiegspunkt

Die priorisierte Bibliotheksreihenfolge lautet nach dem jetzt erreichten Stand fachlich:

```text
MCB                -> Geprüft
RCD                -> Geprüft
RCBO               -> Geprüft
Haupt-/Lastschalter-> Geprüft
Schütze            -> Geprüft
Hilfsschalter      -> NÄCHSTER NORMALER BLOCK
Reihenklemmen
Netzteile
Relais
Motorschutz
Überspannungsschutz
Sicherungen
Transformatoren
Messgeräte
Meldegeräte
SPS-Komponenten
```

## Empfohlener Ablauf für Hilfsschalter

Beim nächsten „weiter“:

1. aktuellen `main` prüfen;
2. dieses Handover lesen;
3. Repository nach bereits vorhandenen Hilfsschalter-/Kontakt-Symbolen, Datenserien, Tests und Referenzen durchsuchen;
4. vorhandene IDs und Pin-Konventionen bevorzugt wiederverwenden;
5. reale Herstellerfamilien nur als Plausibilitäts-/Datenquelle nutzen;
6. zuerst eine herstellerneutrale technische Basis festlegen;
7. anschließend Tests, Doku, Generatorartefakte und Paketstatus aufbauen;
8. vollständige CI abwarten;
9. erst bei grüner CI auf `Geprüft` setzen/mergen.

Keine neue Symbol-ID nur deshalb anlegen, weil die Roadmap einen neuen Namen enthält. Erst prüfen, ob eine bestehende Bibliothek die Funktion bereits abdeckt.

---

# 12. Hersteller können parallel ergänzt werden

Der Benutzer hat ausdrücklich gewünscht, Hersteller **zwischendurch parallel** weiter auszubauen.

Bevorzugter Modus:

```text
Generic-Paket fachlich fertigstellen
+
passende reale Hersteller-/Produktserien bei Gelegenheit ergänzen
```

Bereits gewünschte Hersteller sind vollständig im Stammdatenregister vorhanden:

```text
ABB
Siemens
Hager
Eaton
Schneider Electric
Doepke
Siedle
Shelly
Theben
Eltako
Klöckner-Moeller
LCN / Issendorff
Phoenix Contact
WAGO
Weidmüller
Pollmann
```

Für konkrete Produktserien gilt weiterhin: ausschließlich belegte technische Werte und offizielle Herstellerquellen verwenden.

---

# 13. Fortsetzungs-Checkliste für eine neue Sitzung

In dieser Reihenfolge orientieren:

```text
1. git/main-Stand prüfen
2. docs/handover/README.md lesen
3. docs/handover/ARBEITSSTAND_2026-08-12_TAGESABSCHLUSS.md lesen
4. data/Z_PACKAGE_PROGRESS.json prüfen
5. data/manufacturers/manufacturers.json prüfen
6. letzten Main-CI-Lauf prüfen
7. nächsten Block Hilfsschalter starten
```

Zusätzlich bei Bedarf weiterhin lesen:

```text
docs/handover/ARBEITSSTAND_2026-08-10_TAGESABSCHLUSS.md
```

Dieser ältere Gesamt-Handover enthält weiterhin die detaillierte ProjectOS-/Z_Cockpit-Governance, Sicherheitsgrenzen und freigegebenen frühen UI-/Symbolbaselines.

---

# 14. Kurzfassung für den direkten Wiedereinstieg

Wenn in der nächsten Sitzung nur sehr wenig Kontext verfügbar ist, reicht zunächst diese Zusammenfassung:

```text
Repository: Kurzschuss/kicad-din-electrical
Single Source of Truth: main
Fachlicher Stand vor Handover: 6612911fdd351b33f60545791a43f3ee06e76e93
Main-CI #617: SUCCESS

Geprüfte Pakete:
- Z_MCB
- Z_RCD
- Z_RCBO
- Z_MAIN_SWITCH (deckt Haupt- und Lastschalter ab)
- Z_CONTACTOR

RCD 2P: 80 datengetriebene Varianten
RCD 4P: 81 datengetriebene Varianten
RCBO 1P+N: 16 Varianten
Haupt-/Lastschalter: 8 Varianten
Schütz 3P AC-3: 5 Varianten

Herstellerregister: 16 Einträge vorhanden
Generic-Serien bleiben erhalten; Herstellerdaten separat und nur belegt ergänzen.

Nicht ändern ohne ausdrücklichen Wunsch:
- freigegebene MCB-Geometrie
- freigegebene RCD-2P-/4P-Geometrie
- freigegebene Z_Cockpit-Bibliotheksansicht
- GitHub-Ruleset

Nächster normaler Block: Hilfsschalter.
Vor Neuanlage zuerst vorhandene Symbole/IDs/Daten prüfen.
```

Damit ist der Wiedereinstiegspunkt eindeutig dokumentiert.
