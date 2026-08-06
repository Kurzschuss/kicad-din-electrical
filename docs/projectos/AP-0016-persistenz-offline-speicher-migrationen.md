# AP-0016 – Persistenzmodell, Offline-Datenspeicher und Migrationen

**Status:** Abgeschlossen  
**Version:** 1.0  
**Sprint:** 002 – Core Object Model  
**Abhängigkeiten:** AP-0005, AP-0007, AP-0008, AP-0010, AP-0012, AP-0013, AP-0014, AP-0015, ADR-0001, ADR-0002, ADR-0003

## 1. Ziel

Dieses Arbeitspaket definiert die verbindliche Persistenzarchitektur von ProjectOS.

Die Persistenz muss:

- vollständig offline funktionieren,
- Aggregate und Wertobjekte konsistent speichern,
- Transaktionen unterstützen,
- Versions- und Revisionskonflikte erkennen,
- Ereignis-Outbox und Audit-Trail zuverlässig führen,
- Sicherungen und Wiederherstellung ermöglichen,
- Schemaänderungen über nachvollziehbare Migrationen verarbeiten,
- von der Domänenschicht technisch entkoppelt bleiben.

## 2. Architekturgrundsätze

- Die Domänenschicht kennt keine konkrete Speichertechnologie.
- Repository-Schnittstellen werden in der Domäne definiert, Adapter in der Infrastruktur implementiert.
- Der lokale Datenspeicher ist die primäre Arbeitsquelle.
- Cloud- und GitHub-Systeme sind optionale Integrationen und keine Voraussetzung für den Betrieb.
- Gespeicherte Aggregate müssen nach dem Laden wieder alle Invarianten erfüllen.
- Persistenzmodelle dürfen Domänenobjekte nicht ersetzen.
- Laufzeitdaten, Konfiguration, Projektinhalte, Auditdaten und Sicherungen werden getrennt behandelt.

## 3. Speicherbereiche

ProjectOS unterscheidet folgende Speicherbereiche:

| Bereich | Zweck |
|---|---|
| Konfiguration | versionierte System- und Domänenkonfiguration |
| Projektbestand | fachliche Projekt- und Komponentenobjekte |
| Laufzeitdaten | Warteschlangen, Outbox, Dead Letter, Sperren |
| Audit | unveränderliche Änderungsnachweise |
| Lesemodelle | optimierte Abfrage- und Cockpitdaten |
| Simulation | isolierte Szenarien, Zustände und Ergebnisdaten |
| Sicherungen | konsistente Sicherungsstände |
| Migration | Protokolle und Status ausgeführter Migrationen |

## 4. Standard-Datenspeicher

Für die erste Implementierungsstufe wird ein eingebetteter, transaktionaler lokaler Datenspeicher vorgesehen.

Anforderungen:

- keine Serverinstallation,
- Betrieb ohne Netzwerk,
- ACID-Transaktionen,
- Fremdschlüssel und Eindeutigkeitsregeln,
- Indizes,
- WAL- oder gleichwertiger sicherer Journaling-Modus,
- plattformübergreifende Verfügbarkeit,
- exportierbare Sicherungsdateien.

Die konkrete Technologie wird durch eine gesonderte ADR festgelegt. SQLite ist der bevorzugte Referenzkandidat, aber AP-0016 bindet die Domäne nicht direkt daran.

## 5. Verzeichnisstruktur für lokale Daten

```text
data/
├── projects/
├── runtime/
│   ├── events/
│   │   ├── outbox/
│   │   └── dead-letter/
│   ├── locks/
│   └── cache/
├── audit/
├── simulation/
├── backups/
└── migrations/
```

Produktive Laufzeitinhalte werden nicht in Git versioniert.

## 6. Datenbank- und Projektdateien

Ein ProjectOS-Projekt besitzt eine eindeutige Projektkennung und genau einen autoritativen lokalen Datenbestand.

Vorgesehenes Dateischema:

```text
<projektkennung>.projectos.db
```

Beispiel:

```text
PRJ-000012.projectos.db
```

Zusätzliche Anhänge werden außerhalb der Datenbank gespeichert und über stabile Objektkennungen referenziert.

## 7. Persistenzabbildung

Die Infrastruktur bildet Domänenaggregate auf Persistenzmodelle ab.

Verbindliche Trennung:

```text
Domänenobjekt
    ↕ Mapper
Persistenzmodell
    ↕ Adapter
Lokaler Datenspeicher
```

Regeln:

- Keine Speicherattribute in Domänenobjekten.
- Keine ORM- oder SQL-Abhängigkeiten in der Domänenschicht.
- Persistenzmodelle besitzen keine Fachlogik.
- Mapper müssen vollständig getestet werden.
- Unbekannte oder nicht unterstützte Datenversionen werden nicht stillschweigend ignoriert.

## 8. Persistierte Grunddaten

Jedes gespeicherte Aggregat enthält mindestens:

- `object_id`,
- `business_id`,
- `domain_id`,
- `object_type`,
- `object_version`,
- `revision`,
- `lifecycle_status`,
- `created_at`,
- `created_by`,
- `modified_at`,
- `modified_by`,
- `schema_version`.

## 9. Revisionskontrolle

ProjectOS verwendet optimistische Nebenläufigkeitskontrolle.

Beim Speichern gilt:

```text
UPDATE ...
WHERE object_id = :id
AND revision = :expected_revision
```

Nur genau ein aktualisierter Datensatz gilt als Erfolg.

Bei Abweichung wird `ERR-APP-0001 – Revisionskonflikt` zurückgegeben. Veraltete Änderungen überschreiben niemals stillschweigend neuere Daten.

## 10. Transaktionen

Eine lokale Transaktion umfasst alle atomar notwendigen Änderungen eines Anwendungsfalls:

1. Aggregatänderungen,
2. Revisionsaktualisierung,
3. Outbox-Einträge,
4. Audit-Einträge,
5. Idempotenznachweis des Befehls,
6. notwendige Prozesszustände.

Externe Systeme werden erst nach erfolgreichem Commit angesprochen.

## 11. Outbox und Audit

Die in ADR-0002 festgelegte Outbox wird im gleichen transaktionalen Speicher wie das veränderte Aggregat geführt.

Audit-Einträge sind ausschließlich anhängend. Reguläre Update- und Delete-Operationen auf Auditdaten sind nicht zulässig.

## 12. Löschregeln

Physisches Löschen ist nicht der Standard.

Verbindliche Reihenfolge:

1. fachliches Archivieren,
2. logisches Löschen, falls erforderlich,
3. physisches Löschen nur aufgrund ausdrücklich dokumentierter Aufbewahrungs- oder Datenschutzregeln.

Jede physische Löschung ist auditpflichtig und benötigt eine definierte Berechtigung.

## 13. Lesemodelle

Lesemodelle dürfen getrennt vom Aggregatspeicher geführt werden.

Sie sind:

- aus autoritativen Daten reproduzierbar,
- eindeutig als `STRONG`, `EVENTUAL` oder `SNAPSHOT` gekennzeichnet,
- nicht die Quelle fachlicher Invarianten,
- bei Beschädigung neu aufbaubar.

## 14. Simulation

Simulationen verwenden isolierte Speicherbereiche.

Zulässige Varianten:

- transaktionaler Rollback nach Simulationsende,
- temporäre Projektdatenbank,
- expliziter Simulations-Snapshot.

Simulationen dürfen keine produktiven Daten verändern und keine produktiven Outbox-Ereignisse auslösen.

## 15. Schema-Versionierung

Jeder persistente Speicher besitzt eine eindeutige Schema-Version.

Vorgesehenes Format:

```text
major.minor.patch
```

Die aktuelle Version wird zentral gespeichert und bei jedem Öffnen geprüft.

Unterschiede zwischen Objektversion und Schema-Version:

- Objektversion beschreibt die fachliche Version eines Objekts.
- Schema-Version beschreibt die technische Struktur des Speichers.

## 16. Repository-Migrationen

Jede Änderung am persistenten Schema wird als Repository-Migration modelliert.

Kennung:

```text
RM-<laufende Nummer>
```

Beispiel:

```text
RM-0001
```

Eine Migration enthält mindestens:

- Kennung,
- Titel,
- Ausgangsversion,
- Zielversion,
- Beschreibung,
- Vorbedingungen,
- Ausführungsschritte,
- Validierungsschritte,
- Rückfallstrategie,
- Prüfsumme,
- Status.

## 17. Migrationsregeln

Migrationen müssen:

- geordnet,
- unveränderlich,
- idempotent,
- transaktional, soweit technisch möglich,
- wiederholbar testbar,
- vor der Ausführung sicherbar,
- nach der Ausführung validierbar sein.

Eine bereits veröffentlichte Migration wird nicht nachträglich verändert. Korrekturen erfolgen durch eine neue Migration.

## 18. Migrationsstatus

```text
PENDING
RUNNING
APPLIED
FAILED
ROLLED_BACK
MANUAL_ACTION_REQUIRED
```

Jeder Ausführungsversuch wird protokolliert und auditiert.

## 19. Migration Registry

Vorgesehene Konfiguration:

```text
config/persistence/migration-registry.yaml
```

Beispiel:

```yaml
migrations:
  - id: RM-0001
    from: "0.0.0"
    to: "1.0.0"
    script: migrations/RM-0001-initial-schema.sql
    checksum: "sha256:..."
    transactional: true
    backup_required: true
```

## 20. Sicherungen

ProjectOS unterstützt konsistente lokale Sicherungen.

Eine Sicherung enthält mindestens:

- Projektdatenbank,
- referenzierte Anhänge,
- Schema-Version,
- ProjectOS-Version,
- Erstellungszeit,
- Projektkennung,
- Prüfsummenmanifest.

Vorgesehenes Paketformat:

```text
<projektkennung>-<zeitstempel>.projectos-backup
```

## 21. Sicherungsregeln

- Sicherungen werden nie während eines inkonsistenten Zwischenzustands erstellt.
- Vor jeder nicht trivialen Migration wird automatisch eine Sicherung erzeugt.
- Sicherungen werden durch Prüfsummen validiert.
- Aufbewahrungsregeln sind konfigurierbar.
- Sicherungen können verschlüsselt werden.
- Eine Sicherung ersetzt keine Versionsverwaltung der Projektdokumentation.

## 22. Wiederherstellung

Eine Wiederherstellung erfolgt in folgenden Schritten:

1. Paket und Manifest prüfen,
2. Prüfsummen validieren,
3. Zielpfad und Berechtigung prüfen,
4. vorhandenen Datenbestand sichern,
5. Wiederherstellung in temporären Pfad durchführen,
6. Schema und referenzielle Integrität prüfen,
7. Datenbestand atomar aktivieren,
8. Audit-Eintrag erzeugen.

Eine beschädigte Sicherung darf den vorhandenen Datenbestand nicht überschreiben.

## 23. Export und Portabilität

ProjectOS-Projektdaten müssen auf unterstützten Plattformen transportierbar sein.

Daher gilt:

- keine absoluten Pfade in fachlichen Daten,
- UTF-8 für Text,
- ISO-8601-UTC für Zeitstempel,
- stabile Kennungen statt Speicheradressen,
- normalisierte relative Pfade,
- dokumentierte Dateinamensregeln.

## 24. Verschlüsselung und Schutz

Sensible lokale Speicher können verschlüsselt werden.

Regeln:

- keine fest codierten Schlüssel,
- Schlüssel nicht in derselben Datei wie verschlüsselte Daten speichern,
- Integritätsprüfung zusätzlich zur Verschlüsselung,
- verschlüsselte Sicherungen müssen als solche gekennzeichnet sein,
- Schlüsselwechsel muss ohne Verlust fachlicher Kennungen möglich sein.

Die konkrete Kryptografie wird in einem Sicherheitsarbeitspaket festgelegt.

## 25. Sperr- und Mehrfachzugriff

Ein Projekt darf nicht unkontrolliert von mehreren schreibenden Instanzen geöffnet werden.

Vorgesehen sind:

- exklusive Schreibsperre,
- optionale parallele Lesezugriffe,
- Sperrkennung und Prozessinformation,
- Erkennung verwaister Sperren,
- kontrollierte Übernahme nach Prüfung,
- Auditierung erzwungener Sperraufhebung.

## 26. Fehlerkennungen

```text
ERR-PER-0001  Datenspeicher kann nicht geöffnet werden
ERR-PER-0002  Schema-Version nicht unterstützt
ERR-PER-0003  Persistenzabbildung fehlgeschlagen
ERR-PER-0004  Referenzielle Integrität verletzt
ERR-PER-0005  Transaktion fehlgeschlagen
ERR-PER-0006  Schreibsperre aktiv
ERR-MIG-0001  Migration nicht gefunden
ERR-MIG-0002  Migrationsprüfsumme ungültig
ERR-MIG-0003  Migration fehlgeschlagen
ERR-MIG-0004  Rückfall nicht möglich
ERR-BKP-0001  Sicherung fehlgeschlagen
ERR-BKP-0002  Sicherung beschädigt
ERR-BKP-0003  Wiederherstellung fehlgeschlagen
```

## 27. Konfiguration

Vorgesehene Datei:

```text
config/persistence/persistence.yaml
```

Beispiel:

```yaml
persistence:
  provider: embedded
  transactions: true
  optimistic_concurrency: true
  journal_mode: wal
  foreign_keys: true
  backups:
    enabled: true
    before_migration: true
    retention_count: 10
  migrations:
    automatic: false
    checksum_required: true
  locking:
    exclusive_writer: true
```

Produktive Migrationen werden standardmäßig nicht ohne vorherige Prüfung automatisch ausgeführt.

## 28. Schnittstellen

Vorgesehene Basisschnittstellen:

```text
PersistenceProvider
DatabaseSession
UnitOfWork
MigrationRunner
MigrationRepository
BackupService
RestoreService
ProjectLockService
ReadModelRebuilder
```

## 29. Verzeichnisstruktur

```text
src/core/infrastructure/persistence/
├── provider/
├── mapping/
├── repositories/
├── migrations/
├── backup/
├── locking/
└── read_models/

config/persistence/
migrations/
tests/contract/persistence/
tests/integration/persistence/
tests/migration/
tests/recovery/
```

## 30. Testanforderungen

Mindestens erforderlich:

- Repository-Vertragstests für jede Implementierung,
- Roundtrip-Tests für Aggregate und Wertobjekte,
- Revisionskonflikttests,
- Transaktions- und Rollbacktests,
- Outbox-Atomarität,
- Audit-Unveränderlichkeit,
- Sperrtests,
- Migrationsreihenfolge,
- Migrations-Idempotenz,
- Prüfsummenfehler,
- Sicherung und Wiederherstellung,
- Wiederanlauf nach Prozessabbruch,
- Portabilität zwischen unterstützten Plattformen,
- isolierte Simulationspersistenz.

## 31. Architekturentscheidungen

Mit AP-0016 werden verbindlich festgelegt:

1. Offlinefähiger lokaler Datenspeicher ist primäre Persistenz.
2. Die Domäne bleibt von Speichertechnologien unabhängig.
3. Repositories und Mapper bilden die Persistenzgrenze.
4. Optimistische Revisionskontrolle ist verpflichtend.
5. Aggregat, Outbox, Audit und Befehlsidempotenz werden atomar gespeichert.
6. Auditdaten sind ausschließlich anhängend.
7. Schemaänderungen erfolgen nur über versionierte `RM-*`-Migrationen.
8. Vor risikobehafteten Migrationen wird gesichert.
9. Lesemodelle sind reproduzierbar und nicht fachlich autoritativ.
10. Simulationen verwenden isolierte Speicherbereiche.

## 32. ADR-Bedarf

Vorgesehen:

```text
ADR-0004 – Lokaler Datenspeicher, Persistenzgrenzen und Migrationen
```

**Status:** Angenommen

Die konkrete Auswahl des eingebetteten Speicherprodukts kann in einer nachfolgenden Technologie-ADR präzisiert werden.

## 33. Definition of Done

AP-0016 ist abgeschlossen, wenn:

- Speicherbereiche getrennt sind,
- Persistenzgrenzen definiert sind,
- Transaktions- und Revisionsregeln festgelegt sind,
- Outbox und Audit atomar eingebunden sind,
- Schema-Versionierung und Migrationen beschrieben sind,
- Sicherung und Wiederherstellung definiert sind,
- Sperr-, Sicherheits- und Portabilitätsregeln vorliegen,
- Schnittstellen, Verzeichnisse und Tests festgelegt sind,
- ADR-0004 vorgesehen und angenommen ist.

Alle Kriterien sind mit diesem Dokument erfüllt.

## 34. Commit-Vorschlag

```text
feat(persistence): AP-0016 Offline-Persistenz und Migrationen definieren
```

## 35. Status

**AP-0016 abgeschlossen**

Mit AP-0016 ist die Grundlage für lokale, sichere und migrierbare ProjectOS-Datenbestände definiert. Sprint 002 kann nun mit einem Konsistenzreview und der Festlegung der ersten konkreten Implementierungstechnologie abgeschlossen werden.
