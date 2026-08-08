# Projektdienst

**Dokument-ID:** PLT-0003  
**Titel:** Fachlicher Dienstvertrag für Projekte  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformdienst  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert die fachlichen Operationen und Garantien für Projekte. `PROJECT_MODEL.md` definiert, was ein Projekt ist; dieses Dokument definiert Erzeugen, Öffnen, Ändern, Validieren, Speichern, Speichern unter, Archivieren und Wiederherstellen.

## 2. Grundprinzipien

1. Projektidentität bleibt stabil.
2. Änderungen sind explizit und nachvollziehbar.
3. Ungültige Zustände werden nicht als erfolgreich gespeichert gemeldet.
4. Persistenzänderungen werden erst nach erfolgreichem Abschluss wirksam.
5. Fehler verändern den zuvor gültigen internen Zustand nicht stillschweigend.
6. Repository, Workspace und Projekt bleiben getrennt.
7. Offline-Betrieb bleibt ein regulärer Betriebsfall.

## 3. Erzeugen und Öffnen

Beim Erzeugen werden Projektidentität, Schema, Pflichtmetadaten, Lebenszyklusstatus, Verantwortungsreferenzen und aktivierte Domänen validiert. Beim Öffnen werden Projektidentität, Schema, Version, Referenzen, Kompatibilität, Savepoint und Änderungsstatus geprüft. Ein fehlgeschlagener Öffnungsvorgang darf keinen teilweise geladenen Zustand als aktiv melden.

## 4. Ändern und Validieren

Änderungen erfolgen gegen einen bekannten Projektzustand. Vor Übernahme werden erwartete Version, Berechtigungskontext, Schema, Lebenszyklusregeln, Beziehungen und Plattforminvarianten geprüft. Eine angenommene Änderung markiert das Projekt als geändert, solange kein neuer erfolgreicher Savepoint gesetzt wurde.

## 5. Speichern

Speichern übernimmt den aktuellen validierten Zustand dauerhaft am bestehenden Speicherziel. Der Vorgang muss atomar oder fachlich äquivalent atomar sein: Der bisher gültige dauerhafte Zustand darf bei einem Fehler nicht durch einen unvollständigen Zustand ersetzt werden.

Erst nach erfolgreich abgeschlossenem Schreiben dürfen Savepoint, gespeicherter Status und speicherbezogene interne Metadaten aktualisiert werden.

## 6. Speichern unter

`Speichern unter` schreibt den aktuellen Projektzustand an ein neues Speicherziel. Bis zum vollständigen Erfolg bleibt das bisherige Speicherziel maßgeblich.

Vor erfolgreich abgeschlossenem Schreiben dürfen nicht dauerhaft geändert werden:

- intern geführter Projektpfad bzw. Speicherziel;
- aktueller Projektzustand;
- Savepoint;
- Undo-/Redo-Historie;
- Änderungsstatus.

Erst nach vollständigem Erfolg darf das neue Ziel intern übernommen werden.

## 7. Fehlersemantik bei Speichern

Schlägt ein Speichervorgang fehl:

1. bleibt der interne Projektzustand unverändert;
2. bleibt die Undo-/Redo-Historie unverändert;
3. bleibt der letzte erfolgreiche Savepoint unverändert;
4. bleibt das Projekt als geändert markiert, wenn vorher Änderungen vorlagen;
5. bleibt die bestehende gültige Projektdatei erhalten;
6. werden temporäre Schreibartefakte entfernt oder eindeutig als unvollständig behandelt;
7. wird der Fehler ausdrücklich gemeldet.

## 8. Fehlersemantik bei Speichern unter

Schlägt `Speichern unter` fehl:

1. bleibt das intern geführte Speicherziel auf dem bisherigen Projektpfad;
2. bleibt der aktuelle interne Projektzustand unverändert;
3. bleibt die Undo-/Redo-Historie unverändert;
4. bleibt der Savepoint unverändert;
5. bleibt der Änderungsstatus erhalten;
6. bleibt die bisherige Projektdatei erhalten;
7. darf die neue Zieldatei nicht als gültiges Projekt zurückbleiben;
8. dürfen temporäre Dateien am neuen Ziel nicht als autoritative Projektdateien zurückbleiben;
9. darf das neue Ziel intern erst nach vollständigem Erfolg übernommen werden.

## 9. Atomare Persistenz

Fachlich atomar bedeutet: Entweder wird der vollständige neue Zustand gültig übernommen oder der bisherige gültige Zustand bleibt erhalten. Die konkrete technische Umsetzung ist Implementierungsdetail.

## 10. Savepoint und Undo/Redo

Arbeitszustand, letzter erfolgreich gespeicherter Zustand und Änderungsstatus werden getrennt geführt. Ein fehlgeschlagener Speichervorgang erzeugt keinen Savepoint. Ein Persistenzversuch darf die Undo-/Redo-Historie nicht allein durch den Versuch verändern.

## 11. Versionskonflikte

Ein unbekannter neuerer dauerhafter Zustand darf nicht stillschweigend überschrieben werden. Erkannte Konflikte müssen ausdrücklich gemeldet werden.

## 12. Archivieren und Wiederherstellen

Archivieren beendet die aktive Bearbeitung, ohne Identität und notwendige Historie zu löschen. Wiederherstellung erfolgt unter Prüfung von Schema, Version, Kompatibilität und erforderlichem Berechtigungskontext.

## 13. Offline-First

Öffnen, Ändern, Validieren und lokales Speichern müssen im vorgesehenen lokalen Betriebsumfang ohne permanente Netzwerkverbindung möglich sein. Optionale externe Dienste dürfen lokale Persistenz nicht unnötig blockieren.

## 14. Autorisierung

Der Projektdienst definiert keine Rollen oder Berechtigungen. Geschützte Operationen beachten eine von der Autorisierungsplattform bereitgestellte Entscheidung oder einen prüfbaren Autorisierungskontext.

## 15. Ereignisse

Erfolgreiche Operationen können Ereignisse wie `Projekt erstellt`, `Projekt geändert`, `Projekt gespeichert`, `Projekt unter neuem Ziel gespeichert`, `Projekt archiviert` oder `Projekt wiederhergestellt` erzeugen. Ein fehlgeschlagener Speichervorgang darf kein Erfolgsereignis erzeugen.

## 16. Invarianten

1. Fehlgeschlagenes Speichern erzeugt keinen neuen Savepoint.
2. Fehlgeschlagenes Speichern unter ändert das intern maßgebliche Speicherziel nicht.
3. Persistenzfehler verändern nicht stillschweigend den fachlichen Projektzustand.
4. Undo-/Redo-Historie bleibt bei fehlgeschlagenen Persistenzoperationen unverändert.
5. Eine gültige bestehende Projektdatei wird nicht durch einen unvollständigen Zustand ersetzt.
6. Erfolg wird erst nach vollständig abgeschlossenem dauerhaften Schreiben gemeldet.
7. Projektidentität bleibt von Speicherziel und Repository unabhängig.
8. Archivierung ist nicht Löschung.
9. Versionskonflikte werden nicht stillschweigend überschrieben.

## 17. Nicht festgelegt

Nicht festgelegt werden Dateiformat, technische Atomaritätsmechanismen, Pfad- oder URI-Syntax, Undo-/Redo-Datenstruktur, Locking, Backup, GUI-Fehlerdarstellung oder Cloud-Synchronisation.

## 18. Abhängigkeiten

- `PLATFORM_MODEL.md`
- `PROJECT_MODEL.md`
- `OBJECT_SERVICE.md`
- `SCHEMA_MODEL.md`
- `RELATION_MODEL.md`
- `ADR-0004-core-referenzen-und-schema-bootstrap.md`

## 19. Ergebnis

Erst ein vollständig erfolgreicher atomarer Schreibvorgang darf Savepoint, Speicherziel oder gespeicherten Status verändern. Fehler beim Speichern oder Speichern unter lassen den zuvor gültigen Projekt- und Historienzustand unverändert.
