# Autorisierungsmodell

**Dokument-ID:** PLT-0010  
**Titel:** Fachliches Modell der Autorisierung  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert, wie ProjectOS entscheidet, ob eine Akteursidentität eine konkrete Handlung in einem konkreten Gültigkeitsbereich ausführen darf.

Autorisierung beantwortet die Frage:

> Darf dieser Akteur diese Handlung auf diesem Ziel unter diesen Bedingungen jetzt ausführen?

Authentifizierung beantwortet dagegen nur, ob die behauptete Identität hinreichend nachgewiesen wurde.

## 2. Architekturstellung

Das Autorisierungsmodell gehört zur Plattformebene und baut insbesondere auf `IDENTITY_MODEL.md`, `USER_MODEL.md`, `ACCOUNT_MODEL.md`, `AUTHENTICATION_MODEL.md`, `SESSION_MODEL.md` und `RELATION_MODEL.md` auf.

Die Plattform trifft die Autorisierungsentscheidung. Core und Domänen dürfen eine erforderliche Entscheidung anfordern und deren Ergebnis beachten, definieren aber nicht unabhängig eine zweite Berechtigungslogik.

## 3. Grundsatz

Eine Autorisierungsentscheidung ist kontextbezogen und wird nicht allein aus einer Rolle oder einem Benutzerattribut abgeleitet.

Mindestens können einfließen:

- handelnde Akteursidentität;
- gegebenenfalls vertretene oder delegierende Identität;
- Handlung;
- Zielressource oder Zielobjekt;
- Gültigkeitsbereich;
- Rollen;
- direkte Berechtigungen;
- ausdrückliche Verweigerungen;
- Whitelist- und Blacklist-Regeln;
- Ausnahmerechte;
- Projekt- und Organisationsbeziehungen;
- Delegationen und Stellvertretungen;
- Sitzungskontext;
- Authentifizierungsgrad;
- zeitliche Bedingungen;
- Sicherheits- und Richtlinienzustände.

## 4. Default-Deny

ProjectOS verwendet als Sicherheitsgrundsatz **Default-Deny**.

Eine Handlung ist nicht deshalb erlaubt, weil keine ausdrückliche Verbotsregel gefunden wurde. Es muss eine gültige Erlaubnis oder ein zulässiger Ausnahmeweg vorliegen.

Unvollständige, nicht auflösbare oder widersprüchliche sicherheitsrelevante Informationen dürfen nicht stillschweigend zu einer Erlaubnis führen.

## 5. Autorisierungsanfrage

Eine Autorisierungsanfrage beschreibt mindestens:

- Akteursidentitäts-ID;
- Sitzungs-ID, soweit vorhanden;
- gewünschte Handlung;
- Zieltyp und Zielidentität;
- Gültigkeitsbereich;
- Zeitpunkt;
- gegebenenfalls Projekt-, Organisations-, Workspace- oder Domänenkontext;
- gegebenenfalls Delegations- oder Stellvertretungskontext;
- erforderlichen Authentifizierungsgrad;
- technische Korrelations-ID für Audit und Nachvollziehbarkeit.

## 6. Autorisierungsergebnis

Ein Ergebnis ist mindestens:

- `ALLOW` – Handlung ist zulässig;
- `DENY` – Handlung ist nicht zulässig;
- `STEP_UP_REQUIRED` – höherer Authentifizierungsgrad ist erforderlich;
- `CONTEXT_REQUIRED` – notwendiger Gültigkeits- oder Entscheidungskontext fehlt;
- `INDETERMINATE` – Entscheidung kann wegen fehlerhafter oder widersprüchlicher Daten nicht sicher getroffen werden.

`INDETERMINATE` darf bei einer schreibenden oder sicherheitsrelevanten Handlung nicht wie `ALLOW` behandelt werden.

## 7. Berechtigung

Eine Berechtigung beschreibt eine erlaubbare fachliche Handlung oder Handlungsgruppe.

Beispiele sind konzeptionell:

- Projekt lesen;
- Projekt ändern;
- Benutzer verwalten;
- Rolle zuweisen;
- Freigabe erteilen;
- Simulation starten;
- Konfiguration ändern;
- Audit einsehen.

Die kanonische Struktur einzelner Berechtigungen wird in `PERMISSION_MODEL.md` definiert.

## 8. Rolle

Eine Rolle bündelt Berechtigungen für einen fachlichen Verantwortungs- oder Arbeitskontext.

Eine Rolle ist keine Identität und keine Berechtigung.

Rollen können beispielsweise projekt-, organisations- oder domänenbezogen zugewiesen werden.

Die konkrete Rollenstruktur wird in `ROLE_MODEL.md` definiert.

## 9. Direkte Berechtigungen

Neben Rollen können direkte Berechtigungszuweisungen erforderlich sein.

Direkte Zuweisungen müssen:

- explizit sein;
- einen Gültigkeitsbereich besitzen;
- nachvollziehbar begründet werden können;
- widerrufbar sein;
- auditierbar sein.

Sie dürfen nicht als unsichtbare dauerhafte Sonderrechte im Benutzerprofil abgelegt werden.

## 10. Ausdrückliche Verweigerung

ProjectOS unterstützt ausdrückliche Verweigerungen.

Eine gültige, spezifische Verweigerung muss bei der Berechnung effektiver Berechtigungen berücksichtigt werden und darf nicht allein durch eine allgemeinere Rollenfreigabe verschwinden.

Die genaue Konfliktordnung wird im `PERMISSION_MODEL.md` präzisiert. Grundsätzlich gilt sicherheitsorientiert: Eine einschlägige ausdrückliche Verweigerung besitzt Vorrang, sofern kein formal definierter und auditierter Ausnahmeweg diese gezielt übersteuert.

## 11. Whitelist

Eine Whitelist-Regel kann den zulässigen Umfang einer ansonsten erlaubten Handlung auf ausdrücklich benannte Akteure, Ziele, Bereiche oder Bedingungen beschränken.

Whitelist ist keine globale Benutzerkennzeichnung.

Eine Regel besitzt mindestens:

- Regel-ID;
- Gültigkeitsbereich;
- Ziel bzw. Ressourcengruppe;
- erlaubte Akteure oder Kriterien;
- betroffene Handlungen;
- Begründung;
- Beginn und gegebenenfalls Ende;
- ausstellende bzw. freigebende Identität;
- Auditbezug.

## 12. Blacklist

Eine Blacklist-Regel verweigert eine ansonsten möglicherweise vorhandene Berechtigung für bestimmte Akteure, Ziele, Bereiche oder Bedingungen.

Blacklist ist ebenfalls keine unveränderliche Eigenschaft eines Benutzers.

Eine aktive einschlägige Blacklist-Regel wird als ausdrückliche Verweigerung behandelt, sofern nicht ein formal zulässiges Ausnahmerecht ausdrücklich für genau diesen Konflikt vorgesehen ist.

## 13. Ausnahmerechte

Ausnahmerechte erlauben kontrollierte Abweichungen von regulären Berechtigungsregeln.

Sie müssen mindestens besitzen:

- eindeutige Ausnahme-ID;
- begünstigte Akteursidentität;
- gewährende Identität oder Instanz;
- konkret erlaubte Handlung;
- Gültigkeitsbereich;
- Ziel oder Zielgruppe;
- fachliche Begründung;
- Beginn;
- Ablauf oder explizite Widerrufsbedingung;
- erforderlichen Authentifizierungsgrad;
- Auditpflicht.

Unbefristete oder unbegründete Ausnahmerechte sind zu vermeiden und müssen besonders kenntlich gemacht werden.

Ein Ausnahmerecht darf niemals unsichtbar eine Regel umgehen.

## 14. Notfallzugriff

Für definierte Notfälle kann ein besonders kontrollierter Ausnahmeweg vorgesehen werden.

Ein Notfallzugriff muss mindestens:

- ausdrücklich aktiviert werden;
- eine Begründung verlangen;
- zeitlich eng begrenzt sein;
- erhöhten Authentifizierungsgrad verlangen, soweit technisch möglich;
- vollständig auditiert werden;
- im Z_Cockpit deutlich sichtbar sein;
- nachträglich reviewbar sein.

Notfallzugriff ist kein Ersatz für reguläre Rollen- oder Delegationsmodelle.

## 15. Gültigkeitsbereiche

Berechtigungen und Regeln können insbesondere gelten für:

- global;
- Organisation;
- Projekt;
- Workspace;
- Domäne;
- Objektgruppe;
- einzelnes Objekt;
- konkrete Funktion oder Operation;
- Sitzung.

Ein engerer Gültigkeitsbereich darf nicht unbeabsichtigt auf einen weiteren Bereich ausgeweitet werden.

## 16. Projektleitung

Die Beziehung `Projektleiter` beschreibt fachliche Verantwortung und kann Grundlage einer Rollen- oder Berechtigungszuweisung sein.

Sie ist jedoch nicht selbst identisch mit einer universellen Superuser-Berechtigung.

Welche Handlungen ein Projektleiter ausführen darf, wird durch Rollen- und Berechtigungsregeln definiert.

## 17. Stellvertretung

Eine Stellvertretung erlaubt einem Akteur, in einem ausdrücklich definierten Umfang für einen anderen Verantwortlichen zu handeln.

Dabei müssen getrennt bleiben:

- ursprünglicher Verantwortlicher;
- Stellvertreter;
- Aktivierungszustand;
- Gültigkeitsbereich;
- übertragener Umfang;
- Beginn und Ende;
- konkrete ausführende Sitzung.

Eine eingetragene Stellvertretung bedeutet nicht automatisch, dass sämtliche Rechte des Vertretenen übertragen werden.

## 18. Vertrauensperson

Die Beziehung `Vertrauensperson` beschreibt zunächst eine besondere Vertrauens- oder Eskalationsbeziehung.

Sie besitzt ohne zusätzliche Regel keine automatische administrative Berechtigung.

Mögliche Funktionen wie Wiederherstellungsfreigabe, Eskalation oder Mitwirkung an Notfallprozessen müssen jeweils ausdrücklich als Berechtigung oder Workflow definiert werden.

## 19. Nachfolger

Die Beziehung `Nachfolger` beschreibt eine vorgesehene Übernahme von Verantwortung.

Sie aktiviert Rechte nicht automatisch vor Eintritt der definierten Nachfolgebedingung.

Eine Nachfolge muss aktivierbar, nachvollziehbar und auditierbar sein. Zeitpunkt, Umfang und auslösende Bedingung müssen bekannt sein.

## 20. Delegation

Delegation überträgt einen begrenzten Teil von Befugnissen oder Verantwortlichkeiten von einer Identität an eine andere.

Eine Delegation besitzt mindestens:

- Delegations-ID;
- delegierende Identität;
- ausführende Identität;
- delegierte Berechtigungen oder Verantwortungen;
- Gültigkeitsbereich;
- Beginn und Ende;
- Weiterdelegierbarkeit, sofern zulässig;
- Widerrufszustand;
- Begründung;
- Auditbezug.

Die vollständige Semantik wird in `DELEGATION_MODEL.md` definiert.

## 21. Effektive Berechtigung

Die effektive Berechtigung ist das Ergebnis der Auswertung aller für eine konkrete Anfrage relevanten Regeln.

Konzeptionell wird in folgender Reihenfolge geprüft:

1. Ist die Identität und gegebenenfalls Sitzung grundsätzlich nutzbar?
2. Ist der notwendige Kontext vollständig und gültig?
3. Ist der erforderliche Authentifizierungsgrad erreicht?
4. Welche Rollen und direkten Erlaubnisse gelten im angefragten Gültigkeitsbereich?
5. Welche Delegationen oder Stellvertretungen sind aktiv und einschlägig?
6. Welche Whitelist-Beschränkungen gelten?
7. Welche ausdrücklichen Verweigerungen oder Blacklist-Regeln gelten?
8. Existiert ein formal zulässiges Ausnahmerecht für einen verbleibenden Konflikt?
9. Sind zusätzliche Richtlinien oder Sicherheitsbedingungen erfüllt?
10. Ergebnis erzeugen und sicherheitsrelevanten Entscheidungsnachweis erfassen.

Diese Reihenfolge ist ein fachlicher Entscheidungsrahmen und noch kein technischer Algorithmus.

## 22. Konfliktprinzipien

Mindestens gelten:

1. `Default-Deny`.
2. Fehlender Kontext erzeugt keine implizite Erlaubnis.
3. Spezifische Regeln werden in ihrem Gültigkeitsbereich berücksichtigt.
4. Ausdrückliche Verweigerungen können allgemeine Erlaubnisse sperren.
5. Ausnahmen müssen explizit auf den Konflikt anwendbar sein.
6. Abgelaufene, widerrufene oder noch nicht aktive Regeln sind unwirksam.
7. Delegation kann nicht mehr übertragen, als nach ihren Regeln delegierbar ist.
8. Eine Stellvertretung verschmilzt keine Identitäten.
9. Eine Rolle ist keine Superuser-Abkürzung außerhalb ihres Gültigkeitsbereichs.
10. Sicherheitsrelevante Mehrdeutigkeit führt nicht zu `ALLOW`.

## 23. Offline-First

Autorisierung muss im vorgesehenen Offline-Betriebsumfang möglich sein.

Dazu können lokal geprüfte Snapshots von Rollen, Berechtigungen, Delegationen und Richtlinien erforderlich sein.

Offline-Entscheidungen müssen erkennen lassen:

- auf welchem Autorisierungsstand sie beruhen;
- wann dieser Stand zuletzt bestätigt wurde;
- welche Regeln offline nicht prüfbar sind;
- ob die konkrete Operation offline zulässig ist.

Besonders kritische Operationen dürfen durch Richtlinie auf Online-Prüfung oder zusätzliche Freigabe beschränkt werden.

## 24. Änderungen an Berechtigungen

Änderungen an Rollen, Berechtigungen, Delegationen, Blacklists, Whitelists und Ausnahmerechten sind sicherheitsrelevante Operationen.

Sie müssen autorisiert und auditiert werden.

Eine Identität darf sich nicht allein dadurch zusätzliche Rechte verschaffen, dass sie ihre eigenen Autorisierungsdaten verändert.

Selbstfreigaben für besonders kritische Rechte können durch Richtlinie ausgeschlossen werden.

## 25. Vier-Augen-Prinzip

Für besonders kritische Operationen muss ein Vier-Augen-Prinzip modellierbar sein.

Dabei dürfen Anforderer und unabhängiger Freigeber nicht stillschweigend dieselbe wirksame Identität sein.

Das Vier-Augen-Prinzip kann insbesondere gelten für:

- Vergabe administrativer Rechte;
- Notfallausnahmen;
- kritische Freigaben;
- Sicherheitskonfiguration;
- irreversible Projektoperationen;
- definierte Compliance-Vorgänge.

## 26. Audit

Sicherheitsrelevante Autorisierungsentscheidungen müssen nachvollziehbar sein.

Ein Entscheidungsnachweis kann mindestens enthalten:

- Korrelations-ID;
- Akteursidentität;
- Sitzungs-ID;
- vertretene oder delegierende Identität, soweit relevant;
- Handlung;
- Ziel;
- Gültigkeitsbereich;
- Ergebnis;
- maßgebliche Regelreferenzen;
- Authentifizierungsgrad;
- Zeitpunkt;
- Begründung bei Ausnahme- oder Notfallzugriff.

Geheimnisse dürfen nicht in Auditdaten geschrieben werden.

## 27. Z_Cockpit

`Z_Cockpit` dient als zentrale Sicht- und Bedienoberfläche für die Autorisierungsplattform, ist aber nicht deren Source of Truth.

Das Cockpit soll später insbesondere darstellen können:

- effektive Rollen und Berechtigungen eines Benutzers;
- Herkunft einer Berechtigung;
- Gültigkeitsbereich;
- direkte Erlaubnisse und Verweigerungen;
- aktive Whitelist-/Blacklist-Regeln;
- Ausnahmerechte mit Ablauf und Begründung;
- Projektleiter und Stellvertretungen;
- Vertrauenspersonen und Nachfolger;
- Delegationen;
- ausstehende Freigaben;
- Notfallzugriffe;
- relevante Autorisierungs- und Auditereignisse.

Eine besonders wichtige Cockpit-Funktion ist die **Erklärbarkeit**:

> Warum darf oder darf ein Akteur eine bestimmte Handlung nicht ausführen?

Das Cockpit soll hierfür die maßgeblichen Regelquellen verständlich darstellen können, ohne selbst die Entscheidung neu zu berechnen.

## 28. Autorisierungs-Read-Model

Für UI, Reporting und Z_Cockpit darf ein abgeleitetes Read-Model aufgebaut werden.

Dieses darf beispielsweise effektive Berechtigungen, Rollenherkunft, Regelkonflikte und Ablaufdaten vorberechnen.

Das Read-Model ist nicht autoritativ. Schreibende oder sicherheitskritische Operationen müssen die zuständige Autorisierungsentscheidung verwenden und dürfen nicht allein einem möglicherweise veralteten Cockpit-Read-Model vertrauen.

## 29. Validierung

Eine Autorisierungsregel ist mindestens darauf zu prüfen, dass:

1. Regel-ID und Regeltyp eindeutig sind;
2. Akteur oder Zielgruppe eindeutig referenziert ist;
3. Handlung definiert ist;
4. Gültigkeitsbereich bekannt ist;
5. zeitliche Gültigkeit konsistent ist;
6. ausstellende oder verantwortliche Identität nachvollziehbar ist;
7. Ausnahme- und Notfallregeln eine Begründung besitzen;
8. Delegationen den delegierbaren Umfang nicht überschreiten;
9. widersprüchliche Regeln erkennbar bleiben;
10. sicherheitsrelevante Änderungen auditierbar sind.

## 30. Invarianten

1. Authentifizierung ist keine Autorisierung.
2. Identität besitzt nicht allein durch Existenz Rechte.
3. Rolle und Berechtigung sind getrennte Konzepte.
4. Autorisierung ist immer kontextbezogen.
5. Default-Deny gilt.
6. Blacklist und Whitelist sind Regeln, keine unveränderlichen Benutzerattribute.
7. Ausnahmerechte sind explizit, begründet, begrenzt und auditierbar.
8. Stellvertretung und Delegation verschmelzen keine Identitäten.
9. Vertrauensperson und Nachfolger erhalten nicht automatisch administrative Rechte.
10. Z_Cockpit ist nicht die Source of Truth der Autorisierung.
11. Ein veraltetes Read-Model darf keine sicherheitskritische Schreibentscheidung autorisieren.
12. Sicherheitsrelevante Mehrdeutigkeit wird nicht als Erlaubnis interpretiert.

## 31. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- konkrete Rollenlisten;
- vollständige Berechtigungskataloge;
- technische Policy-Engine;
- Programmiersprachen-APIs;
- Datenbanktabellen;
- Tokenformate;
- konkrete kryptografische Verfahren;
- GUI-Layout des Z_Cockpit;
- vollständige Delegations-Workflows;
- Organisationshierarchien.

## 32. Folgemodelle

Auf diesem Modell bauen insbesondere auf:

- `ROLE_MODEL.md`;
- `PERMISSION_MODEL.md`;
- `DELEGATION_MODEL.md`;
- `ORGANIZATION_MODEL.md`;
- `AUDIT_MODEL.md`;
- spätere Autorisierungsdienste und Cockpit-Read-Models.

## 33. Abhängigkeiten

Dieses Dokument basiert insbesondere auf:

- `PLATFORM_MODEL.md`;
- `IDENTITY_MODEL.md`;
- `USER_MODEL.md`;
- `ACCOUNT_MODEL.md`;
- `AUTHENTICATION_MODEL.md`;
- `SESSION_MODEL.md`;
- `PROJECT_MODEL.md`;
- `WORKSPACE_MODEL.md`;
- `RELATION_MODEL.md`;
- `Z_COCKPIT_IDENTITY_INTEGRATION.md`;
- `ADR-0002-identitaet-als-plattformkonzept.md`;
- `ADR-0003-architekturebenen-und-kernelgrenze.md`;
- `ADR-0004-core-referenzen-und-schema-bootstrap.md`.

## 34. Ergebnis

ProjectOS besitzt ein fachliches Autorisierungsmodell, das Rollen, direkte Berechtigungen, Verweigerungen, Whitelist/Blacklist, Ausnahmerechte, Stellvertretungen und Delegationen kontextbezogen zusammenführen kann.

Die effektive Berechtigung wird nachvollziehbar ermittelt, sicherheitsrelevante Mehrdeutigkeit führt nicht zur Freigabe und Z_Cockpit kann Entscheidungen transparent darstellen, ohne selbst zur zweiten Berechtigungsquelle zu werden.
