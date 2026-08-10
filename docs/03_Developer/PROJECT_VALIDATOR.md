# ProjectOS Projektvalidator

Der Projektvalidator bündelt die repositoryweiten Konsistenzprüfungen in einem einzigen, nicht schreibenden Prüfpfad.

## Aufruf

```text
python -m tools.project_validator
```

Für CI und andere Werkzeuge kann zusätzlich ein maschinenlesbarer JSON-Bericht erzeugt werden:

```text
python -m tools.project_validator --json-output build/Z_PROJECT_VALIDATION.json
```

Der JSON-Bericht verwendet `schema_version: 1` und enthält Gesamtstatus, Prüfungszahlen sowie die einzelnen Prüfergebnisse mit stabilen Kennungen `PRJ-001` bis `PRJ-010`.

## Geprüfte Bereiche

Der Validator prüft aktuell:

1. `PRJ-001` – zentrales Projektmodell `project_state.yaml`;
2. `PRJ-002` – KiCad-Symbol- und Footprintbibliotheken über den bestehenden Bibliotheksvalidator;
3. `PRJ-003` – technischen Gerätekatalog und seine Symbol-/Footprintreferenzen;
4. `PRJ-004` – Aktualität der datengetrieben erzeugten Gerätevarianten;
5. `PRJ-005` – Aktualität von Symbol- und Footprintindex;
6. `PRJ-006` – Aktualität des Bibliotheks-Qualitätsberichts;
7. `PRJ-007` – Aktualität der generierten Symbolvorschauen;
8. `PRJ-008` – Aktualität der HTML-Bibliotheksreferenz;
9. `PRJ-009` – Aktualität des HTML-Gerätekatalogs;
10. `PRJ-010` – Konsistenz der zentralen Z_Cockpit-Seitenregistrierung.

Damit werden bestehende Fachvalidatoren und Generatoren nicht ersetzt oder dupliziert. Der Projektvalidator orchestriert ihre bestehenden Single-Source-of-Truth-Verträge und macht das Gesamtergebnis einheitlich auswertbar.

## Statusmodell

Jede Prüfung besitzt einen der Zustände:

- `ok` – Prüfung vollständig bestanden;
- `warning` – kein blockierender Konsistenzfehler, aber offene Hinweise;
- `error` – blockierender Projektfehler oder Generator-Drift.

Warnungen führen nicht zu einem fehlerhaften Prozess-Exit. Sobald mindestens eine Prüfung den Zustand `error` besitzt, beendet sich der Validator mit Exit-Code `1`.

Der aktuelle Bibliotheksvalidator kann beispielsweise weiterhin Hinweise zu noch nicht gepflegten Hersteller- oder Datenblattfeldern liefern. Diese werden als nicht blockierende Projektwarnung zusammengeführt, ohne den bestehenden Fachvalidator umzudeuten.

## Z_Cockpit

Die Qualitätsseite des Z_Cockpits zeigt den Projektvalidator oberhalb der bestehenden Bibliotheksgesundheit an. Sichtbar sind:

- Gesamtstatus der Projektkonsistenz;
- bestandene Prüfungen;
- Warnungs- und Fehlerzahl;
- jede einzelne `PRJ-*`-Prüfung mit Meldung und optionalen Details.

Die bestehende Bibliotheksansicht wird dadurch nicht verändert.

## CI und Release

Die vollständige ProjectOS-Prüfkette erzeugt den JSON-Bericht unter:

```text
build/Z_PROJECT_VALIDATION.json
```

Auch der ProjectOS-Release-Workflow führt den Projektvalidator vor dem Paket-Build aus. Dadurch kann ein Release nicht mit erkanntem Generator-Drift, ungültigem Projektmodell oder anderen blockierenden Konsistenzfehlern gebaut werden.

## Architekturgrenze

Der Projektvalidator ist bewusst read-only:

- keine Generatorausgabe wird automatisch überschrieben;
- keine Projektkonfiguration wird verändert;
- keine Warnung wird automatisch unterdrückt;
- Fachvalidatoren bleiben Eigentümer ihrer jeweiligen Regeln.

Bei einem Drift meldet der Validator die betroffene Ausgabe. Die Aktualisierung erfolgt weiterhin über den zuständigen Generator und wird anschließend erneut geprüft.
