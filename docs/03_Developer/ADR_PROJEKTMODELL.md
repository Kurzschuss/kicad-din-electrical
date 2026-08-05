# ADR – Projektmodell als zentrale Wahrheitsquelle

## Status

Angenommen.

## Kontext

Projektfortschritt, Meilensteine, nächste Aufgaben, Cockpit-Anzeigen und spätere Release-Entscheidungen dürfen nicht in mehreren voneinander unabhängigen Dateien gepflegt werden. Doppelte Pflege würde zu widersprüchlichen Angaben führen.

## Entscheidung

Der fachliche Projektzustand wird zentral in `project_state.yaml` beschrieben.

Aus diesem Modell werden künftig abgeleitet:

- Meilensteinfortschritt,
- Gesamtfortschritt,
- nächste sinnvolle Aufgaben,
- Entwicklungsnavigator,
- Cockpit-Dashboard,
- Roadmap- und Release-Ansichten.

Das Projektmodell enthält keine flüchtigen Laufzeitdaten wie den aktuellen Git-Status, GitHub-Verbindungszustand oder das Ergebnis einer gerade ausgeführten CI-Prüfung. Solche Informationen werden weiterhin zur Laufzeit ermittelt und nur mit dem fachlichen Projektmodell kombiniert.

## Regeln

- Eine Aufgabe besitzt eine projektweit eindeutige ID.
- Zulässige Zustände sind `done`, `in_progress`, `planned` und `blocked`.
- Fortschrittswerte werden berechnet und nicht manuell eingetragen.
- Das GitHub-Ruleset bleibt bis zur gemeinsamen Freigabe als `blocked` markiert.
- Die Projektsprache für sichtbare Bezeichnungen ist Deutsch.
- Änderungen am Modell müssen durch Tests validiert werden.

## Format

`project_state.yaml` verwendet zunächst die JSON-kompatible Teilmenge von YAML. Dadurch kann das Modell ohne zusätzliche Laufzeitabhängigkeit zuverlässig mit der Python-Standardbibliothek gelesen werden. Eine spätere Erweiterung auf vollständiges YAML erfordert eine eigene dokumentierte Architekturentscheidung.

## Folgen

Vorteile:

- keine doppelte Fortschrittspflege,
- reproduzierbare Auswertung,
- einheitliche Informationen in Cockpit, Dokumentation und späteren Releases,
- automatisierte Validierung in CI.

Nachteile:

- jede neue fachliche Aufgabe benötigt eine stabile ID,
- Änderungen am Schema müssen versioniert und migriert werden,
- flüchtige technische Zustände dürfen nicht fälschlich als dauerhafter Projektzustand gespeichert werden.
