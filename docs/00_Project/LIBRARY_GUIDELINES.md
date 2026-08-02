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

## Qualitätsstufen

### Entwurf

Die Struktur ist vorhanden, aber das Paket befindet sich noch im Aufbau. Einzelne Bestandteile oder Nachweise können fehlen.

### Geprüft

Symbol, Dokumentation, Katalogdaten und Tests sind vollständig. Alle automatisierten Prüfungen sind erfolgreich, und die fachliche Prüfung wurde dokumentiert.

### Praxisgetestet

Das geprüfte Paket wurde zusätzlich in mindestens einem realen oder realitätsnahen KiCad-Projekt eingesetzt. Erkenntnisse aus diesem Einsatz wurden berücksichtigt.

## Grundsatz

Ein Gerät gilt erst dann als vollständig, wenn das gesamte Paket nachvollziehbar dokumentiert und geprüft ist. Dadurch sollen viele halbfertige Symbole vermieden und stattdessen schrittweise verlässliche, professionell nutzbare Bibliothekseinträge aufgebaut werden.
