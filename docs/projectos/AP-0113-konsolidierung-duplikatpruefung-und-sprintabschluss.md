# AP-0113 – Konsolidierung, Duplikatprüfung und Sprintabschluss

## Ziel

Die seit AP-0090 rekursiv gewachsene Kette aus Audit, Suche, Alarm, Historie und erneuter Autorisierung wird beendet. Neue Sicherheitsfälle verwenden das einheitliche Modul `projectos.security_events`.

## Kanonisches Modell

- `SecurityEvent`
- `SecurityEventKind`
- `SecurityEventSeverity`
- `SecurityEventStatus`
- `SQLiteSecurityEventRepository`

Die Herkunft wird durch `source_type` und `source_id` beschrieben. Abhängigkeiten zwischen Ereignissen werden über `parent_event_id` modelliert. Damit ist keine neue Python-Klasse oder SQLite-Tabelle pro Rekursionsebene erforderlich.

## Kompatibilitätsregel

Die vorhandenen spezialisierten Module aus AP-0075 bis AP-0112 bleiben vorerst lesbar, damit bestehende Daten und Importe nicht zerstört werden. Sie gelten jedoch als eingefrorene Kompatibilitätsschicht:

- keine weitere rekursive Ableitung,
- keine neuen `...attempt_action_attempt...`-Module,
- keine neuen Tabellen für dieselbe Ereignisfolge,
- neue Funktionen ausschließlich über das kanonische Sicherheitsereignismodell.

## Automatische Duplikatprüfung

`tests/test_projectos_repository_consistency.py` prüft:

1. eindeutige AP-Nummern der Dokumentdateien,
2. keine doppelten AP-Einträge im Arbeitsstand,
3. keine mehrfach exportierten Namen in `projectos/__init__.py`,
4. keine mehrfach definierten `ERR-KICAD-*`- oder `WARN-KICAD-*`-Codes in unterschiedlichen Laufzeitmodulen.

## Abschluss

- AP-0112 wird als letzter spezialisierter Kompatibilitätsbaustein abgeschlossen.
- AP-0113 führt das kanonische Modell und die Schutzprüfungen ein.
- Sprint 005 erhält kein automatisches `next_work_package` mehr.
- Weitere Entwicklung wird erst nach einem neuen, fachlich abgegrenzten Sprintziel geplant.

## Offener Qualitätsnachweis

Der vollständige GitHub-Actions-Lauf für den aktuellen Branch-Kopf ist noch ausstehend. Ein erfolgreicher älterer Lauf beweist nicht die neuen Konsolidierungsänderungen.
