# AP-0076 – Autorisierung von KiCad-Freigabeentscheidungen

## Ziel

Technische KiCad-Freigabeentscheidungen dürfen nur durch eine projektbezogen handlungsberechtigte Person mit wirksamer Rollenberechtigung dauerhaft protokolliert werden.

## Berechtigung

Die verbindliche Berechtigung lautet:

```text
PERM-KICAD-RELEASE-DECIDE
```

Für eine erfolgreiche Entscheidung müssen beide Ebenen erfüllt sein:

1. Die ermittelte Projektfunktion besitzt für das Projekt eine Handlungsvollmacht für die Berechtigung.
2. Die handelnde Rolle der ermittelten Person erteilt dieselbe Berechtigung tatsächlich.

Eine Whitelist oder ein Ausnahmerecht allein genügt für die Freigaberolle nicht. Die protokollierte `acting_role` muss unter den Rollen liegen, die die Berechtigung erteilen.

## Ablauf

```text
Projektverantwortung ermitteln
→ Projektvollmacht prüfen
→ Benutzerautorisierung prüfen
→ handelnde Rolle prüfen
→ Freigabeentscheidung unveränderlich speichern
```

Bei Abwesenheit des Projektleiters kann die deterministisch ermittelte Stellvertretung handeln, sofern Projektvollmacht und Rollenberechtigung ebenfalls vorliegen.

## Komponenten

- `PERM_KICAD_RELEASE_DECIDE`
- `AuthorizedKiCadReleaseDecision`
- `AuthorizedKiCadReleaseService`

## Fehlerkennungen

- `ERR-KICAD-0078`: Projektvollmacht oder Benutzerautorisierung lehnt die Freigabe ab.
- `ERR-KICAD-0079`: Die angegebene handelnde Rolle erteilt die Freigabeberechtigung nicht.

## Persistenzverhalten

Eine abgelehnte Autorisierung erzeugt keinen Eintrag in `projectos_kicad_release_audit`. Erst nach erfolgreicher Prüfung wird die Entscheidung mit der tatsächlich ermittelten handelnden Person und Rolle angehängt.

## Grenzen

Die technische Freigabe ersetzt keine formelle Normen-, Produkt-, Sicherheits- oder Betreiberfreigabe. Zuständigkeiten und Rollen müssen projektspezifisch gepflegt werden.
