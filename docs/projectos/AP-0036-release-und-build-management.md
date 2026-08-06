# AP-0036 – Release-, Versions- und Build-Management

**Status:** Abgeschlossen  
**Sprint:** 003 – Core Implementation

## Ziel

ProjectOS erhält eine reproduzierbare, prüfbare und automatisierbare Release-Grundlage.

## Umsetzung

- Semantic Versioning über `SemanticVersion`
- kontrollierte Erhöhung über `VersionBump`
- unveränderliches `ReleaseManifest`
- SHA-256-Prüfsumme des kanonischen Manifests
- standardkonformes Python-Build-Gerüst in `pyproject.toml`
- GitHub-Actions-Workflow für Tests, Syntaxprüfung, Wheel, Source Distribution und Prüfsummen
- Build-Artefakte werden als Workflow-Artefakt gespeichert

## Tag-Schema

ProjectOS-Releases verwenden:

```text
projectos-vMAJOR.MINOR.PATCH
```

Beispiel:

```text
projectos-v0.15.0
```

## Release-Ablauf

1. Arbeitsstand und Paketversion aktualisieren.
2. Vollständige Testsuite ausführen.
3. Syntaxprüfung durchführen.
4. Wheel und Source Distribution bauen.
5. SHA-256-Prüfsummen erzeugen.
6. Artefakte im GitHub-Workflow speichern.
7. Nach fachlicher Freigabe einen signierten Tag lokal erzeugen und pushen.

## Sicherheitsgrenze

Der Workflow erstellt bewusst keinen GitHub-Release und veröffentlicht nichts in einem Paketindex. Dafür sind später explizite Schreibberechtigungen, Freigaben und Secrets erforderlich. Signierte Tags werden lokal beziehungsweise durch einen gesondert abgesicherten Release-Prozess erzeugt.

## Definition of Done

- SemVer-Modell implementiert und getestet
- Release-Manifest implementiert und getestet
- Build-Konfiguration vorhanden
- Release-Workflow vorhanden
- Prüfsummen und Artefaktspeicherung eingerichtet
- Arbeitsstand und Paketversion aktualisiert
