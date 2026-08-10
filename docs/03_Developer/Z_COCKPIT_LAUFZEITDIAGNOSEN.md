# Z_Cockpit – persistierte Laufzeitdiagnosen

## Ziel

Die Diagnose-Seite des Z_Cockpit kann neben Projektvalidator und repositoryweiter Projektanalyse nun auch die vorhandene ProjectOS-Wissensgraphdiagnose aus einem persistierten Laufzeitzustand anzeigen.

Die Persistenz folgt dem ProjectOS-Prinzip **Quelle speichern, Ableitung reproduzieren**. Deshalb werden keine fertigen Diagnoseergebnisse, Ampelfarben oder Reparaturempfehlungen persistiert.

## Persistierte Quelle

Die fachliche Quelle ist `ProjectOSProjectMemory` mit:

- Wissenselementen;
- typisierten Beziehungen;
- bekannten Message-IDs;
- bekannten Correlation-IDs;
- Zeitstempel des gespeicherten Zustands.

Versionierter Vertrag:

```text
distributions/projectos_project_memory_persistence.py
```

Aktuelle Persistenzversion:

```text
1
```

Abgeleitet und bewusst **nicht** gespeichert werden:

- `ProjectOSKnowledgeDiagnosticsService`-Ergebnisse;
- Z_Cockpit-Diagnosearbeitslisten;
- Ampelzustände;
- Schweregrad-Zählungen;
- Reparaturempfehlungen.

## Lokale Standarddatei

Das Z_Cockpit sucht automatisch nach:

```text
build/PROJECTOS_RUNTIME_MEMORY.json
```

`build/` ist durch `.gitignore` ausgeschlossen. Der Laufzeitzustand wird daher nicht versehentlich als Repository-Quelldatei versioniert.

Fehlt die Datei, bleibt die Diagnose-Seite vollständig nutzbar und zeigt weiterhin Projektvalidator und Projektanalyse. Die fehlende Laufzeitquelle ist **nicht blockierend**.

## Speichern aus einer ProjectOS-Runtime

Eine Runtime persistiert ihren aktuellen Wissensgraphen explizit über:

```python
from distributions.projectos_project_memory_persistence import save_project_memory_state

save_project_memory_state(
    "build/PROJECTOS_RUNTIME_MEMORY.json",
    memory,
    known_message_ids=known_message_ids,
    known_correlation_ids=known_correlation_ids,
)
```

Die Speicherung erfolgt atomar über den vorhandenen ProjectOS-Dateischreibpfad. Die Quelldaten werden dabei validiert; Projekt-ID, Wissens-/Beziehungs-IDs sowie Message-/Correlation-IDs müssen gültige UUIDs sein.

## Laden

```python
from distributions.projectos_project_memory_persistence import load_project_memory_state

state = load_project_memory_state("build/PROJECTOS_RUNTIME_MEMORY.json")
```

Der geladene Zustand enthält wieder ein vollständiges `ProjectOSProjectMemory` und den Diagnosekontext. Beziehungen werden gegen die vorhandenen Wissensknoten validiert.

## Z_Cockpit-Anbindung

Die Cockpit-Brücke liegt unter:

```text
tools/z_cockpit/runtime_diagnostics.py
```

Beim Erzeugen des Cockpits wird die Standarddatei automatisch geprüft. Ist sie vorhanden, wird sie geladen und die bestehende `ZCockpitDiagnosticsWorklistView` neu ausgeführt.

Die Diagnose-Seite erhält dadurch zusätzlich die Quelle:

```text
Laufzeitdiagnose
```

Codes werden für die Cockpitdarstellung mit `RT-` gekennzeichnet, zum Beispiel:

```text
RT-DUPLICATE_SEMANTIC_RELATION
RT-SUPERSESSION_CONFLICT
RT-UNRESOLVED_CAUSATION
RT-UNRESOLVED_CORRELATION
RT-ISOLATED_KNOWLEDGE
```

Ein fehlerfreier persistierter Wissensgraph wird als nicht blockierender `RT-OK`-Hinweis sichtbar. Die fachliche Schwere `info` wird in der Tabelle als **Hinweis** dargestellt und verschlechtert den Gesamtstatus nicht.

## Read-only-Grenze

Das Z_Cockpit verändert den persistierten Wissensgraphen nicht. Es:

1. liest den versionierten Snapshot;
2. validiert ihn;
3. berechnet die vorhandenen ProjectOS-Diagnosen neu;
4. führt diese mit Projektvalidator und Projektanalyse zusammen.

Automatische Reparaturen oder fachliche Entscheidungen werden weiterhin nicht ausgeführt.

## Datenschutz und Repository-Sicherheit

Der Snapshot enthält ausschließlich ProjectOS-Wissensgraphdaten und explizite technische Referenz-IDs. Benutzerverwaltungsbestände, Tokens, Passwörter, Schlüssel und GitHub-Anmeldedaten werden von diesem Persistenzvertrag nicht übernommen.

Da die Standarddatei unter `build/` liegt, bleibt sie ein lokales Laufzeitartefakt. Soll ein Zustand bewusst archiviert werden, muss das außerhalb dieses automatischen Cockpitpfads ausdrücklich erfolgen.

## Fehlerverhalten

- Datei fehlt: keine Laufzeitdiagnose, kein Fehler.
- Nicht unterstützte Persistenzversion: Laden wird abgewiesen.
- Ungültige UUIDs: Laden wird abgewiesen.
- Beziehung auf unbekannten Wissensknoten: Laden wird abgewiesen.
- Projekt-ID-Konflikt: Laden wird abgewiesen.

Damit werden beschädigte oder fachlich inkonsistente Persistenzdaten nicht stillschweigend als gültige Laufzeitquelle angezeigt.

## Tests

Die Tests decken insbesondere ab:

- Roundtrip von Wissensknoten und Beziehungen;
- Erhalt von Message-/Correlation-IDs;
- Versionsprüfung;
- Cross-Project-Abweisung;
- erneute Berechnung von Warnungen und Hinweisen aus dem persistierten Graphen;
- nicht blockierendes Verhalten bei fehlender Datei;
- Integration in die vorhandene Diagnose-Seite.

Technische Tests:

```text
distributions/test_projectos_project_memory_persistence.py
tests/test_runtime_diagnostics_persistence.py
```

## Architekturentscheidung

Die bestehende ProjectOS-Projektbundle-v4-Persistenz für Benutzerverwaltung wird durch diese Änderung **nicht** umgedeutet oder erweitert. Der Laufzeit-Wissensgraph bleibt ein separater lokaler Runtime-Snapshot. Dadurch werden bestehende Projektdateien nicht migriert und die Diagnoseableitung bleibt unabhängig aktualisierbar.
