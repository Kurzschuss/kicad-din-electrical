# AP-0084 – Qualitäts- und Freigabeprüfung der globalen Sicherheitsbesetzung

## Ziel

AP-0084 bewertet die aktuelle globale Sicherheitsbesetzung deterministisch und ohne automatische Änderung von Benutzern oder Verantwortungen.

## Entscheidungen

- `APPROVED`: Die konfigurierte Besetzungsrichtlinie ist erfüllt.
- `REJECTED`: Mindestens eine fachliche Besetzungsanforderung ist verletzt.
- `INSUFFICIENT_DATA`: Die konfigurierte Mindestanzahl historischer Wechsel ist noch nicht erreicht.

## Standardrichtlinie

Standardmäßig gelten folgende Anforderungen:

- globale Hauptverantwortung vorhanden,
- globale Stellvertretung vorhanden,
- Hauptverantwortung aktiv,
- Stellvertretung aktiv,
- beide Verantwortungen unterschiedlichen Personen zugeordnet,
- keine Mindestanzahl historischer Wechsel.

Die Richtlinie ist konfigurierbar. Beispielsweise kann die Stellvertretung für eine begrenzte Projektphase optional sein. Eine solche Lockerung muss ausdrücklich konfiguriert werden.

## Findings

- `ERR-KICAD-0135`: negative Mindestanzahl historischer Wechsel
- `ERR-KICAD-0136`: unzureichende Datenbasis
- `ERR-KICAD-0137`: Hauptverantwortung fehlt
- `ERR-KICAD-0138`: Stellvertretung fehlt
- `ERR-KICAD-0139`: Hauptverantwortung ist inaktiv
- `ERR-KICAD-0140`: Stellvertretung ist inaktiv
- `ERR-KICAD-0141`: Hauptverantwortung und Stellvertretung sind derselben Person zugeordnet

## Grenzen

Das Quality Gate:

- weist keine Personen zu,
- aktiviert oder deaktiviert keine Benutzer,
- ändert keine Rollen oder Berechtigungen,
- ersetzt keine organisatorische oder rechtliche Freigabe,
- bewertet ausschließlich die gespeicherte ProjectOS-Konfiguration.
