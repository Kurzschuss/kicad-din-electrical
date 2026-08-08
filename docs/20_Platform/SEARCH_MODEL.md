# Suchmodell

**Dokument-ID:** PLT-0021  
**Titel:** Fachliches Modell für Suche, Auffindbarkeit und Suchprojektionen  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert Suche und Auffindbarkeit als eigenständige Plattformfunktion von ProjectOS.

Die Suche ermöglicht das gezielte Finden und Eingrenzen von Objekten, Beziehungen, Projekten, Wissenselementen, Benutzern, Organisationen, Auditdaten, Konfigurationen, Plugins und späteren Domänenobjekten.

Suche ist keine Source of Truth. Sie liefert abgeleitete Treffer auf Basis autoritativer Plattform- und Domänendaten.

## 2. Grundsatz

ProjectOS behandelt Suche nicht als Komfortfunktion, sondern als Plattformdienst.

Mit wachsendem Projektumfang muss Information auffindbar bleiben, ohne dass Benutzer Verzeichnisstrukturen oder interne Speicherorte kennen müssen.

Für die Suche gelten insbesondere:

- Rechteprüfung und Sichtbarkeitsgrenzen;
- stabile Referenzierbarkeit von Treffern;
- nachvollziehbare Trefferherkunft;
- explizite Kennzeichnung veralteter oder unvollständiger Indizes;
- Offline-Fähigkeit im vorgesehenen Betriebsumfang;
- keine konkurrierende fachliche Wahrheit im Suchindex.

## 3. Architekturstellung

Das Suchmodell gehört zur Plattformebene.

Es baut insbesondere auf `PLATFORM_MODEL.md`, `PROJECT_MODEL.md`, `RELATION_MODEL.md`, `IDENTITY_MODEL.md`, `ORGANIZATION_MODEL.md`, `AUDIT_MODEL.md`, `MEMORY_MODEL.md`, `CONFIGURATION_MODEL.md`, `PLUGIN_MODEL.md`, `BUS_MODEL.md` und späteren Domänenmodellen auf.

Domänen dürfen eigene Suchfelder, Suchadapter und fachliche Projektionen bereitstellen, müssen jedoch die zentralen Sicherheits- und Herkunftsregeln einhalten.

## 4. Suchbare Quellen

Mindestens folgende Quelltypen müssen grundsätzlich suchbar gemacht werden können:

- Projekte;
- Workspaces, soweit zulässig;
- allgemeine Plattformobjekte;
- Objektbeziehungen;
- Benutzer und Akteursidentitäten;
- Organisationen, Teams, Gruppen und Zugehörigkeiten;
- Rollen und Berechtigungsreferenzen;
- Delegationen und Stellvertretungen;
- Audit- und Sicherheitsnachweise;
- Projektwissen und Entscheidungen;
- Konfigurationsobjekte;
- Plugins und Erweiterungen;
- Dokument- und Artefaktreferenzen;
- Simulationsergebnisse, sofern dafür eine persistierte oder freigegebene Sicht existiert;
- spätere Domänenobjekte wie MCB, RCCB oder andere elektrische Komponenten.

Nicht jeder Quelltyp ist für jeden Benutzer sichtbar.

## 5. Suchanfrage

Eine Suchanfrage beschreibt mindestens:

- Suchtext oder strukturierte Kriterien;
- aktuellen Akteurs- und Sitzungskontext, soweit erforderlich;
- Projekt-, Organisations-, Workspace- oder Domänenkontext;
- gewünschte Quelltypen;
- Filter;
- Sortierung;
- gewünschte Treffermenge;
- optionalen Zeit- oder Versionsbezug;
- Korrelations-ID für Nachvollziehbarkeit bei sicherheitsrelevanten Suchvorgängen.

## 6. Suchkriterien

Unterstützt werden sollen insbesondere:

- stabile ID oder UUID;
- Name und Bezeichnung;
- Typ;
- Status;
- Eigentümer oder Verantwortlicher;
- Projektbezug;
- Organisationsbezug;
- Domäne;
- Eigenschaftswert;
- Tag oder Klassifikation;
- Beziehungstyp;
- Version;
- Zeitraum;
- Freitext;
- Auditmerkmal;
- Wissensart;
- Berechtigungs- oder Rollenreferenz.

Domänen dürfen weitere fachliche Kriterien ergänzen.

## 7. Suche nach Beziehungen

ProjectOS muss nicht nur Objekte, sondern auch ihre Beziehungen auffindbar machen können.

Beispiele:

- Welche Entscheidungen begründen dieses Modell?
- Welche Tests prüfen dieses Objekt?
- Welche Benutzer besitzen eine Rolle in diesem Projekt?
- Welche Delegationen betreffen diese Berechtigung?
- Welche Organisationen referenzieren dieses Projekt?
- Welche Wissenselemente beziehen sich auf diesen Fehler?

Die Suche darf dabei keine zweite Beziehungslogik erzeugen, sondern verwendet die kanonischen Beziehungen und deren Projektionen.

## 8. Volltextsuche

Volltextsuche kann für geeignete Inhalte bereitgestellt werden.

Sie muss unterscheiden können zwischen:

- indexiertem Inhalt;
- nicht indexiertem Inhalt;
- nicht verfügbarem Inhalt;
- aus Sicherheitsgründen nicht sichtbarem Inhalt.

Ein fehlender Treffer darf nicht automatisch bedeuten, dass ein Objekt nicht existiert.

## 9. Strukturierte Suche

Für technische und fachliche Nutzung muss strukturierte Suche möglich sein.

Beispiele:

```text
type = MCB
project = P-001
status = active
rated_current = 16A
```

oder:

```text
identity = U-123
role = reviewer
scope = project:P-001
```

Die konkrete Abfragesprache wird nicht in diesem Dokument festgelegt.

## 10. Treffer

Ein Suchtreffer beschreibt mindestens:

- stabile Referenz auf die autoritative Quelle;
- Trefferart;
- Anzeigename oder Zusammenfassung;
- relevanten Kontext;
- Trefferherkunft;
- Datenstand oder Versionsbezug;
- Sichtbarkeitsstatus;
- optionalen Relevanzwert;
- optionalen Hinweis auf veraltete oder unvollständige Daten.

Der Treffer selbst ist keine neue Kopie der fachlichen Wahrheit.

## 11. Relevanz

Suchrelevanz darf unterschiedliche Signale berücksichtigen, beispielsweise:

- textuelle Übereinstimmung;
- exakte ID-Übereinstimmung;
- Projekt- oder Domänennähe;
- Beziehung zum aktuellen Objekt;
- Aktualität;
- Status;
- explizite Benutzerfilter.

Benutzergewichtung darf nicht pauschal versteckt die Sichtbarkeit oder Rangfolge sicherheitsrelevanter Informationen verzerren.

Falls Gewichtung fachlich verwendet wird, muss dies erklärbar und kontextbezogen sein.

## 12. Berechtigungsprüfung

Suchergebnisse unterliegen denselben Autorisierungs- und Datenschutzregeln wie direkte Objektzugriffe.

Daraus folgt:

- nicht sichtbare Objekte dürfen nicht über Suchtreffer offengelegt werden;
- sensible Metadaten dürfen nicht durch Trefferzusammenfassungen leaken;
- Trefferanzahl darf keine unzulässigen Rückschlüsse ermöglichen, sofern dies sicherheitsrelevant ist;
- Öffnen eines Treffers erfordert weiterhin die vollständige Objekt- oder Dienstautorisierung;
- Suchindex oder Read-Model ersetzt keine produktive Autorisierungsentscheidung.

## 13. Sichtbarkeit und Teilansichten

Ein Benutzer kann berechtigt sein, nur einen Teil eines Objekts oder seiner Metadaten zu sehen.

Die Suche muss solche Sichtbarkeitsstufen berücksichtigen können.

Beispielsweise kann sichtbar sein:

- dass ein Projekt existiert;
- aber nicht dessen vertraulicher Inhalt;

oder:

- dass ein Benutzer Mitglied einer Organisation ist;
- aber nicht dessen vollständige Profildaten.

## 14. Audit-Suche

Auditdaten benötigen besondere Such- und Sichtbarkeitsregeln.

Suchkriterien können insbesondere sein:

- Akteursidentität;
- Korrelations-ID;
- Projekt;
- Organisation;
- Handlung;
- Ziel;
- Ergebnis;
- Zeitraum;
- Delegation;
- Ausnahme;
- Risikoklasse.

Audit-Suche darf Schutz- und Aufbewahrungsregeln nicht umgehen.

## 15. Projektgedächtnis

Das Projektgedächtnis muss über Wissensarten und Beziehungen durchsuchbar sein.

Dadurch sollen Fragen möglich werden wie:

- Warum wurde eine Entscheidung getroffen?
- Welche Anforderung führte zu einer Implementierung?
- Welche Erkenntnisse betreffen ein bestimmtes Modell?
- Welche offene Frage hängt mit einem Fehler zusammen?
- Welche verworfenen Alternativen existieren?

Die Suche liefert Referenzen auf Wissenselemente und nicht bloß unstrukturierte Textfundstellen.

## 16. Benutzer- und Organisationssuche

Benutzer, Identitäten, Organisationen, Teams und Zugehörigkeiten müssen innerhalb zulässiger Sichtbarkeitsgrenzen suchbar sein.

Die Suche darf keine unzulässige Personenprofilerstellung ermöglichen.

Insbesondere Gewichtungsinformationen, Sicherheitsstatus oder vertrauliche Organisationsbeziehungen sind nur bei entsprechender Berechtigung sichtbar.

## 17. Berechtigungs- und Rollenrecherche

Für administrative und erklärende Funktionen muss die Suche Referenzen auf Rollen, Berechtigungen, Delegationen und Regelquellen auffindbar machen können.

Dies unterstützt insbesondere Z_Cockpit bei der Frage:

> Woher stammt dieses effektive Recht?

Die eigentliche effektive Autorisierungsentscheidung wird weiterhin durch die Autorisierungsplattform getroffen.

## 18. Konfigurationssuche

Konfigurationsobjekte müssen mindestens nach Typ, Gültigkeitsbereich, Ziel, Version, Status und verantwortlicher Instanz suchbar sein.

Geheimnisse dürfen weder indexiert noch in Treffern dargestellt werden.

## 19. Plugin-Suche

Plugins und Erweiterungspunkte können nach Plugin-ID, Fähigkeit, Version, Status, Herkunft, Abhängigkeit und bereitgestelltem Erweiterungspunkt gesucht werden.

Plugin-interne Indizes dürfen keine fremden Sicherheitsgrenzen umgehen.

## 20. Domänensuche

Domänen dürfen spezialisierte Suchprojektionen bereitstellen.

Beispiele für spätere Elektrodomänen:

- Gerätetyp;
- Hersteller;
- Bemessungsstrom;
- Auslösecharakteristik;
- Polzahl;
- Normreferenz;
- Projektverwendung;
- Bibliotheksreferenz.

Diese Felder gehören der jeweiligen Domäne und werden nicht in das Plattformmodell hart codiert.

## 21. Suchindex

Ein Suchindex ist eine abgeleitete technische oder fachliche Projektion.

Er ist nicht autoritativ.

Der Index muss erkennen lassen können:

- zugrunde liegende Datenversion oder Aktualitätsmarke;
- Zeitpunkt der letzten Aktualisierung;
- unvollständige Quellen;
- Fehler oder ausstehende Aktualisierungen;
- Offline- oder Synchronisationsstatus.

## 22. Aktualisierung

Suchindizes können ereignisgetrieben, periodisch oder bei Bedarf aktualisiert werden.

Das Busmodell kann für Änderungsbenachrichtigungen verwendet werden.

Ein fehlgeschlagenes Indexupdate darf die autoritative Quelle nicht verändern.

Die Suche muss einen veralteten Indexzustand sichtbar machen können, wenn dieser relevant ist.

## 23. Konsistenz

ProjectOS darf für Suche eventual consistency zulassen, sofern dies für die jeweilige Suchart vertretbar ist.

Sicherheitskritische Entscheidungen dürfen jedoch nicht allein auf möglicherweise veralteten Suchdaten basieren.

Für exakte operative Entscheidungen muss die autoritative Quelle erneut geprüft werden.

## 24. Offline-First

Die Suche muss im vorgesehenen Offline-Betriebsumfang funktionieren können.

Lokale Suche kann auf lokal verfügbaren Projektionen und Daten basieren.

Dabei muss erkennbar bleiben:

- welche Quellen lokal vollständig sind;
- welche Daten nur zwischengespeichert sind;
- wann zuletzt synchronisiert wurde;
- welche externen Quellen fehlen;
- ob Suchergebnisse veraltet sein können.

Offline-Suche darf fehlende externe Daten nicht als nicht existent darstellen.

## 25. Synchronisation

Bei Wiederverbindung müssen Suchprojektionen neu bewertet oder aktualisiert werden können.

Konflikte betreffen die autoritativen Daten und werden nicht im Suchindex gelöst.

Der Index folgt dem Ergebnis der zuständigen Plattform- oder Domänendienste.

## 26. Datenschutz

Suche besitzt ein erhöhtes Risiko für Datenaggregation.

Daher gelten insbesondere:

- Datenminimierung;
- berechtigungsabhängige Indexierung und Ausgabe;
- Schutz vor unzulässiger Querverknüpfung personenbezogener Daten;
- keine Indexierung von Geheimnissen;
- Zweckbindung für sensible Suchfelder;
- kontrollierte Sichtbarkeit von Benutzergewichtungen und Sicherheitsmetadaten.

## 27. Audit

Nicht jede normale Suchanfrage muss auditpflichtig sein.

Auditierbar sein können insbesondere:

- privilegierte Suche in Auditdaten;
- Suche nach besonders sensiblen Benutzer- oder Sicherheitsinformationen;
- administrative Massenabfragen;
- Suche in vertraulichen Projekten;
- Export großer Suchergebnismengen;
- sicherheitsrelevante Suchkonfigurationen.

Die konkrete Auditpflicht wird durch Richtlinie bestimmt.

## 28. Z_Cockpit

Z_Cockpit soll die zentrale Suchoberfläche für Plattform- und Projektdaten bereitstellen können.

Vorgesehen sind insbesondere:

- globale Suche;
- projektbezogene Suche;
- organisationsbezogene Suche;
- Wissenssuche;
- Audit-Suche;
- Rollen-/Berechtigungsrecherche;
- Plugin- und Konfigurationssuche;
- spätere Domänensuche.

Treffer müssen ihren Kontext und ihre Quelle verständlich erkennen lassen.

## 29. Z_Cockpit und Rechtesimulation

Die Rechtesimulation darf Suchfunktionen verwenden, um relevante Rollen, Berechtigungen, Delegationen, Organisationen oder Regeln auszuwählen.

Die Simulation darf jedoch nicht allein aus Suchindizes effektive Rechte berechnen.

Sie muss die autoritativen Simulations- und Autorisierungsregeln verwenden.

## 30. Fehlerfälle

Die Suche muss insbesondere unterscheiden können:

- keine Treffer;
- Quelle nicht verfügbar;
- Index veraltet;
- Teilindex unvollständig;
- nicht autorisiert;
- Suchkriterium ungültig;
- Suchadapter fehlgeschlagen;
- externe Quelle nicht erreichbar.

Diese Zustände dürfen nicht zu einem generischen „nicht gefunden“ zusammenfallen, wenn dies fachlich relevant ist.

## 31. Validierung

Eine Suchprojektion oder ein Suchadapter ist mindestens darauf zu prüfen, dass:

1. Quelltyp eindeutig ist;
2. Treffer auf stabile autoritative Referenzen zeigen;
3. Sichtbarkeitsregeln angewendet werden;
4. keine Geheimnisse indexiert werden;
5. Datenstand erkennbar ist;
6. veraltete oder unvollständige Zustände darstellbar sind;
7. Domänenfelder ihrem Eigentümer zugeordnet bleiben;
8. Indexfehler autoritative Daten nicht verändern;
9. Treffer keine unzulässigen Metadaten offenlegen;
10. produktive Entscheidungen nicht allein auf Suchprojektionen beruhen.

## 32. Invarianten

1. Suche ist keine Source of Truth.
2. Suchindex und autoritative Daten bleiben getrennt.
3. Nicht autorisierte Daten werden nicht durch Suche offengelegt.
4. Geheimnisse werden nicht indexiert.
5. Ein fehlender Treffer beweist nicht zwingend Nichtexistenz.
6. Suchprojektionen dürfen veraltet sein, müssen dies aber erkennbar machen können.
7. Produktive Autorisierung verwendet nicht allein Suchdaten.
8. Domänenspezifische Suchfelder bleiben Eigentum der Domäne.
9. Offline-Suche kennzeichnet fehlende oder veraltete Quellen.
10. Z_Cockpit ist Suchoberfläche, nicht Such-Source-of-Truth.
11. Rechtesimulation verwendet Suche nur zur Auswahl und Navigation, nicht als Berechtigungsengine.
12. Treffer bleiben auf ihre autoritative Quelle zurückführbar.

## 33. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- konkrete Suchmaschine;
- konkretes Indexformat;
- konkreten Rankingalgorithmus;
- konkrete Volltextsyntax;
- konkrete Datenbanktechnologie;
- konkrete Vektor- oder Embedding-Technik;
- konkrete GUI-Layouts;
- endgültige Domänensuchfelder;
- konkrete Cache-Strategien.

## 34. Folgemodelle

Auf diesem Modell bauen insbesondere auf:

- spätere Suchdienste und Suchadapter;
- Z_Cockpit-Suchansichten;
- Wissens- und Beziehungsnavigation;
- Audit-Analyse;
- Plugin-Suchadapter;
- domänenspezifische Suchprojektionen;
- spätere MCB- und RCCB-Suche.

## 35. Abhängigkeiten

Dieses Dokument basiert insbesondere auf:

- `PLATFORM_MODEL.md`;
- `PROJECT_MODEL.md`;
- `WORKSPACE_MODEL.md`;
- `IDENTITY_MODEL.md`;
- `AUTHORIZATION_MODEL.md`;
- `ROLE_MODEL.md`;
- `PERMISSION_MODEL.md`;
- `DELEGATION_MODEL.md`;
- `ORGANIZATION_MODEL.md`;
- `AUDIT_MODEL.md`;
- `USER_WEIGHT_MODEL.md`;
- `MEMORY_MODEL.md`;
- `BUS_MODEL.md`;
- `CONFIGURATION_MODEL.md`;
- `PLUGIN_MODEL.md`;
- `RELATION_MODEL.md`;
- `Z_COCKPIT_IDENTITY_INTEGRATION.md`;
- `Z_COCKPIT_AUTHORIZATION_SIMULATION.md`.

## 36. Ergebnis

ProjectOS besitzt ein zentrales, sicherheitsbewusstes Suchmodell für Plattform-, Projekt-, Wissens-, Audit- und spätere Domänendaten.

Suche und Suchindizes bleiben abgeleitete Sichten, während autoritative Plattform- und Domänendaten, Berechtigungsentscheidungen und Fachlogik in ihren jeweiligen Eigentumsbereichen verbleiben.