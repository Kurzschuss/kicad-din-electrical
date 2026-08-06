# ADR-0003 – Struktur der Anwendungsschicht und CQRS-Grundlagen

**Status:** Angenommen

## Kontext

ProjectOS benötigt eine klar getrennte, testbare und offlinefähige Anwendungsschicht für Zustandsänderungen, Abfragen, Berechtigungen und langlebige Prozesse.

## Entscheidung

- Schreibende Befehle und lesende Abfragen werden getrennt.
- Befehle und Abfragen sind unveränderliche Objekte.
- Jeder Befehl besitzt genau einen primären Behandler.
- Fachliche Regeln verbleiben in der Domänenschicht.
- Berechtigungen werden vor Zustandsänderungen geprüft.
- Schreibende Anwendungsfälle besitzen explizite Transaktionsgrenzen.
- Externe Systeme werden nicht innerhalb lokaler Transaktionen aufgerufen.
- Langlebige und domänenübergreifende Abläufe werden durch Prozessmanager koordiniert.
- Befehle und Prozessmanager müssen idempotent sein.
- Kompensationen werden als eigenständige fachliche Aktionen modelliert.
- Abfragen dürfen spezialisierte Lesemodelle verwenden.
- Simulationen verwenden dieselben Anwendungsfälle wie der Produktivbetrieb.

## Konsequenzen

- Command Bus und Query Bus werden als zentrale Anwendungsschnittstellen eingeführt.
- Querschnittsfunktionen werden über eine deterministische Pipeline ausgeführt.
- Revisionskonflikte werden strukturiert behandelt.
- Lesemodelle müssen ihre Konsistenzart kenntlich machen.
