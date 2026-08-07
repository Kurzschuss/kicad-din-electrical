# AP-0122 – Portable KiCad-3D-Pfadstrategie

## Ziel

ProjectOS-KiCad-Footprints dürfen keine benutzerspezifischen absoluten 3D-Modellpfade enthalten. Die 3D-Bindung muss nach einem Repository-Clone auf unterschiedlichen Entwicklungsrechnern reproduzierbar konfigurierbar sein.

## Architekturentscheidung

ProjectOS trennt ab jetzt strikt zwischen Entwicklungsquelle und produktiver KiCad-Laufzeit:

```text
Repository / Single Source of Truth
<Documents>/GitHub/kicad-din-electrical
        |
        | run_tests.bat / detect_kicad.bat
        v
produktive KiCad-Laufzeit
<Documents>/kicad
```

Das Repository enthält Quellcode, Tests, Dokumentation und erzeugte bzw. erzeugbare Artefakte. KiCad arbeitet mit den synchronisierten Z_-Bibliotheken und 3D-Modellen aus dem Benutzerordner `Documents/kicad`.

Damit muss KiCad nicht dauerhaft auf einen GitHub-Arbeitsordner zugreifen.

## 3D-Pfadvertrag

ProjectOS verwendet für eigene 3D-Modelle die KiCad-Pfadvariable

```text
Z_PROJECTOS_3DMODEL_DIR
```

Der MCB-Footprint referenziert sein Modell über:

```text
${Z_PROJECTOS_3DMODEL_DIR}/Z_MCB_1P/generated/Z_MCB_1P.wrl
```

`Z_PROJECTOS_3DMODEL_DIR` zeigt auf die produktive KiCad-3D-Laufzeit:

```text
<Documents>/kicad/3dmodels/Z_3DModell.3dshapes
```

und nicht mehr auf `<Repository>/models`.

Die Entwicklungsquelle bleibt separat:

```text
<Repository>/models
```

`detect_kicad.bat` synchronisiert STEP-/STP-/WRL-Artefakte aus `models/` in die produktive 3D-Laufzeit und erhält dabei die relative Ordnerstruktur.

## Namensregel

Die Variable trägt bewusst das Präfix `Z_`. Damit ist sie eindeutig als ProjectOS-/Z_-Ressource erkennbar. Die frühere Arbeitsbezeichnung `PROJECTOS_3DMODEL_DIR` ist verworfen.

## Repository-Verwaltung

`run_tests.bat` stellt Repositoryquelle und KiCad-Laufzeit getrennt dar. Zusätzlich zeigt die Repository-Verwaltung:

- verwendetes `git.exe`,
- lokalen Branch,
- lokalen Commit,
- zugehörigen GitHub-Commit,
- Ahead-/Behind-Status,
- lokale Änderungen.

Git wird über PATH, übliche Git-for-Windows-Pfade und GitHub Desktop gesucht.

Das Repository kann über den Menüpunkt `R` in den Windows-Dokumenteordner unter `GitHub/kicad-din-electrical` installiert werden. Vorhandene Verzeichnisse werden nicht überschrieben. Updates erfolgen ausschließlich per Fast-Forward und werden bei lokalen Änderungen oder divergierenden Historien blockiert.

## Regeln

1. Keine benutzerspezifischen absoluten 3D-Pfade in versionierten Footprints.
2. Keine `${KIPRJMOD}`-Abhängigkeit für ProjectOS-eigene 3D-Bibliotheken.
3. Footprints adressieren ProjectOS-3D-Modelle über `${Z_PROJECTOS_3DMODEL_DIR}`.
4. Repository und produktive KiCad-Laufzeit sind getrennte Ebenen.
5. `models/` im Repository ist Quelle; `Documents/kicad/3dmodels/Z_3DModell.3dshapes` ist Laufzeitkopie.
6. OpenSCAD bleibt Geometrie-Single-Source-of-Truth; STEP und WRL sind reproduzierbare Zielartefakte.
7. Automatische Synchronisation darf vorhandene fremde KiCad-Ressourcen nicht löschen.
8. Repository-Updates dürfen lokale Änderungen nicht überschreiben.

## Abnahmekriterien

AP-0122 ist abgeschlossen, wenn:

- der MCB-Footprint `${Z_PROJECTOS_3DMODEL_DIR}` verwendet,
- die Variable auf die KiCad-Laufzeit zeigt,
- das MCB-WRL aus dem Repository in die KiCad-Laufzeit synchronisiert wird,
- kein absoluter Benutzerpfad im Footprint vorhanden ist,
- Repositoryquelle und KiCad-Laufzeit im Testmenü getrennt angezeigt werden,
- Git lokal inklusive GitHub-Desktop-Installation gefunden werden kann,
- lokale und GitHub-Version vergleichbar sind,
- automatisierte Tests die Architektur absichern,
- das Modell aus der KiCad-Laufzeit ohne rotes X dargestellt wird.

## Status

`in Bearbeitung – Repository/Laufzeit-Trennung implementiert; lokaler Windows- und KiCad-Nachweis steht aus`
