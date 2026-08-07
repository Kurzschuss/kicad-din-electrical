# AP-0114 – Sprint 006 starten: MCB-Goldstandard als Referenzpaket

## Ziel

Sprint 006 beginnt mit der ersten fachlich abgegrenzten Validierungsdomäne aus Architecture Freeze 1.0: MCB. Der Leitungsschutzschalter wird als erstes vollständiges Gerätepaket umgesetzt und dient danach als verbindliche Referenz für weitere Schutzgerätefamilien.

## Ausgangspunkt

- Sprint 001 bis Sprint 005 sind abgeschlossen.
- AP-0001 bis AP-0113 sind abgeschlossen.
- Der lokale vollständige Prüfweg ist erfolgreich: Repository-Health-Check, vollständige Testsuite, Python-Syntaxprüfung und Z_-Qualitätsprüfung.
- `initial_validation_domains` enthält MCB und RCCB.
- GitHub-Issue #87 definiert den MCB-Goldstandard als erstes vollständiges Gerätepaket.

## Sprintziel

Zunächst wird ausschließlich der MCB 1-polig als Referenzgerät vollständig geprüft und dokumentiert. Weitere Polzahlen und Varianten werden erst nach Abschluss des Referenzpakets abgeleitet.

## Verbindlicher Umfang für den MCB-Goldstandard

1. MCB-Referenzsymbol 1P fachlich und grafisch prüfen.
2. Symbolstandard für Schutzgeräte vollständig anwenden.
3. SVG-Vorschau erzeugen.
4. Einheitliche Fachdokumentation erstellen.
5. Herstellerneutralen Gerätekatalogeintrag anlegen.
6. Geräteserie und Variantenkonzept vorbereiten.
7. Technische HTML-Darstellung ergänzen.
8. Kleines realistisches KiCad-Beispielprojekt erstellen.
9. Automatisierte Tests ergänzen.
10. Qualitätsstatus von `Entwurf` erst nach vollständigem Nachweis auf `Geprüft` setzen.

## Reihenfolge

AP-0114 legt Sprintziel, Grenzen und Nachweisführung fest. Die fachliche und grafische Bestandsaufnahme des vorhandenen MCB-1P-Artefakts ist das nächste Arbeitspaket. Es werden noch keine weiteren MCB-Varianten und noch keine RCCB-Implementierungen begonnen.

## Definition of Done für AP-0114

- Sprint 006 ist im Arbeitsstand angelegt.
- MCB ist als aktive Validierungsdomäne festgelegt.
- Issue #87 ist als fachlicher Bezug dokumentiert.
- Der Umfang des MCB-1P-Goldstandards ist eingefroren.
- Das nächste Arbeitspaket ist eindeutig die Bestandsaufnahme und Validierung des vorhandenen MCB-1P-Pakets.
