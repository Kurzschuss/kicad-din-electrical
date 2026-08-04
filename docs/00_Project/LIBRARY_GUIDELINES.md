# Qualitätshandbuch für Bibliothekspakete

Dieses Dokument wird als verbindliches Qualitätshandbuch für neue Gerätefamilien und Bibliothekspakete ausgebaut.

## Ziel

Neue Geräte sollen nicht als einzelne, voneinander getrennte Dateien entstehen, sondern als vollständig nachvollziehbare Pakete.

Ein vollständiges Gerätepaket umfasst – soweit fachlich sinnvoll:

- Symbolbibliothek
- optionalen Footprint
- Gerätekatalogeintrag
- Geräteserie oder Variantenbeschreibung
- SVG-Vorschau
- HTML-Dokumentation
- Benutzerdokumentation
- Beispielprojekt
- automatisierte Tests
- Qualitätsstatus

## Verbindliche Themen des Handbuchs

Das Qualitätshandbuch wird schrittweise um folgende Regeln ergänzt:

- Aufbau und Benennung neuer Symbole
- Pflichtfelder und Metadaten
- Entscheidungskriterien für `required`, `optional` und `none`
- Aufnahme von Geräten in den Gerätekatalog
- Anforderungen an Geräteserien und Varianten
- erforderliche Dokumentation
- erforderliche Tests und Validatorprüfungen
- Kriterien für die Qualitätsstufen
- Nachweis einer praktischen Verwendung

## Sprach- und Benennungsregel

Deutsch ist die verbindliche Primärsprache des Projekts.

### Benutzerseitige Inhalte

Folgende Inhalte werden grundsätzlich auf Deutsch geführt:

- Benutzerdokumentation und Anleitungen
- Menüs, Konsolenausgaben und Fehlermeldungen
- HTML-Katalog und sichtbare Gerätebezeichnungen
- Beschreibungen, Hinweise und Qualitätsberichte
- Namen von Gerätefamilien in der deutschsprachigen Darstellung

Beispiele sind `Leitungsschutzschalter`, `Fehlerstrom-Schutzeinrichtung`, `Hauptschalter` und `Überspannungs-Schutzeinrichtung`.

### Technische Kennungen

Etablierte internationale Fachkürzel bleiben für stabile technische Kennungen, Dateinamen, Bibliotheksnamen und IDs zulässig und erwünscht. Dazu gehören insbesondere `MCB`, `RCD`, `RCBO` und `SPD`.

Bestehende Kennungen wie `Z_MCB`, `Z_RCD`, `protection.mcb` oder `generic.mcb-1p-b16-template` werden nicht allein aus sprachlichen Gründen umbenannt. Dadurch bleiben Projekte, Verweise und Generatorausgaben kompatibel.

Eigene Bibliotheken, Symbole, Footprints, 3D-Modelle und Designblöcke tragen weiterhin verbindlich das Präfix `Z_`.

### Zweisprachige Gerätemetadaten

Neue oder fachlich überarbeitete Gerätekatalogeinträge erhalten zusätzlich zu den stabilen technischen Kennungen zweisprachige Anzeigenamen:

```json
{
  "name_de": "Leitungsschutzschalter B16, 1-polig",
  "name_en": "Miniature Circuit Breaker B16, 1-pole",
  "abbreviation": "MCB"
}
```

Dabei gilt:

- `name_de` ist die primäre sichtbare Bezeichnung.
- `name_en` ermöglicht internationale Suche und spätere englische Ausgaben.
- `abbreviation` enthält ein etabliertes, sprachneutrales Fachkürzel.
- Technische IDs und Bibliotheksverweise werden nicht aus den Anzeigenamen abgeleitet.
- Generatoren und Katalogausgaben verwenden standardmäßig `name_de`; Englisch ist eine zusätzliche Darstellung.

Bestehende Katalogdaten werden schrittweise migriert. Neue Gerätefamilien dürfen nur noch mit deutschen und englischen Anzeigenamen angelegt werden.

## Qualitätsstufen

### Entwurf

Die Struktur ist vorhanden, aber das Paket befindet sich noch im Aufbau. Einzelne Bestandteile oder Nachweise können fehlen.

### Geprüft

Symbol, Dokumentation, Katalogdaten und Tests sind vollständig. Alle automatisierten Prüfungen sind erfolgreich, und die fachliche Prüfung wurde dokumentiert.

### Praxisgetestet

Das geprüfte Paket wurde zusätzlich in mindestens einem realen oder realitätsnahen KiCad-Projekt eingesetzt. Erkenntnisse aus diesem Einsatz wurden berücksichtigt.

## Grundsatz

Ein Gerät gilt erst dann als vollständig, wenn das gesamte Paket nachvollziehbar dokumentiert und geprüft ist. Dadurch sollen viele halbfertige Symbole vermieden und stattdessen schrittweise verlässliche, professionell nutzbare Bibliothekseinträge aufgebaut werden.
