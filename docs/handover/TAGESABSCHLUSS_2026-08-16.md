# Tagesabschluss 16.08.2026

## Zusammenfassung

Der heutige Arbeitstag diente der Fortsetzung des lokalen KiCad-Kompatibilitäts- und GUI-Prüfblocks auf dem Branch `agent/kicad-local-symbol-load-test`.

Der automatische KiCad-Ladetest war bereits erfolgreich. Heute wurde insbesondere die manuelle GUI-Prüfung des RCBO/FI-LS-Symbols `Z_RCBO_1P_N:RCBO_1P_N` durchgeführt und die Symbolgeometrie anhand der Referenz iterativ korrigiert.

Ergebnis für RCBO/FI-LS: **GUI-Sichtprüfung PASS / vom Anwender freigegeben**.

## GitHub-/Arbeitsstand

Repository:

```text
Kurzschuss/kicad-din-electrical
```

Aktiver Prüfbranch:

```text
agent/kicad-local-symbol-load-test
```

Wichtig:

- `main` bleibt die Single Source of Truth für bereits gemergte Arbeit.
- Die heutigen KiCad-Kompatibilitäts- und GUI-Korrekturen liegen weiterhin im Prüfbranch.
- Der Prüfbranch soll erst nach Abschluss der restlichen manuellen Z_I-GUI-Kontrolle nach `main` übernommen werden.

## Automatischer echter KiCad-Test – bestätigter Stand

Der lokale Test mit KiCad 10.99 hatte bereits erfolgreich **PASS** erreicht.

Verwendete CLI:

```text
C:\Program Files\KiCad\10.99\bin\kicad-cli.exe
```

Bestätigt:

- RCBO: 1 logisches Symbol, 1/1 gerendert;
- Z_I: 52 logische Top-Level-Symbole;
- 55 Unit-SVGs exportiert, bedingt durch das Mehrfacheinheiten-Schütz;
- Re-Save-Test für RCBO und Z_I erfolgreich;
- erneuter Export der Re-Save-Kopien erfolgreich;
- `Contactor_3P_1NO_1NC`: 4/4 Units strukturell vorhanden.

Während dieses Prüfblocks wurden zuvor außerdem korrigiert:

1. PowerShell-Parserfehler bei `"$Label:"` → `"${Label}:"`;
2. ungültige freie `; ...`-Kommentarzeilen in `Z_RCBO_1P_N.kicad_sym` entfernt;
3. Testlogik von 52 erwarteten SVG-Dateien auf 52 logische Symbole / 55 Unit-SVGs korrigiert.

## RCBO/FI-LS – heutige GUI-Prüfung

Ausgangsbasis war die im Schaltplaneditor direkt aus dem Prüfbranch geladene Bibliothek.

Zunächst wurde erkannt, dass eine ältere global registrierte RCBO-Kopie angezeigt worden war. Für die eigentliche Prüfung wurde deshalb die Branch-Datei projektspezifisch unter einem eindeutigen Test-Nickname geladen.

### Heute korrigierte bzw. verifizierte Punkte

- automatische KiCad-Pintexte ausgeblendet, damit die sichtbaren Klemmenbezeichnungen nicht doppelt erscheinen;
- sichtbare Klemmenkennzeichnung bleibt `1 / 3 N / 2 / 4 N`;
- drei gekoppelte Schaltkontakte in der gewünschten Anordnung;
- mittlerer Schalterwinkel gegenüber den anderen Kontakten angepasst;
- gestrichelte mechanische Kopplung tiefer und durch die Kontaktgruppe geführt;
- mechanische Kopplung läuft durch den rechten Betätigungsblock;
- obere Drahtbrücke links korrigiert;
- rechter Betätigungsblock und darunterliegender Auslöseblock in der Höhe angepasst;
- untere rechte Rückführung zur Klemme `4/N` beibehalten;
- Summenstromwandler und beide Leiter beibehalten;
- linker Testzweig mehrfach an die Referenz angeglichen;
- final: links E-förmige Betätigungsgeometrie statt Textbuchstabe, mit schräger mechanischer Anlenkung zum Testzweig;
- Widerstand und eigener Testschalter links bleiben als Teil des Testkreises erhalten.

Die zuletzt in KiCad sichtbare Fassung wurde vom Anwender mit

```text
sollte passen
```

freigegeben.

Damit ist die **RCBO-Neuzeichnung für diesen Prüfblock abgeschlossen**.

## RCBO-Familie – unveränderter fachlicher Umfang

Die Typ-A-RCBO-Familie bleibt als gemeinsame Bauart `1P+N / 2P` umgesetzt:

- kein separates zweites 2P-Symbol;
- 64 Typ-A-Planungsvarianten;
- Nennstrom: 6 / 10 / 13 / 16 / 20 / 25 / 32 / 40 A;
- Bemessungsdifferenzstrom: 10 / 30 mA;
- Auslösecharakteristik: B / C;
- Ausschaltvermögen: 6 / 10 kA;
- RCD-Typ A.

Die Variantenmatrix selbst ist bereits in `main` integriert. Die heutigen Arbeiten betreffen die KiCad-Kompatibilität und die sichtbare Referenzgeometrie im Prüfbranch.

## Z_I – aktueller Stand

`Z_I_ElectricalComponents` v14 ist bereits in `main` integriert:

- 52 Top-Level-Symbole;
- 254 KiCad-Pindefinitionen;
- 8 direkte Funktionsdubletten im Overlap-Audit;
- 3 strukturelle Schütz-Overlaps;
- 41 Symbole ohne direktes kanonisches Gegenstück.

Der echte lokale KiCad-Test bestätigt, dass diese Bibliothek vom KiCad-Parser geladen und vollständig gerendert werden kann.

## Offene Arbeit / nächster Einstiegspunkt

Beim nächsten Fortsetzen **nicht erneut mit RCBO beginnen**.

Direkt weiter mit der restlichen manuellen KiCad-GUI-Endkontrolle:

1. `Contactor_3P_1NO_1NC` im Symbolwähler öffnen und Units A–D einzeln kontrollieren.
2. Potential-/Pfeilsymbole auf Fangpunkte und sinnvolle Ausrichtung prüfen.
3. Alle 52 Z_I-Symbole auf Textrotation, abgeschnittene Texte, unplausible Pinpositionen und auffällige Geometrie prüfen.
4. Auffälligkeiten einzeln im Prüfbranch korrigieren und nach jeder größeren Korrekturrunde den echten KiCad-Ladetest erneut ausführen.
5. Wenn die gesamte GUI-Prüfung PASS ist, Prüfbranch nach `main` übernehmen.
6. Danach mit der geplanten **Z_I-v15-Normalisierung** beginnen.

## Merksatz für die nächste Sitzung

**RCBO ist GUI-seitig freigegeben. Nächster Prüfpunkt ist `Contactor_3P_1NO_1NC`, Units A–D.**
