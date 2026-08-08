# Berechtigungsmodell

**Dokument-ID:** PLT-0012  
**Titel:** Fachliches Modell von Berechtigungen  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert Berechtigungen als stabile, referenzierbare Beschreibungen fachlicher Handlungen innerhalb von ProjectOS.

Eine Berechtigung beschreibt, welche Handlung grundsätzlich autorisierbar ist. Sie trifft selbst keine Autorisierungsentscheidung.

## 2. Architekturstellung

Das Berechtigungsmodell gehört zur Plattformebene und baut insbesondere auf `AUTHORIZATION_MODEL.md`, `ROLE_MODEL.md`, `IDENTITY_MODEL.md`, `PROJECT_MODEL.md` und `RELATION_MODEL.md` auf.

Die Autorisierungsplattform wertet Berechtigungen im jeweiligen Kontext aus.

## 3. Grundsatz

Für Berechtigungen gilt:

```text
Berechtigungsdefinition
    ↓ wird zugeordnet über
Rolle / direkte Zuweisung / Delegation
    ↓ wird eingeschränkt durch
Gültigkeitsbereich / Verweigerung / Richtlinie
    ↓ wird ausgewertet durch
Autorisierung
```

Eine vorhandene Berechtigungsreferenz bedeutet daher nicht automatisch `ALLOW`.

## 4. Berechtigungsidentität

Jede Berechtigung besitzt eine stabile Berechtigungs-ID.

Die Berechtigungs-ID:

- ist unabhängig von Anzeigename und Übersetzung;
- bleibt bei sprachlicher oder redaktioneller Änderung erhalten;
- wird nicht für fachlich andere Handlungen wiederverwendet;
- ist maschinenlesbar und dauerhaft referenzierbar;
- darf nicht aus Benutzer-, Rollen- oder Projekt-IDs abgeleitet werden.

## 5. Berechtigungsdefinition

Eine Berechtigungsdefinition beschreibt mindestens:

- stabile Berechtigungs-ID;
- fachlichen Namen;
- Beschreibung und Zweck;
- Operation bzw. Handlungsart;
- zulässige Zieltypen;
- zulässige Gültigkeitsbereiche;
- Risikoklasse;
- erforderlichen minimalen Authentifizierungsgrad, soweit vorgesehen;
- optionale Zusatzbedingungen;
- Lebenszyklusstatus;
- Version;
- Historien- und Auditbezüge.

## 6. Operation und Ziel

Eine Berechtigung beschreibt eine Operation auf einem Ziel oder Zieltyp.

Konzeptionelle Beispiele:

- `project.read`;
- `project.update`;
- `project.archive`;
- `identity.read`;
- `user.manage`;
- `role.assign`;
- `permission.grant`;
- `simulation.start`;
- `release.approve`;
- `audit.read`.

Die konkrete technische Benennung wird später in einem Berechtigungskatalog verbindlich festgelegt.

## 7. Berechtigungskatalog

ProjectOS benötigt einen zentralen Berechtigungskatalog.

Dieser Katalog ist die maßgebliche Quelle für gültige Berechtigungs-IDs und deren fachliche Bedeutung.

Rollen, direkte Zuweisungen, Delegationen und Richtlinien dürfen nur auf bekannte oder ausdrücklich versioniert erweiterte Berechtigungen verweisen.

Domänen dürfen eigene fachliche Berechtigungen ergänzen, ohne bestehende Plattformberechtigungen umzudeuten.

## 8. Plattform- und Domänenberechtigungen

Berechtigungen können mindestens unterschieden werden in:

- Core-nahe technische Plattformberechtigungen;
- Projektberechtigungen;
- Identitäts- und Benutzerverwaltungsberechtigungen;
- Sicherheits- und Administrationsberechtigungen;
- Auditberechtigungen;
- Workspace-Berechtigungen;
- domänenspezifische Berechtigungen.

Domänenberechtigungen bleiben Eigentum der jeweiligen Domäne, werden aber durch dieselbe Autorisierungsplattform ausgewertet.

## 9. Granularität

Berechtigungen sollen fachlich ausreichend granular, aber nicht unnötig mikroskopisch sein.

Zu grobe Berechtigungen erzeugen übermäßige Rechte. Zu feine Berechtigungen erzeugen schwer wartbare Rollen und Richtlinien.

Die Granularität muss deshalb entlang fachlicher Handlungen geschnitten werden.

## 10. Lesen, Ändern, Freigeben

Lesen, Ändern und Freigeben sind grundsätzlich unterschiedliche Berechtigungsarten.

Aus `read` folgt nicht `update`.

Aus `update` folgt nicht automatisch `approve`.

Aus `approve` folgt nicht automatisch administrative Verwaltung.

## 11. Administrative Berechtigungen

Administrative Berechtigungen sind besonders sensibel.

Beispiele sind:

- Identitäten verwalten;
- Konten sperren oder entsperren;
- Rollen definieren;
- Rollen zuweisen;
- direkte Berechtigungen gewähren;
- Blacklist-/Whitelist-Regeln ändern;
- Ausnahmerechte gewähren;
- Sicherheitsrichtlinien ändern.

Solche Berechtigungen müssen möglichst eng geschnitten, besonders auditiert und gegebenenfalls mit erhöhtem Authentifizierungsgrad abgesichert werden.

## 12. Direkte Berechtigungszuweisung

Eine Berechtigung kann einer Akteursidentität direkt zugewiesen werden, wenn eine rollenbasierte Abbildung fachlich nicht geeignet ist.

Eine direkte Zuweisung beschreibt mindestens:

- Zuweisungs-ID;
- Akteursidentität;
- Berechtigungs-ID;
- Wirkung `ALLOW` oder `DENY`;
- Gültigkeitsbereich;
- Zielreferenz, soweit erforderlich;
- Beginn;
- optionales Ende;
- Begründung;
- ausstellende bzw. freigebende Identität;
- Status;
- Auditbezug.

Direkte Zuweisungen dürfen nicht als versteckte Benutzerflags umgesetzt werden.

## 13. `ALLOW`

`ALLOW` bezeichnet eine positive Berechtigungsquelle.

Sie kann insbesondere stammen aus:

- Rolle;
- direkter Berechtigungszuweisung;
- gültiger Delegation;
- kontrolliertem Ausnahmerecht;
- formal definierter System- oder Dienstregel.

Eine `ALLOW`-Quelle bleibt den Einschränkungen des Autorisierungsmodells unterworfen.

## 14. `DENY`

`DENY` bezeichnet eine ausdrückliche Verweigerung.

Eine Verweigerung kann insbesondere stammen aus:

- direkter `DENY`-Zuweisung;
- Blacklist-Regel;
- Sicherheitsrichtlinie;
- Kontextbedingung;
- Objekt- oder Bereichssperre.

Eine einschlägige Verweigerung ist sicherheitsrelevant und darf nicht durch eine allgemeinere Erlaubnis ignoriert werden.

## 15. Default-Deny

Wenn keine wirksame positive Berechtigungsquelle existiert, ist die Handlung nicht erlaubt.

Das Fehlen einer `DENY`-Regel ist keine Erlaubnis.

Damit bleibt der Grundsatz aus `AUTHORIZATION_MODEL.md` erhalten.

## 16. Gültigkeitsbereich

Jede Zuweisung oder Regel muss ihren Gültigkeitsbereich eindeutig beschreiben.

Mindestens vorgesehen sind:

- global;
- Organisation;
- Projekt;
- Workspace;
- Domäne;
- Objektgruppe;
- einzelnes Objekt;
- konkrete Operation oder Funktion;
- Sitzung.

Eine auf ein Projekt begrenzte Berechtigung darf nicht auf andere Projekte ausstrahlen.

## 17. Bereichsvererbung

Gültigkeitsbereiche können hierarchische Beziehungen besitzen.

Eine Berechtigung auf einem übergeordneten Bereich darf nur dann auf untergeordnete Bereiche wirken, wenn diese Vererbung ausdrücklich zulässig ist.

Vererbung muss:

- deterministisch;
- nachvollziehbar;
- begrenzbar;
- durch `DENY` oder spezifischere Regeln einschränkbar

sein.

## 18. Spezifität

Bei mehreren einschlägigen Regeln muss die fachliche Spezifität berücksichtigt werden.

Eine objektspezifische Regel kann beispielsweise enger sein als eine projektweite Regel.

Spezifität allein darf jedoch keine ausdrückliche Sicherheitsverweigerung außer Kraft setzen.

## 19. Konfliktauflösung

Für Berechtigungskonflikte gelten mindestens folgende fachliche Regeln:

1. Default-Deny.
2. Nur aktive, gültige und einschlägige Regeln werden berücksichtigt.
3. Eine explizite Verweigerung wird nicht durch eine allgemeinere Erlaubnis überstimmt.
4. Eine spezifischere Verweigerung schränkt eine weitere Erlaubnis ein.
5. Ein Ausnahmerecht darf nur den Konflikt übersteuern, für den es ausdrücklich gültig ist.
6. Abgelaufene oder widerrufene Ausnahmen sind unwirksam.
7. Sicherheitsrelevante Mehrdeutigkeit führt nicht zu `ALLOW`.
8. Das endgültige Ergebnis wird ausschließlich durch die Autorisierungsplattform erzeugt.

## 20. Whitelist

Whitelist-Regeln können Berechtigungen auf definierte Akteure, Ziele oder Bedingungen einschränken.

Sie definieren keinen neuen Berechtigungstyp, sondern wirken als zusätzliche Autorisierungsbedingung.

Eine Whitelist kann beispielsweise bedeuten:

> `permission.assign` ist nur für ausdrücklich zugelassene Administratoridentitäten im globalen Bereich zulässig.

## 21. Blacklist

Blacklist-Regeln werden als ausdrückliche Verweigerungsquellen behandelt.

Sie können sich auf Akteure, Konten, Geräte, Projekte, Ressourcen, Operationen oder andere kontrollierte Kriterien beziehen.

Blacklist-Einträge müssen begründet, gültigkeitsbezogen, versionierbar und auditierbar sein.

## 22. Ausnahmerechte

Ein Ausnahmerecht ist keine normale Berechtigung und keine normale Rolle.

Es referenziert eine oder mehrere bestehende Berechtigungen und erlaubt deren kontrollierte Nutzung trotz einer ansonsten wirksamen Einschränkung, sofern das Autorisierungsmodell dies für den konkreten Konflikt zulässt.

Ausnahmerechte müssen zeitlich oder durch eine eindeutige Widerrufsbedingung begrenzt sein.

## 23. Delegierbarkeit

Nicht jede Berechtigung ist delegierbar.

Die Berechtigungsdefinition kann festlegen:

- delegierbar;
- nur eingeschränkt delegierbar;
- nicht delegierbar;
- nur mit zusätzlicher Freigabe delegierbar.

Eine Delegation darf nie einen größeren Gültigkeitsbereich oder höhere Wirkung erzeugen, als die delegierende Identität wirksam übertragen darf.

## 24. Stellvertretung

Stellvertretung kann Berechtigungen nur innerhalb des ausdrücklich vorgesehenen Vertretungsumfangs wirksam machen.

Sie ist keine pauschale Kopie sämtlicher Rechte des Vertretenen.

Besonders persönliche oder nicht delegierbare Berechtigungen können von Stellvertretung ausgeschlossen werden.

## 25. Vier-Augen-Prinzip

Berechtigungen können als vier-augen-pflichtig gekennzeichnet werden.

Dann reicht eine einzelne erfolgreiche Autorisierung nicht aus; der zugehörige Workflow muss eine unabhängige zweite Identität mit passender Freigabeberechtigung prüfen.

Zwei Konten derselben Akteursidentität gelten dabei nicht als zwei unabhängige Personen.

## 26. Trennung von Aufgaben

ProjectOS muss Berechtigungen und Rollen so kombinieren können, dass unvereinbare Aufgaben getrennt bleiben.

Beispiele:

- `release.prepare` und unabhängiges `release.approve`;
- `permission.request` und alleinige `permission.grant`-Freigabe;
- `security.change` und unabhängige Sicherheitsfreigabe.

Diese Regeln werden durch Rollen-, Berechtigungs- und Autorisierungsmodell gemeinsam getragen.

## 27. Risikoklasse

Berechtigungen können einer Risikoklasse zugeordnet werden.

Konzeptionell können mindestens unterschieden werden:

- niedrig;
- normal;
- erhöht;
- kritisch.

Die Risikoklasse kann Einfluss haben auf:

- erforderlichen Authentifizierungsgrad;
- Auditumfang;
- Vier-Augen-Prinzip;
- Offline-Zulässigkeit;
- Ausnahmeregeln;
- notwendige Freigaben.

## 28. Authentifizierungsgrad

Eine Berechtigung kann einen minimalen Authentifizierungsgrad verlangen.

Ist dieser in der aktuellen Sitzung nicht erfüllt, erzeugt die Autorisierung gegebenenfalls `STEP_UP_REQUIRED` statt `ALLOW` oder endgültigem `DENY`.

Das Berechtigungsmodell definiert nur die Anforderung; die Authentifizierungsplattform erbringt den Nachweis.

## 29. Offline-First

Berechtigungsdefinitionen und für den vorgesehenen Offline-Betriebsumfang notwendige Zuweisungen müssen lokal verfügbar sein können.

Es muss erkennbar sein:

- auf welchem Berechtigungsstand die lokale Bewertung beruht;
- ob eine Berechtigung offline ausgewertet werden darf;
- ob eine Operation zwingend Online-Bestätigung benötigt;
- ob seit dem letzten bestätigten Stand möglicherweise sicherheitsrelevante Änderungen fehlen.

Kritische Berechtigungen können als nicht offline nutzbar markiert werden.

## 30. Versionierung

Berechtigungsdefinitionen sind versionierbar.

Eine Änderung der Bedeutung einer Berechtigungs-ID ist besonders kritisch.

Daher gilt:

- redaktionelle Klarstellungen können kompatibel sein;
- Erweiterungen von Zieltypen oder Gültigkeitsbereichen benötigen Kompatibilitätsprüfung;
- fachlich andere Handlungen benötigen eine neue Berechtigungs-ID;
- bestehende IDs dürfen nicht stillschweigend umgedeutet werden.

## 31. Deprecation

Berechtigungen können als veraltet markiert werden.

Eine veraltete Berechtigung darf für historische Auswertung erhalten bleiben, soll aber nicht mehr neu zugewiesen werden.

Migration auf Nachfolgerberechtigungen muss nachvollziehbar erfolgen.

## 32. Audit

Mindestens folgende Vorgänge müssen auditierbar sein:

- Berechtigungsdefinition angelegt oder geändert;
- Berechtigung deaktiviert oder als veraltet markiert;
- direkte `ALLOW`-Zuweisung erteilt oder entzogen;
- direkte `DENY`-Zuweisung erteilt oder aufgehoben;
- Gültigkeitsbereich geändert;
- Delegierbarkeit geändert;
- Risikoklasse geändert;
- besonders kritische Berechtigung vergeben;
- Ausnahmerecht auf eine Berechtigung angewendet.

## 33. Z_Cockpit

`Z_Cockpit` soll Berechtigungen transparent und erklärbar darstellen.

Mindestens sichtbar sein sollen:

- Berechtigungs-ID und Name;
- Beschreibung;
- Risikoklasse;
- zulässige Gültigkeitsbereiche;
- delegierbar oder nicht delegierbar;
- erforderlicher Authentifizierungsgrad;
- Rollen, die diese Berechtigung enthalten;
- direkte Zuweisungen;
- ausdrückliche Verweigerungen;
- Whitelist-/Blacklist-Einflüsse;
- Ausnahmerechte;
- effektive Wirkung je Benutzer und Kontext.

Das Cockpit soll nicht nur `ja/nein` anzeigen, sondern die Herkunft einer effektiven Berechtigung erklären können.

## 34. Berechtigungs-Read-Model

Für Cockpit, Reporting und Analyse darf ein nicht-autoritatives Read-Model aufgebaut werden.

Es kann beispielsweise darstellen:

- alle effektiven Berechtigungen einer Identität;
- Rechte je Projekt oder Organisation;
- Herkunft aus Rolle, direkter Zuweisung oder Delegation;
- widersprüchliche Regelquellen;
- bevorstehende Abläufe;
- nicht mehr verwendete Berechtigungen;
- besonders privilegierte Identitäten.

Dieses Read-Model darf sicherheitskritische Schreiboperationen nicht selbst autorisieren.

## 35. Validierung

Eine Berechtigungsdefinition ist mindestens darauf zu prüfen, dass:

1. die Berechtigungs-ID eindeutig ist;
2. die fachliche Handlung klar beschrieben ist;
3. zulässige Zieltypen definiert sind;
4. Gültigkeitsbereiche eindeutig sind;
5. Risikoklasse gültig ist;
6. Delegierbarkeit konsistent ist;
7. Authentifizierungsanforderungen bekannt sind;
8. keine bestehende ID fachlich umgedeutet wird;
9. Referenzen aus Rollen und Richtlinien auflösbar sind;
10. sicherheitsrelevante Änderungen auditierbar sind.

## 36. Invarianten

1. Eine Berechtigung ist keine Autorisierungsentscheidung.
2. Jede Berechtigung besitzt eine stabile ID.
3. `ALLOW` ohne gültigen Kontext erzeugt nicht automatisch Zugriff.
4. Das Fehlen von `DENY` ist keine Erlaubnis.
5. Direkte Rechte sind explizit, begrenzt und auditierbar.
6. Direkte Verweigerungen sind explizite Sicherheitsregeln.
7. Rollen und Berechtigungen bleiben getrennt.
8. Ausnahmerechte sind keine normalen Dauerberechtigungen.
9. Nicht delegierbare Rechte dürfen durch Delegation nicht übertragen werden.
10. Z_Cockpit ist nicht die Source of Truth.
11. Bestehende Berechtigungs-IDs werden nicht fachlich umgedeutet.
12. Sicherheitsrelevante Mehrdeutigkeit führt nicht zu `ALLOW`.

## 37. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- konkrete vollständige Berechtigungslisten;
- technische Policy-Engine;
- Datenbanktabellen;
- Programmiersprachen-Enums;
- konkrete UI-Bedienelemente;
- vollständige Delegationsprozesse;
- Organisationshierarchien;
- konkrete kryptografische oder Token-Verfahren.

## 38. Folgemodelle

Auf diesem Modell bauen insbesondere auf:

- `DELEGATION_MODEL.md`;
- `ORGANIZATION_MODEL.md`;
- `AUDIT_MODEL.md`;
- spätere Autorisierungsdienste;
- der versionierte Berechtigungskatalog;
- Z_Cockpit-Read-Models für Rechte und Sicherheitsanalyse.

## 39. Abhängigkeiten

Dieses Dokument basiert insbesondere auf:

- `PLATFORM_MODEL.md`;
- `IDENTITY_MODEL.md`;
- `USER_MODEL.md`;
- `ACCOUNT_MODEL.md`;
- `AUTHENTICATION_MODEL.md`;
- `SESSION_MODEL.md`;
- `AUTHORIZATION_MODEL.md`;
- `ROLE_MODEL.md`;
- `PROJECT_MODEL.md`;
- `RELATION_MODEL.md`;
- `Z_COCKPIT_IDENTITY_INTEGRATION.md`.

## 40. Ergebnis

ProjectOS besitzt ein eigenständiges fachliches Berechtigungsmodell mit stabilen Berechtigungs-IDs, klaren Gültigkeitsbereichen, positiver und negativer Wirkung, kontrollierter Delegierbarkeit, Risikoklassen und nachvollziehbarer Versionierung.

Damit können Rollen, direkte Zuweisungen, Verweigerungen, Delegationen und Ausnahmerechte auf einen gemeinsamen Berechtigungskatalog verweisen, während die endgültige Entscheidung weiterhin ausschließlich durch die Autorisierungsplattform getroffen wird.
