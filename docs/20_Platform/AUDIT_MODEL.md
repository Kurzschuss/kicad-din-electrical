# Auditmodell

**Dokument-ID:** PLT-0015  
**Titel:** Fachliches Modell für Audit, Nachweis und sicherheitsrelevante Vorgänge  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert das kanonische Auditmodell von ProjectOS.

Audit dokumentiert sicherheits-, verantwortungs-, freigabe- oder nachweisrelevante Vorgänge so, dass später nachvollziehbar bleibt:

- wer gehandelt hat;
- in welchem Kontext gehandelt wurde;
- welche Handlung ausgeführt oder versucht wurde;
- welches Ziel betroffen war;
- welche Autorisierungs- oder Verantwortungsgrundlage maßgeblich war;
- welches Ergebnis eingetreten ist;
- welche fachliche Begründung oder Freigabe vorlag.

Audit ist ausdrücklich nicht mit fachlicher Objekthistorie gleichzusetzen.

## 2. Architekturstellung

Das Auditmodell gehört zur Plattformebene.

Es baut insbesondere auf `PLATFORM_MODEL.md`, `IDENTITY_MODEL.md`, `ACCOUNT_MODEL.md`, `AUTHENTICATION_MODEL.md`, `SESSION_MODEL.md`, `AUTHORIZATION_MODEL.md`, `ROLE_MODEL.md`, `PERMISSION_MODEL.md`, `DELEGATION_MODEL.md`, `ORGANIZATION_MODEL.md`, `PROJECT_MODEL.md` und `RELATION_MODEL.md` auf.

Alle Plattformbereiche und Domänen verwenden für auditpflichtige Vorgänge denselben kanonischen Auditweg. Sie dürfen keine voneinander unabhängigen Auditwahrheiten einführen.

## 3. Audit und Historie

Audit und Historie beantworten unterschiedliche Fragen.

Historie beantwortet insbesondere:

> Wie hat sich ein Objekt fachlich verändert?

Audit beantwortet insbesondere:

> Wer hat wann, warum, in welchem Kontext und unter welcher Berechtigungsgrundlage welche Handlung mit welchem Ergebnis ausgeführt?

Daraus folgt:

- nicht jede Objektänderung benötigt denselben Auditumfang;
- nicht jeder Auditvorgang verändert ein fachliches Objekt;
- Audit darf auf Objektversionen oder Historieneinträge referenzieren;
- Historie darf Audit nicht ersetzen;
- Audit darf fachliche Historie nicht als zweite Objektversionierung duplizieren.

## 4. Audit-Eintrag

Ein Audit-Eintrag ist ein dauerhaft referenzierbarer Plattformnachweis für einen auditpflichtigen Vorgang oder einen relevanten Teil davon.

Ein Audit-Eintrag beschreibt mindestens, soweit für den Vorgang vorhanden:

- eindeutige Audit-ID;
- Ereignis- oder Vorgangstyp;
- Zeitpunkt;
- tatsächlich handelnde Akteursidentität;
- verwendetes Konto;
- Sitzungs-ID;
- vertretene, delegierende oder originär verantwortliche Identität;
- Projekt-, Organisations-, Workspace- oder Domänenkontext;
- ausgeführte oder versuchte Handlung;
- Zieltyp und Zielidentität;
- Gültigkeitsbereich;
- Autorisierungsergebnis oder Berechtigungsnachweisreferenz;
- maßgebliche Rollen-, Berechtigungs-, Delegations-, Ausnahme- oder Richtlinienreferenzen;
- Ergebnis des Vorgangs;
- fachliche Begründung, soweit erforderlich;
- Korrelations-ID;
- Referenzen auf vorherigen und nachfolgenden Zustand, soweit fachlich sinnvoll;
- Herkunft bzw. ausführenden Plattformdienst.

## 5. Stabile Auditidentität

Jeder persistierte Audit-Eintrag besitzt eine stabile Audit-ID.

Diese ID:

- wird nicht wiederverwendet;
- ist unabhängig von UI, Logdatei oder Speichertechnologie;
- kann von anderen Nachweisen referenziert werden;
- bleibt auch bei Archivierung oder Speicherüberführung erhalten.

## 6. Tatsächlich handelnde Identität

Audit muss immer die tatsächlich handelnde Akteursidentität erfassen, soweit eine Handlung einem Akteur zugeordnet werden kann.

Bei Stellvertretung oder Delegation bleiben mindestens getrennt:

- tatsächlich handelnde Identität;
- vertretene oder delegierende Identität;
- Delegations- oder Stellvertretungsreferenz;
- konkret wirksamer Umfang.

Eine stellvertretende Handlung darf im Audit niemals so erscheinen, als hätte die vertretene Person selbst technisch gehandelt.

## 7. Menschliche und technische Akteure

Audit unterstützt menschliche und technische Akteursidentitäten.

Technische Vorgänge können beispielsweise ausgeführt werden durch:

- Dienste;
- API-Clients;
- Automatisierungen;
- Geräte;
- Systemprozesse.

Technische Akteure dürfen nicht unter einer unspezifischen Sammelidentität verschwinden, wenn individuelle Nachvollziehbarkeit erforderlich ist.

## 8. Konto und Sitzung

Konto und Sitzung sind zusätzliche Kontextinformationen und ersetzen nicht die Akteursidentität.

Audit kann festhalten:

- welches Konto verwendet wurde;
- welche Sitzung beteiligt war;
- welchen Authentifizierungsgrad die Sitzung besaß;
- ob die Sitzung online oder offline war;
- ob Step-up-Authentifizierung erforderlich oder erfolgt war;
- ob eine Notfall- oder Wiederherstellungssitzung beteiligt war.

Vollständige Tokens oder Geheimnisse werden nicht gespeichert.

## 9. Autorisierungsnachweis

Für sicherheitsrelevante Vorgänge muss nachvollziehbar sein, auf welcher Autorisierungsgrundlage eine Handlung erlaubt, verweigert oder eingeschränkt wurde.

Ein Audit-Eintrag kann hierzu referenzieren auf:

- Autorisierungsergebnis;
- Berechtigungs-ID;
- Rollen-ID oder Rollenzuweisung;
- direkte `ALLOW`- oder `DENY`-Zuweisung;
- Whitelist- oder Blacklist-Regel;
- Ausnahmerecht;
- Delegation oder Stellvertretung;
- Organisations- oder Projektbeziehung;
- Richtlinienstand;
- erforderlichen und erreichten Authentifizierungsgrad.

Der Audit-Eintrag muss nicht die gesamte Policy-Engine duplizieren. Er muss aber eine spätere fachliche Rekonstruktion der maßgeblichen Entscheidung ermöglichen.

## 10. Erlaubte und verweigerte Vorgänge

Nicht nur erfolgreiche Handlungen können auditpflichtig sein.

Je nach Risiko und Richtlinie können ebenfalls auditpflichtig sein:

- verweigerte administrative Handlungen;
- fehlgeschlagene sicherheitskritische Authentifizierungen;
- `STEP_UP_REQUIRED`-Vorgänge;
- `INDETERMINATE`-Entscheidungen;
- versuchte Nutzung gesperrter Konten;
- versuchte Nutzung widerrufener Delegationen;
- sicherheitsrelevante Validierungsfehler.

Normale, erwartbare und risikoarme Fehler müssen nicht zwangsläufig vollständig auditiert werden.

## 11. Korrelations-ID

Zusammengehörige Vorgänge müssen über eine Korrelations-ID verknüpfbar sein können.

Dies ist insbesondere wichtig für:

- mehrstufige Freigaben;
- Vier-Augen-Prozesse;
- Projektänderungen mit mehreren Objektoperationen;
- Authentifizierung und anschließende Sitzungserzeugung;
- Delegationsaktivierung und nachfolgende Handlung;
- Rechtesimulation und spätere Änderungsanforderung;
- Synchronisations- oder Importvorgänge.

Eine Korrelations-ID ersetzt nicht die einzelnen Audit-IDs.

## 12. Vorgangskette

Komplexe Prozesse können mehrere Audit-Einträge erzeugen.

Beispiel:

```text
Änderung angefordert
        ↓
Rechtesimulation durchgeführt
        ↓
Freigabe angefordert
        ↓
zweite Identität genehmigt
        ↓
Änderung produktiv ausgeführt
        ↓
Sitzungen neu bewertet
```

Alle Einträge können über Korrelations- und Referenzbeziehungen zusammengeführt werden, ohne sie zu einem unstrukturierten Großdatensatz zu verschmelzen.

## 13. Unveränderlichkeit der Bedeutung

Persistierte Audit-Einträge dürfen nicht stillschweigend nachträglich in ihrer fachlichen Bedeutung verändert werden.

Korrekturen erfolgen durch neue, referenzierende Audit-Einträge oder ausdrücklich definierte Nachtragsmechanismen.

Damit bleibt nachvollziehbar:

- was ursprünglich erfasst wurde;
- warum eine Korrektur erforderlich war;
- wer die Korrektur veranlasst hat;
- welcher Stand als fachlich korrigiert gilt.

## 14. Integrität

Auditdaten müssen gegen unbemerkte Manipulation geschützt werden können.

Das fachliche Modell fordert mindestens:

- eindeutige Identitäten;
- nachvollziehbare Reihenfolge bzw. Zeitbezüge;
- erkennbare Korrekturen;
- überprüfbare Referenzen;
- keine stillschweigende Überschreibung bestehender Einträge;
- Erkennbarkeit von Integritätsverletzungen, soweit die Implementierung dies unterstützt.

Konkrete kryptografische Verkettung, Signatur oder Speichertechnologie wird hier nicht festgelegt.

## 15. Zeit

Audit benötigt einen nachvollziehbaren Zeitbezug.

Dabei ist zu unterscheiden zwischen:

- Zeitpunkt der fachlichen Handlung;
- Zeitpunkt der lokalen Erfassung;
- gegebenenfalls Zeitpunkt der Synchronisation oder zentralen Übernahme.

Bei Offline-Betrieb darf ein späterer Synchronisationszeitpunkt nicht den ursprünglichen lokalen Handlungszeitpunkt ersetzen.

Zeitquellen, Zeitzonen und bekannte Unsicherheiten müssen soweit erforderlich erkennbar sein.

## 16. Offline-First

Audit muss auch im vorgesehenen Offline-Betrieb funktionieren.

Lokale auditpflichtige Vorgänge werden lokal erfasst und dürfen nicht verloren gehen, nur weil ein externer Auditdienst nicht erreichbar ist.

Bei Wiederverbindung gilt:

- lokale Einträge werden kontrolliert synchronisiert;
- ursprüngliche Audit-ID und lokaler Handlungszeitpunkt bleiben erhalten;
- Konflikte oder Integritätsprobleme werden sichtbar;
- doppelte Einträge werden nicht stillschweigend als neue Vorgänge interpretiert;
- lokale und zentrale Herkunft bleibt nachvollziehbar.

## 17. Synchronisation

Audit-Synchronisation darf bestehende Auditbedeutung nicht überschreiben.

Ein synchronisierter Eintrag kann zusätzliche Transport- oder Bestätigungsmetadaten erhalten, aber der ursprüngliche fachliche Inhalt bleibt nachvollziehbar.

Fehlerhafte Synchronisation darf nicht so dargestellt werden, als sei der Nachweis erfolgreich zentral übernommen worden.

## 18. Projektbezogenes Audit

Projektbezogene Auditvorgänge können insbesondere sein:

- Projekt angelegt;
- Projekt archiviert oder wiederhergestellt;
- Verantwortlichkeit geändert;
- kritische Konfiguration geändert;
- Release vorbereitet oder freigegeben;
- sicherheitsrelevante Projektoperation ausgeführt;
- irreversible oder besonders kritische Handlung angefordert bzw. bestätigt.

Normale fachliche Objektbearbeitung kann je nach Domäne primär über Historie nachvollzogen werden und muss nicht automatisch denselben Auditumfang erzeugen.

## 19. Identitäts- und Kontoaudit

Auditpflichtig sind je nach Richtlinie insbesondere:

- Identität angelegt, eingeschränkt, gesperrt oder stillgelegt;
- Konto angelegt, aktiviert, gesperrt, entsperrt oder stillgelegt;
- Identitätszuordnung eines Kontos geändert;
- Authentifizierungsverfahren registriert, entfernt oder rotiert;
- MFA-Konfiguration geändert;
- Notfall- oder Wiederherstellungsverfahren verwendet.

Geheimnisse selbst werden niemals in Auditdaten geschrieben.

## 20. Sitzungs- und Authentifizierungsaudit

Sicherheitsrelevante Sitzungs- und Authentifizierungsvorgänge können insbesondere umfassen:

- erfolgreiche Authentifizierung;
- sicherheitsrelevanter Fehlversuch;
- Step-up-Vorgang;
- Sitzung erzeugt;
- Sitzung beendet;
- Sitzung abgelaufen;
- Sitzung widerrufen;
- Notfallsitzung gestartet oder beendet;
- sicherheitsbedingte Einschränkung.

Auditumfang und Aufbewahrung dürfen nach Risikoklasse differenziert werden.

## 21. Rollen- und Berechtigungsaudit

Mindestens folgende Änderungen müssen auditierbar sein:

- Rollendefinition angelegt oder geändert;
- Berechtigungsbündel einer Rolle geändert;
- Rollenzuweisung erteilt, geändert oder widerrufen;
- Berechtigungsdefinition geändert;
- direkte `ALLOW`-Zuweisung erteilt oder entzogen;
- direkte `DENY`-Zuweisung erteilt oder aufgehoben;
- Risikoklasse oder Delegierbarkeit geändert;
- Ausnahmerecht gewährt, geändert, verwendet oder widerrufen;
- Whitelist-/Blacklist-Regel geändert.

Besonders kritische Rechte müssen eine erhöhte Nachweistiefe unterstützen können.

## 22. Delegationsaudit

Mindestens folgende Delegationsvorgänge müssen auditierbar sein:

- Delegation angelegt;
- freigegeben oder abgelehnt;
- aktiviert;
- Umfang geändert;
- verlängert;
- pausiert;
- widerrufen;
- abgelaufen;
- weiterdelegiert;
- Stellvertretung aktiviert oder beendet;
- Nachfolge aktiviert;
- delegierte sicherheitskritische Handlung ausgeführt.

Bei der Handlung bleiben ausführende und delegierende bzw. vertretene Identität getrennt sichtbar.

## 23. Organisationsaudit

Mindestens folgende Organisationsvorgänge müssen auditierbar sein:

- Organisation oder Organisationseinheit angelegt oder geändert;
- Organisationseinheit verschoben oder stillgelegt;
- Team oder Gruppe geändert;
- Zugehörigkeit angelegt, aktiviert, pausiert, beendet oder widerrufen;
- externe Mitgliedschaft verlängert;
- Verantwortlicher geändert;
- Organisationshierarchie geändert;
- organisationsbezogene Rolle oder Richtlinie geändert;
- organisationsbezogene Delegation aktiviert oder widerrufen.

## 24. Vier-Augen-Prinzip

Bei vier-augen-pflichtigen Vorgängen muss Audit die tatsächlich unabhängigen beteiligten Akteursidentitäten getrennt nachweisen können.

Mindestens unterscheidbar sind:

- Antragsteller bzw. Auslöser;
- prüfende oder freigebende Identität;
- gegebenenfalls ausführende Identität;
- Zeitpunkt der einzelnen Schritte;
- jeweils verwendeter Autorisierungskontext;
- Ergebnis der Freigabe.

Zwei Konten derselben Akteursidentität dürfen auditseitig nicht als zwei unabhängige Personen erscheinen.

## 25. Notfall- und Ausnahmepfade

Notfallzugriffe und Ausnahmerechte benötigen besonders deutliche Auditspuren.

Mindestens müssen nachvollziehbar sein:

- Auslöser;
- begünstigte bzw. handelnde Identität;
- gewährende oder bestätigende Instanz;
- Begründung;
- Gültigkeitsbereich;
- Beginn und Ende;
- tatsächlich ausgeführte kritische Handlungen;
- nachträgliche Review- oder Abschlussentscheidung, soweit vorgesehen.

## 26. Rechtesimulation

Reine Rechtesimulation verändert keine produktiven Autorisierungsdaten.

Trotzdem kann sie sicherheitsrelevant sein.

Auditierbar sein können insbesondere:

- privilegierte Simulation für andere Benutzer;
- Simulation kritischer administrativer Rechte;
- verwendeter Ausgangsstand;
- simulierter Projekt- oder Organisationskontext;
- Ersteller des Szenarios;
- Übernahme eines Szenarios in eine produktive Änderungsanforderung.

Das vollständige hypothetische Simulationsmodell muss nicht zwangsläufig dauerhaft im Audit dupliziert werden. Eine nachvollziehbare Szenarioreferenz genügt, sofern der relevante Stand reproduzierbar bleibt.

## 27. Sicherheitsereignis und Audit

Sicherheitsereignis und Audit sind verwandte, aber nicht identische Konzepte.

Ein `SecurityEvent` beschreibt ein sicherheitsrelevantes Ereignis für Erkennung, Bewertung oder Reaktion.

Ein Audit-Eintrag beschreibt den Nachweis eines Vorgangs.

Ein Sicherheitsereignis kann:

- auf einen oder mehrere Audit-Einträge referenzieren;
- aus Auditdaten abgeleitet werden;
- zusätzliche Risikobewertung oder Reaktionsinformationen enthalten.

Es darf keine voneinander unabhängige widersprüchliche Sicherheits- und Auditwahrheit entstehen.

## 28. Datenschutz und Datenminimierung

Audit darf nicht zum unkontrollierten Sammelspeicher werden.

Es gilt Datenminimierung.

Insbesondere dürfen nicht gespeichert werden:

- Klartextkennwörter;
- private Schlüssel;
- vollständige Sitzungstokens;
- vollständige Authentifizierungstokens;
- geheime Recovery-Codes;
- unnötige personenbezogene Inhalte;
- vollständige fachliche Nutzdaten, wenn eine stabile Referenz ausreicht.

## 29. Aufbewahrung

Auditdaten können anderen Aufbewahrungsanforderungen unterliegen als normale Projekt- oder Workspace-Daten.

Das Modell muss unterschiedliche Aufbewahrungsklassen unterstützen können.

Eine konkrete gesetzliche oder organisatorische Frist wird in diesem Dokument nicht festgelegt.

Löschung, Anonymisierung oder Archivierung muss mit Nachweispflicht, Datenschutz und Referenzintegrität abgestimmt werden.

## 30. Anonymisierung und historische Referenzen

Personenbezogene Attribute können abhängig von Richtlinie anonymisiert oder eingeschränkt werden müssen.

Dabei soll die fachliche Nachvollziehbarkeit eines historischen Vorgangs soweit erforderlich erhalten bleiben.

Es ist zu unterscheiden zwischen:

- stabiler historischer Akteursreferenz;
- aktuell auflösbaren Profildaten;
- datenschutzbedingt entfernten oder eingeschränkten Attributen.

## 31. Suche und Auswertung

Audit muss innerhalb zulässiger Sichtbarkeitsgrenzen auswertbar sein.

Such- und Filterkriterien können insbesondere sein:

- Audit-ID;
- Korrelations-ID;
- Akteursidentität;
- Konto oder Sitzung;
- Projekt;
- Organisation;
- Zielobjekt;
- Handlung;
- Ergebnis;
- Zeitraum;
- Berechtigungs-ID;
- Rollen- oder Delegationsreferenz;
- Risikoklasse;
- Notfall- oder Ausnahmebezug.

Suche muss Auditberechtigungen und Datenschutzgrenzen beachten.

## 32. Z_Cockpit

`Z_Cockpit` darf Auditdaten anzeigen und analysieren, ist aber nicht die Source of Truth.

Mindestens vorgesehen sind:

- zeitliche Auditansicht;
- Filter nach Benutzer, Projekt, Organisation und Vorgang;
- Anzeige von Autorisierungsergebnis und Rechteherkunft;
- Delegations- und Stellvertretungsbezug;
- Vier-Augen- und Freigabeketten;
- Notfall- und Ausnahmemarkierungen;
- Korrelations- bzw. Vorgangsketten;
- Offline-/Synchronisationsstatus;
- Hinweise auf Integritäts- oder Rekonstruktionsprobleme.

Auditinformationen dürfen nur dargestellt werden, wenn der aktuelle Benutzer zur Einsicht berechtigt ist.

## 33. Z_Cockpit und Rechtesimulation

Z_Cockpit muss klar zwischen produktivem Audit und hypothetischer Simulation unterscheiden.

Ein Simulationsresultat wird nicht als tatsächlich ausgeführte Berechtigungsänderung dargestellt.

Wird ein Simulationsszenario später in eine produktive Änderungsanforderung übernommen, sollen Simulation und produktiver Vorgang über Referenz oder Korrelationsbezug nachvollziehbar verbunden werden können.

## 34. Read-Model

Für Cockpit, Reporting und Analyse dürfen nicht-autoritative Audit-Read-Models aufgebaut werden.

Sie können insbesondere vorberechnen:

- Vorgangsketten;
- Freigabeketten;
- Rechteherkunft;
- ungewöhnliche Häufungen;
- ablaufende Ausnahmerechte;
- delegierte kritische Handlungen;
- organisations- oder projektbezogene Sicherheitsänderungen.

Read-Models dürfen ursprüngliche Auditdaten nicht ersetzen oder stillschweigend verändern.

## 35. Export und Nachweis

Auditdaten können für interne oder externe Nachweise exportiert werden müssen.

Ein Export muss mindestens erkennen lassen:

- zugrunde liegenden Datenstand;
- Filter- und Auswahlbereich;
- Erstellungszeitpunkt;
- erstellende Identität oder Instanz;
- gegebenenfalls bekannte Einschränkungen oder fehlende Daten.

Ein Export ist eine abgeleitete Darstellung und nicht die primäre Auditquelle.

## 36. Fehlerfälle

Kann ein auditpflichtiger Vorgang nicht ausreichend auditiert werden, darf dies bei sicherheits- oder nachweiskritischen Operationen nicht stillschweigend ignoriert werden.

Je nach Richtlinie kann daraus folgen:

- Vorgang wird verweigert;
- Vorgang wird als eingeschränkt behandelt;
- lokaler Auditpuffer wird verwendet;
- ein deutliches Sicherheitsereignis wird erzeugt.

Welcher Modus gilt, wird durch Risiko und Betriebsrichtlinie bestimmt.

## 37. Audit und atomare Operationen

Bei fachlich atomaren Operationen muss Audit den tatsächlichen Ausgang korrekt widerspiegeln.

Ein fehlgeschlagener Schreibvorgang darf nicht als erfolgreiche fachliche Änderung auditiert werden.

Es kann stattdessen einen Audit- oder Fehlernachweis über den fehlgeschlagenen Versuch geben, wenn dieser auditpflichtig ist.

Damit bleibt insbesondere die Save-/Save-As-Semantik erhalten: Erst ein erfolgreich abgeschlossener atomarer Schreibvorgang darf als erfolgreiche Persistenzhandlung gelten.

## 38. Validierung

Ein Audit-Eintrag ist mindestens darauf zu prüfen, dass:

1. eine eindeutige Audit-ID vorhanden ist;
2. Audittyp bzw. Vorgangstyp bekannt ist;
3. Zeitpunkt vorhanden und syntaktisch gültig ist;
4. handelnde Akteursidentität vorhanden ist, sofern der Vorgang einen Akteur besitzt;
5. Ziel und Handlung soweit erforderlich eindeutig referenziert sind;
6. Ergebnis bekannt ist;
7. Delegations- oder Stellvertretungsbezüge konsistent sind;
8. Korrelationsreferenzen gültig sind, soweit vorhanden;
9. keine verbotenen Geheimnisse enthalten sind;
10. Nachträge bestehende Einträge nicht stillschweigend überschreiben;
11. Offline- und Synchronisationsstatus konsistent sind;
12. sicherheitsrelevante Autorisierungsreferenzen nachvollziehbar sind.

## 39. Invarianten

1. Audit und fachliche Objekthistorie sind getrennt.
2. Persistierte Audit-Einträge werden nicht stillschweigend in ihrer Bedeutung überschrieben.
3. Die tatsächlich handelnde Akteursidentität bleibt nachvollziehbar.
4. Delegation und Stellvertretung verschmelzen keine Identitäten.
5. Konto und Sitzung ersetzen nicht die Akteursidentität.
6. Audit speichert keine Kennwörter, privaten Schlüssel oder vollständigen Tokens.
7. Ein fehlgeschlagener Vorgang wird nicht als erfolgreicher Vorgang auditiert.
8. Offline-Erfassung erhält ursprüngliche Identität und Handlungszeit.
9. Synchronisation erzeugt keine zweite widersprüchliche Auditwahrheit.
10. Z_Cockpit ist nicht die Source of Truth für Audit.
11. Read-Models und Exporte sind Ableitungen.
12. Simulation wird nicht als produktive Änderung auditiert.
13. Vier-Augen-Nachweise beziehen sich auf tatsächlich unabhängige Akteursidentitäten.
14. Korrekturen erfolgen nachvollziehbar und nicht durch unsichtbare Überschreibung.
15. Datenschutz und Nachweispflicht müssen gemeinsam berücksichtigt werden.

## 40. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- konkrete Datenbanktabellen;
- konkretes Logformat;
- konkrete SIEM- oder Monitoringprodukte;
- konkrete Hash-, Signatur- oder Verkettungsalgorithmen;
- konkrete gesetzliche Aufbewahrungsfristen;
- konkrete GUI-Layouts;
- konkrete Exportformate;
- technische Zeitserver;
- vollständige Security-Event-Implementierung.

## 41. Folgemodelle

Auf diesem Modell bauen insbesondere auf:

- spätere Auditdienste;
- Sicherheitsereignis- und Monitoringmodelle;
- Z_Cockpit-Audit-Read-Models;
- Compliance- und Nachweisfunktionen;
- Freigabe- und Vier-Augen-Workflows;
- spätere Projektgedächtnis- und Wissensbeziehungen.

## 42. Abhängigkeiten

Dieses Dokument basiert insbesondere auf:

- `PLATFORM_MODEL.md`;
- `PROJECT_MODEL.md`;
- `WORKSPACE_MODEL.md`;
- `IDENTITY_MODEL.md`;
- `USER_MODEL.md`;
- `ACCOUNT_MODEL.md`;
- `AUTHENTICATION_MODEL.md`;
- `SESSION_MODEL.md`;
- `AUTHORIZATION_MODEL.md`;
- `ROLE_MODEL.md`;
- `PERMISSION_MODEL.md`;
- `DELEGATION_MODEL.md`;
- `ORGANIZATION_MODEL.md`;
- `RELATION_MODEL.md`;
- `Z_COCKPIT_IDENTITY_INTEGRATION.md`;
- `Z_COCKPIT_AUTHORIZATION_SIMULATION.md`.

## 43. Ergebnis

ProjectOS besitzt ein eigenständiges kanonisches Auditmodell für sicherheits-, verantwortungs-, freigabe- und nachweisrelevante Vorgänge.

Audit bleibt von fachlicher Historie getrennt, hält tatsächliche Akteure und Autorisierungskontexte nachvollziehbar, unterstützt Delegation, Organisation, Vier-Augen-Prinzip, Offline-Betrieb und Rechtesimulation und verhindert, dass Z_Cockpit, Logs oder technische Speicherformen zu konkurrierenden Auditquellen werden.
