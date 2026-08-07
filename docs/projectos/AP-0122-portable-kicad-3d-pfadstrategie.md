# AP-0122 – Portable KiCad-3D-Pfadstrategie

## Ziel

ProjectOS-KiCad-Footprints dürfen keine benutzerspezifischen absoluten 3D-Modellpfade enthalten. Die 3D-Bindung muss nach einem Repository-Clone auf unterschiedlichen Entwicklungsrechnern reproduzierbar konfigurierbar sein.

## Ausgangslage

AP-0121 hat nachgewiesen, dass `Z_MCB_1P.step` und `Z_MCB_1P.wrl` von KiCad korrekt dargestellt werden können. Ein direkter Windows-Pfad funktioniert technisch, ist aber nicht portabel.

Die bisherige Footprint-Referenz

```text
${KIPRJMOD}/../../models/Z_MCB_1P/generated/Z_MCB_1P.step
```

ist für einen wiederverwendbaren Bibliotheks-Footprint ungeeignet, weil `${KIPRJMOD}` vom jeweils geöffneten KiCad-Projekt abhängt.

## Entscheidung

ProjectOS führt für eigene 3D-Modelle die KiCad-Pfadvariable im Z_-Namensraum

```text
Z_PROJECTOS_3DMODEL_DIR
```

ein.

Der MCB-Footprint referenziert sein Modell künftig ausschließlich über:

```text
${Z_PROJECTOS_3DMODEL_DIR}/Z_MCB_1P/generated/Z_MCB_1P.wrl
```

`Z_PROJECTOS_3DMODEL_DIR` zeigt lokal auf den Repository-Ordner `models`.

Beispiel Windows:

```text
C:/Users/<Benutzer>/Documents/GitHub/kicad-din-electrical/models
```

Dieser konkrete absolute Wert ist nur lokale Konfiguration und wird nicht in Bibliotheksdateien versioniert.

## Namensregel

Die Variable trägt bewusst das Präfix `Z_`. Damit ist sie eindeutig als ProjectOS-/Z_-Ressource erkennbar und folgt der bestehenden Namenskonvention der eigenen KiCad-Ressourcen. Die frühere Arbeitsbezeichnung `PROJECTOS_3DMODEL_DIR` ist verworfen und darf nicht als endgültiger Vertrag verwendet werden.

## Warum WRL im Footprint

Für die KiCad-Bibliotheksbindung wird zunächst das im Praxislauf bestätigte WRL-Artefakt verwendet. STEP bleibt parallel als reproduzierbares neutrales CAD-Austauschformat erhalten.

## Regeln

1. Keine Pfade mit `C:/Users/...` oder anderen benutzerspezifischen Verzeichnissen in versionierten Footprints.
2. Keine Abhängigkeit der Bibliotheksobjekte von `${KIPRJMOD}` für ProjectOS-eigene 3D-Bibliotheken.
3. ProjectOS-eigene Modelle werden über `${Z_PROJECTOS_3DMODEL_DIR}` adressiert.
4. Der lokale Variablenwert zeigt auf `<Repository>/models`.
5. OpenSCAD bleibt Geometrie-Single-Source-of-Truth; STEP und WRL bleiben erzeugte Artefakte.
6. Die Pfadregel wird durch automatisierte Tests abgesichert.

## Lokale KiCad-Konfiguration

In KiCad wird unter den konfigurierbaren 3D-/Umgebungs-Pfaden die Variable `Z_PROJECTOS_3DMODEL_DIR` auf den lokalen `models`-Ordner des geklonten Repositorys gesetzt.

Danach darf der Footprint keine benutzerspezifische Pfadangabe mehr benötigen.

## Abnahmekriterien

AP-0122 ist abgeschlossen, wenn:

- der MCB-Footprint `${Z_PROJECTOS_3DMODEL_DIR}` verwendet,
- die verworfene Arbeitsbezeichnung `${PROJECTOS_3DMODEL_DIR}` nicht mehr verwendet wird,
- kein `${KIPRJMOD}` für die MCB-3D-Bindung verbleibt,
- kein absoluter Benutzerpfad im Footprint vorhanden ist,
- ein Test diese Regeln absichert,
- das Modell nach lokaler Konfiguration der Variablen in KiCad ohne rotes X geladen wird.

## Status

`in Bearbeitung – Z_-Pfadvertrag implementiert, automatisierter und lokaler KiCad-Nachweis folgen`
