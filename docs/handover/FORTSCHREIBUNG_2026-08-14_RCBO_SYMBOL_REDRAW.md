# Fortschreibung 2026-08-14 – RCBO-Symbol neu gezeichnet

## Ausgangspunkt

Nach der Erweiterung der Typ-A-RCBO-Planungsmatrix auf 64 Varianten wurde die vorhandene Symbolgrafik `Z_RCBO_1P_N:RCBO_1P_N` erneut visuell mit einer vorgegebenen RCBO/FI-LS-Referenzdarstellung verglichen.

Die bisherige allgemeine Funktionsdarstellung wurde als nicht ausreichend passend bewertet.

## Freigegebene Referenz

Am 14.08.2026 wurde eine überarbeitete Darstellung visuell abgestimmt und vom Benutzer mit **„jetzt passt es“** freigegeben.

Die freigegebene Darstellung enthält insbesondere:

- Beschriftungen `1`, `3 N`, `2`, `4 N`;
- Test-/Prüfkreis mit `T` und `E` links;
- zwei mechanisch gekoppelte Hauptkontakte;
- Überstromauslöser im L-Zweig;
- Summenstromwandler um L und N mit zwei dargestellten Kernbereichen;
- gestrichelte mechanische Kopplung;
- Betätigungs-/Fehlerstromblock rechts oben;
- Auslöse-/Betätigungsblock rechts unten;
- elektrische Rückführung des unteren rechten Kreises zum Leiter von Klemme `4 / N`.

Während der Abstimmung wurden drei Detailkorrekturen ausdrücklich festgelegt:

1. Der Draht links oben endet vor der gestrichelten Linie und berührt diese nicht.
2. Die Proportionen der rechten Betätigungs-/Auslöseblöcke wurden korrigiert.
3. Die untere rechte Leitung wird mit dem Leiter am Schaltkontakt `4 / N` verbunden.

## GitHub-Stand

Arbeitsbranch:

`agent/rcbo-symbol-reference-redraw`

Dort wurden bereits aktualisiert:

- `symbols/Z_RCBO_1P_N.kicad_sym`
- `tests/test_z_rcbo_1p_n_family.py`
- `docs/04_Reference/Z_RCBO_REFERENCE.md`

Die 64 Typ-A-Varianten bleiben unverändert und referenzieren weiterhin genau ein gemeinsames Symbol:

`Z_RCBO_1P_N:RCBO_1P_N`

## Elektrische Semantik

Es wird weiterhin kein separates 2P-Symbol angelegt. Im Projekt werden 1P+N und 2P für diese Bauart gemeinsam geführt.

Elektrische Pins:

- Pin 1: Eingang L
- Pin 2: Ausgang L
- Pin 3: Eingang N
- Pin 4: Ausgang N

## Noch auszuführen

Vor dem Merge nach `main` müssen im lokalen Repository die generierten Artefakte aktualisiert werden:

- Symbolvorschauen
- Symbolindex / Bibliotheksreferenz
- Qualitätsbericht
- HTML-Referenz
- gegebenenfalls weitere durch die Repository-Generatoren berührte Dateien

Anschließend:

1. vollständige Tests ausführen;
2. Branch pushen;
3. PR gegen `main` öffnen;
4. GitHub-CI abwarten;
5. bei grüner CI per Squash nach `main` mergen.

## Nächster Einstiegspunkt

Nach erfolgreichem Merge ist der RCBO-Block funktional und grafisch abgeschlossen. Danach kann wieder beim allgemeinen KiCad-Ladetest bzw. bei der weiteren Bibliotheksnormalisierung fortgesetzt werden.
