# Fortschreibung 2026-08-15 – RCBO Typ A / FI-LS 1P+N / 2P

## Zusammenfassung

Der RCBO-/FI-LS-Arbeitsblock ist abgeschlossen und in `main` integriert.

### Gerätefamilie

Für die Projektbibliothek werden `1P+N` und `2P` als gemeinsame Bauart geführt. Es gibt **kein zweites separates 2P-Symbol**.

Kanonisches Symbol:

```text
Z_RCBO_1P_N:RCBO_1P_N
```

Elektrische Semantik:

- Pin 1: Eingang L
- Pin 2: Ausgang L
- Pin 3: Eingang N
- Pin 4: Ausgang N
- ein geschützter Außenleiter
- Neutralleiter mitgeschaltet

## Typ-A-Planungsmatrix

PR #248 wurde erfolgreich gemergt.

Die Typ-A-Serie umfasst jetzt **64 Varianten**:

- Nennstrom: 6, 10, 13, 16, 20, 25, 32, 40 A
- Bemessungsdifferenzstrom: 10, 30 mA
- Auslösecharakteristik: B, C
- Bemessungsausschaltvermögen: 6, 10 kA
- RCD-Charakteristik: Typ A
- Bauart/Projektbezeichnung: 1P+N / 2P

Rechnung:

```text
8 × 2 × 2 × 2 = 64 Varianten
```

Die bereits vorhandenen Basis-IDs für 30 mA / 6 kA bleiben erhalten.

## Freigegebene Symbolgeometrie

Die vorherige allgemeine RCBO-Funktionsgrafik wurde verworfen und nach visueller Abstimmung ersetzt.

Die freigegebene Darstellung enthält:

- Testkreis `T / E` links
- zwei mechanisch gekoppelte Hauptkontakte
- Überstromauslöser im L-Zweig
- Summenstromwandler um L und N
- rechten Fehlerstrom-/Betätigungsblock
- Anschlussbezeichnungen `1`, `3 N`, `2`, `4 N`
- verkürzte linke obere Leitung, die nicht auf der gestrichelten Kopplungslinie endet
- korrigierte Proportionen der Betätigungsblöcke
- untere rechte Rückführung mit Verbindung zum Leiter/Kontakt an Klemme `4 / N`

PR #249 wurde erfolgreich per Squash nach `main` gemergt.

Merge-Commit:

```text
99aee707ab975e4ba9d7c536c7012c9434417798
```

## Prüfstand

Lokaler Abschlusslauf:

- RCBO-spezifische Tests: 7/7 bestanden
- Gesamttests: 934/934 bestanden
- Bibliotheksvalidator: 0 Fehler, 57 nicht blockierende Hinweise
- erzeugte Gerätevarianten aktuell: 285
- Gerätekatalog: 287 Gerätedateien, 19 Familien, 0 Fehler
- Symbolvorschauen: 75 aktuell
- 3D-Vorschauen: 6 aktuell
- ProjectOS Projektvalidator: 10/10 Prüfungen bestanden, 0 Fehler
- GitHub PR-CI: erfolgreich

Die verbleibenden 57 Validatorhinweise betreffen bereits bekannte fehlende Hersteller-/Datenblattangaben, vorbereitete leere Bibliotheken sowie einige Footprint-/Symbolbibliothekszuordnungen. Sie blockieren den RCBO-Stand nicht.

## Verbindlicher Stand für die Fortsetzung

1. RCBO Typ A mit 64 Varianten ist abgeschlossen.
2. Die freigegebene RCBO-Symbolgeometrie ist in `main`.
3. Für RCBO ist derzeit **keine weitere Symbolneuzeichnung** offen.
4. Als nächstes wieder beim bestehenden Projekt-Backlog ansetzen:
   - lokaler KiCad-Ladetest der Bibliotheken,
   - Z_I-v15-Normalisierungsplanung,
   - offene Hersteller-/Datenblattmetadaten nur bei belastbarer Quelle ergänzen.

`main` bleibt die Single Source of Truth.