# Delegationsmodell

**Dokument-ID:** PLT-0013  
**Titel:** Fachliches Modell für Delegation, Stellvertretung und Nachfolge  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert, wie ProjectOS Befugnisse und Verantwortlichkeiten kontrolliert von einer Akteursidentität auf eine andere übertragen oder vertretungsweise nutzbar machen kann.

Delegation, Stellvertretung und Nachfolge sind verwandt, aber nicht identisch.

## 2. Architekturstellung

Das Delegationsmodell gehört zur Plattformebene und baut insbesondere auf `IDENTITY_MODEL.md`, `USER_MODEL.md`, `ROLE_MODEL.md`, `PERMISSION_MODEL.md`, `AUTHORIZATION_MODEL.md`, `SESSION_MODEL.md` und `RELATION_MODEL.md` auf.

Die Autorisierungsplattform entscheidet letztlich, ob eine delegierte oder stellvertretende Handlung zulässig ist.

## 3. Grundsatz

Delegation überträgt keine Identität.

Für jede delegierte Handlung müssen mindestens getrennt erkennbar bleiben:

- delegierende bzw. vertretene Identität;
- ausführende Identität;
- delegierte Befugnis oder Verantwortung;
- Gültigkeitsbereich;
- zeitliche Gültigkeit;
- konkrete Sitzung bzw. Nutzungskontext;
- maßgebliche Delegationsreferenz.

## 4. Delegationsarten

Die Plattform muss mindestens unterscheiden können zwischen:

- Berechtigungsdelegation;
- Verantwortungsdelegation;
- Stellvertretung;
- temporärer Projektvertretung;
- technischer Delegation an Dienst oder Automatisierung;
- geplanter Nachfolge bzw. Verantwortungsübernahme.

Die konkrete Wirkung jeder Art wird ausdrücklich definiert und nicht aus dem Namen abgeleitet.

## 5. Delegationsidentität

Jede Delegation besitzt eine stabile Delegations-ID.

Die Delegations-ID:

- ist unabhängig von beteiligten Konten;
- bleibt für den historischen Vorgang erhalten;
- wird nach Beendigung nicht für eine neue Delegation wiederverwendet;
- ist in Autorisierung, Sitzung, Audit und Z_Cockpit referenzierbar.

## 6. Delegationskern

Eine Delegation beschreibt mindestens:

- Delegations-ID;
- Delegationsart;
- delegierende bzw. originär verantwortliche Identität;
- ausführende bzw. empfangende Identität;
- Gültigkeitsbereich;
- Zielreferenz, soweit erforderlich;
- delegierte Rollen, Berechtigungen oder Verantwortungen;
- explizite Ausschlüsse;
- Beginn;
- optionales Ende oder Ablaufbedingung;
- Aktivierungsstatus;
- Weiterdelegierbarkeit;
- Begründung;
- ausstellende oder freigebende Identität bzw. Instanz;
- erforderliche Freigaben;
- Historien- und Auditbezüge.

## 7. Umfang

Eine Delegation muss ihren Umfang ausdrücklich festlegen.

Der Umfang kann referenzieren:

- einzelne Berechtigungen;
- definierte Berechtigungsgruppen;
- eine Rolle oder einen begrenzten Teil einer Rolle;
- konkrete Verantwortungen;
- einzelne Objekte oder Objektgruppen;
- Projekt, Organisation oder Domäne;
- definierte Workflows oder Operationen.

Eine Formulierung wie „alle Rechte“ ist nur zulässig, wenn dieser Umfang formal definiert, zulässig und prüfbar ist.

## 8. Delegierbarkeit

Eine Berechtigung kann gemäß `PERMISSION_MODEL.md` delegierbar, eingeschränkt delegierbar, nicht delegierbar oder nur mit zusätzlicher Freigabe delegierbar sein.

Eine Delegation darf keine nicht delegierbare Berechtigung wirksam machen.

Die delegierende Identität kann niemals mehr übertragen, als sie nach den geltenden Regeln tatsächlich übertragen darf.

## 9. Berechtigungsdelegation

Bei einer Berechtigungsdelegation wird eine ausdrücklich definierte Menge von Berechtigungen für einen begrenzten Kontext an eine andere Identität nutzbar gemacht.

Dabei bleibt die Herkunft der Berechtigung als `Delegation` erkennbar.

Eine delegierte Berechtigung wird nicht zu einer originären direkten Berechtigungszuweisung des Empfängers.

## 10. Verantwortungsdelegation

Eine Verantwortungsdelegation kann fachliche Zuständigkeit für einen begrenzten Zeitraum oder Kontext übertragen.

Verantwortung und Berechtigung bleiben getrennt.

Eine Verantwortungsdelegation erzeugt nur die Berechtigungen, die durch Rollen-, Berechtigungs- und Autorisierungsregeln ausdrücklich daran gekoppelt sind.

## 11. Stellvertretung

Stellvertretung ist eine kontrollierte Form der Delegation für die Wahrnehmung einer bestehenden Verantwortung.

Sie muss mindestens definieren:

- vertretene Identität;
- Stellvertreter;
- vertretene Rolle oder Verantwortung;
- Gültigkeitsbereich;
- Beginn und Ende;
- übertragene Befugnisse;
- Ausschlüsse;
- Aktivierungsbedingung;
- Begründung;
- Freigabe.

Eine Stellvertretung kopiert nicht pauschal sämtliche Rechte des Vertretenen.

## 12. Aktivierung einer Stellvertretung

Eine Stellvertretung kann vorbereitet sein, ohne bereits wirksam zu sein.

Konzeptionelle Aktivierungsarten sind:

- sofort mit Freigabe;
- ab festem Zeitpunkt;
- manuell durch berechtigte Instanz;
- durch Abwesenheitsstatus;
- durch definierte Notfall- oder Eskalationsbedingung;
- nach bestätigter Übergabe.

Automatische Aktivierungsbedingungen müssen deterministisch und auditierbar sein.

## 13. Vertrauensperson

Eine Vertrauensperson ist keine automatische Delegation.

Sie kann jedoch in ausdrücklich definierten Prozessen eine Rolle spielen, beispielsweise:

- Wiederherstellungsfreigabe;
- Eskalation;
- Mitfreigabe eines Notfallvorgangs;
- Bestätigung einer Nachfolge oder Stellvertretung.

Daraus entstehen nur die dafür ausdrücklich vorgesehenen Berechtigungen.

## 14. Nachfolge

Eine Nachfolge beschreibt eine geplante zukünftige Verantwortungsübernahme.

Vor Aktivierung erzeugt eine Nachfolgerbeziehung grundsätzlich keine produktiven Rechte.

Eine Nachfolge muss mindestens definieren:

- bisher verantwortliche Identität;
- Nachfolger;
- zu übernehmende Verantwortung oder Rolle;
- Aktivierungsbedingung;
- Zeitpunkt bzw. Wirksamkeitsbeginn;
- Gültigkeitsbereich;
- notwendige Freigaben;
- Umgang mit bestehenden Delegationen;
- Auditbezug.

## 15. Nachfolgeaktivierung

Bei Aktivierung einer Nachfolge müssen die daraus entstehenden Änderungen explizit durchgeführt und nachvollziehbar gemacht werden.

Es ist zu unterscheiden zwischen:

- Übernahme einer Verantwortung;
- Zuweisung einer Rolle;
- Aktivierung einzelner Berechtigungen;
- Beendigung bisheriger Zuweisungen;
- Fortführung oder Widerruf bestehender Delegationen.

Nachfolge ist keine Identitätsersetzung.

## 16. Technische Delegation

Menschliche oder technische Akteure können definierte Aufgaben an Dienste oder Automatisierungen delegieren, sofern die betreffenden Berechtigungen technisch delegierbar sind.

Technische Delegation muss mindestens besitzen:

- eindeutige technische Empfängeridentität;
- klaren Zweck;
- begrenzten Umfang;
- begrenzten Gültigkeitsbereich;
- kontrollierte Laufzeit;
- auditierbare Nutzung;
- Widerrufsmöglichkeit.

Unspezifische Sammelidentitäten sind zu vermeiden.

## 17. Weiterdelegation

Weiterdelegation ist standardmäßig nicht implizit erlaubt.

Eine Delegation muss ausdrücklich festlegen, ob und in welchem Umfang Weiterdelegation zulässig ist.

Wenn sie zulässig ist, müssen mindestens gelten:

- Umfang darf nicht erweitert werden;
- Gültigkeitsbereich darf nicht erweitert werden;
- Ablauf darf nicht über den Ablauf der übergeordneten Delegation hinausreichen;
- nicht weiterdelegierbare Rechte bleiben ausgeschlossen;
- Delegationskette muss vollständig nachvollziehbar sein.

## 18. Delegationskette

Bei mehrstufiger Delegation muss die vollständige Herkunft rekonstruierbar sein.

Beispiel:

```text
A
 ↓ delegiert an
B
 ↓ delegiert zulässig weiter an
C
```

Für eine Handlung von C müssen A, B, C, beide Delegationen und der zulässige Umfang nachvollziehbar bleiben.

Zyklen in Delegationsketten sind unzulässig.

## 19. Lebenszyklus

Eine Delegation besitzt mindestens konzeptionell folgende Zustände:

- Entwurf;
- wartet auf Freigabe;
- vorbereitet;
- aktiv;
- pausiert;
- widerrufen;
- abgelaufen;
- beendet;
- archiviert.

Nur eine gültige aktive Delegation kann neue Autorisierungswirkungen erzeugen.

## 20. Widerruf

Delegationen müssen widerrufbar sein.

Widerruf kann abhängig von Richtlinie ausgelöst werden durch:

- delegierende Identität;
- empfangende Identität;
- Projektleitung;
- zuständige administrative oder Sicherheitsrolle;
- Ablauf oder Statusänderung;
- Sicherheitsereignis;
- Beendigung einer zugrunde liegenden Rolle oder Verantwortung.

Widerruf muss für neue Autorisierungsentscheidungen wirksam werden.

## 21. Auswirkungen auf Sitzungen

Wird eine Delegation widerrufen, pausiert oder beendet, müssen betroffene aktive Sitzungen neu bewertet werden können.

Eine Sitzung darf keine delegierten Rechte dauerhaft konservieren, nachdem die zugrunde liegende Delegation unwirksam geworden ist.

Das `SESSION_MODEL.md` hält hierfür die Delegationsreferenz im Nutzungskontext.

## 22. Ablauf

Zeitlich begrenzte Delegationen enden automatisch nach ihrer definierten Gültigkeit.

Ablauf darf nicht stillschweigend durch eine noch aktive Sitzung umgangen werden.

Vor Ablauf kann das Z_Cockpit – abhängig von Richtlinie – Warnungen oder Verlängerungsanforderungen anzeigen.

## 23. Verlängerung

Eine Verlängerung ist eine sicherheitsrelevante Änderung und keine bloße UI-Aktion.

Sie muss:

- erneut validiert werden;
- autorisiert werden;
- gegebenenfalls erneut freigegeben werden;
- neue zeitliche Grenzen setzen;
- auditierbar sein.

## 24. Änderung des Umfangs

Eine Erweiterung einer Delegation wird wie eine neue Rechtegewährung behandelt.

Besonders kritisch sind:

- zusätzliche Berechtigungen;
- größerer Gültigkeitsbereich;
- längere Laufzeit;
- erlaubte Weiterdelegation;
- Aufnahme kritischer oder administrativer Rechte.

Solche Änderungen können erhöhte Authentifizierung oder Vier-Augen-Freigabe verlangen.

## 25. `DENY` und Blacklist

Delegation darf ausdrückliche Verweigerungen nicht unsichtbar umgehen.

Eine delegierte positive Berechtigungsquelle bleibt den `DENY`-, Blacklist- und Richtlinienregeln der Autorisierung unterworfen.

Nur ein ausdrücklich zulässiges Ausnahmerecht kann einen dafür definierten Konflikt behandeln.

## 26. Ausnahmerechte

Ausnahmerechte und Delegation bleiben getrennte Konzepte.

Eine Ausnahme darf nicht als Delegation getarnt werden und eine Delegation darf kein verborgenes Ausnahmerecht erzeugen.

Wenn ein Ausnahmerecht delegierbar sein soll, muss dies ausdrücklich und besonders restriktiv geregelt werden.

## 27. Vier-Augen-Prinzip

Eine Delegation darf das Vier-Augen-Prinzip nicht dadurch umgehen, dass eine Rolle oder Freigabeberechtigung an eine Identität übertragen wird, die dadurch ihre eigene Handlung freigeben könnte.

Die tatsächlichen Akteursidentitäten des konkreten Vorgangs müssen auf Unabhängigkeit geprüft werden.

Zwei Konten derselben Identität bleiben eine Identität.

## 28. Trennung von Aufgaben

Unvereinbare Rollen und Berechtigungen bleiben auch unter Delegation unvereinbar, sofern die jeweilige Richtlinie keine ausdrücklich geprüfte Ausnahme vorsieht.

Die Delegationsvalidierung muss solche Konflikte vor Aktivierung erkennen können.

## 29. Offline-First

Delegationen können offline ausgewertet werden, wenn der notwendige bestätigte Delegations- und Autorisierungsstand lokal verfügbar ist.

Es muss sichtbar sein:

- auf welchem Snapshot die Delegation beruht;
- ob sie zum lokalen Zeitpunkt aktiv ist;
- ob ein Widerruf möglicherweise noch nicht synchronisiert wurde;
- ob die betreffenden Berechtigungen offline zulässig sind.

Kritische Delegationen können Online-Bestätigung verlangen.

## 30. Z_Cockpit

`Z_Cockpit` soll Delegationen und Stellvertretungen transparent darstellen und bei entsprechender Autorisierung verwalten können.

Mindestens sichtbar sein sollen:

- Delegationsart;
- Delegations-ID;
- originär verantwortliche bzw. delegierende Identität;
- ausführende Identität;
- delegierte Rolle, Berechtigung oder Verantwortung;
- Ausschlüsse;
- Gültigkeitsbereich;
- Beginn und Ende;
- Status;
- Weiterdelegierbarkeit;
- Freigaben;
- Begründung;
- relevante Auditinformationen.

Aktive Stellvertretung muss im Nutzungskontext besonders sichtbar sein.

## 31. Rechtesimulation

Delegationen müssen in der Z_Cockpit-Rechtesimulation berücksichtigt werden.

Vor Aktivierung oder Änderung soll insbesondere prüfbar sein:

- welche zusätzlichen effektiven Rechte entstehen;
- welche Rechte ausdrücklich ausgeschlossen bleiben;
- welche nicht delegierbaren Rechte nicht übertragen werden;
- welche Konflikte mit `DENY`, Blacklist oder Unvereinbarkeiten entstehen;
- welche Auswirkungen Ablauf oder Widerruf haben;
- ob Weiterdelegation neue Risiken erzeugt;
- ob Vier-Augen-Regeln verletzt würden.

Die Integrationsregeln stehen in `Z_COCKPIT_AUTHORIZATION_SIMULATION.md`.

## 32. Delegations-Read-Model

Für Cockpit und Analyse darf ein nicht-autoritatives Read-Model aufgebaut werden.

Es kann insbesondere darstellen:

- aktive Delegationen einer Identität;
- von einer Identität ausgestellte Delegationen;
- Delegationsketten;
- bald ablaufende Delegationen;
- pausierte oder widerrufene Delegationen;
- Rechteherkunft aus Delegation;
- Konflikte und Warnungen.

Produktive Autorisierungsentscheidungen dürfen nicht allein aus diesem Read-Model erfolgen.

## 33. Audit

Mindestens folgende Vorgänge müssen auditierbar sein:

- Delegation angelegt;
- Delegation freigegeben oder abgelehnt;
- Delegation aktiviert;
- Delegationsumfang geändert;
- Delegation verlängert;
- Delegation pausiert;
- Delegation widerrufen;
- Delegation abgelaufen;
- Weiterdelegation angelegt;
- Stellvertretung aktiviert oder beendet;
- Nachfolge aktiviert;
- delegierte sicherheitskritische Handlung ausgeführt.

Bei einer delegierten Handlung müssen ausführende und delegierende bzw. vertretene Identität nachvollziehbar sein.

## 34. Validierung

Eine Delegation ist mindestens darauf zu prüfen, dass:

1. Delegations-ID eindeutig ist;
2. delegierende und empfangende Identität gültig und verschieden sind, sofern der spezielle Delegationstyp nichts anderes verlangt;
3. Gültigkeitsbereich zulässig ist;
4. Beginn und Ende konsistent sind;
5. alle referenzierten Rollen und Berechtigungen existieren;
6. nur delegierbare Befugnisse enthalten sind;
7. die delegierende Identität den delegierbaren Umfang tatsächlich besitzt;
8. Ausschlüsse widerspruchsfrei sind;
9. Weiterdelegation nicht mehr erlaubt als die übergeordnete Delegation;
10. keine Delegationszyklen entstehen;
11. Unvereinbarkeiten und Vier-Augen-Regeln berücksichtigt sind;
12. notwendige Freigaben vorhanden sind;
13. sicherheitsrelevante Änderungen auditierbar sind.

## 35. Invarianten

1. Delegation verschmilzt keine Identitäten.
2. Delegation erzeugt keine originäre Berechtigungszuweisung beim Empfänger.
3. Nicht delegierbare Rechte bleiben nicht delegierbar.
4. Delegation kann Umfang, Bereich und Laufzeit der zulässigen Quelle nicht erweitern.
5. Stellvertretung ist keine pauschale Kopie aller Rechte.
6. Vertrauensperson besitzt ohne zusätzliche Regel keine Delegationswirkung.
7. Nachfolge erzeugt vor Aktivierung keine produktiven Rechte.
8. Weiterdelegation ist nur ausdrücklich zulässig.
9. Delegationsketten bleiben vollständig nachvollziehbar und zyklusfrei.
10. Widerruf und Ablauf müssen neue Autorisierungsentscheidungen beeinflussen.
11. Delegation umgeht kein `DENY` oder Blacklist stillschweigend.
12. Vier-Augen-Prinzip bleibt auf tatsächliche unabhängige Identitäten bezogen.
13. Z_Cockpit ist nicht die Source of Truth der Delegation.
14. Rechtesimulation hat keine produktive Wirkung.

## 36. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- konkrete technische Delegationstokens;
- konkrete Workflow-Engine;
- konkrete Datenbanktabellen;
- vollständige Organisationshierarchien;
- konkrete UI-Layouts;
- technische Synchronisationsprotokolle;
- vollständige Auditimplementierung.

## 37. Folgemodelle

Auf diesem Modell bauen insbesondere auf:

- `ORGANIZATION_MODEL.md`;
- `AUDIT_MODEL.md`;
- spätere Identitäts- und Autorisierungsdienste;
- Delegations- und Stellvertretungs-Workflows;
- Z_Cockpit-Read-Models und Rechtesimulation.

## 38. Abhängigkeiten

Dieses Dokument basiert insbesondere auf:

- `PLATFORM_MODEL.md`;
- `IDENTITY_MODEL.md`;
- `USER_MODEL.md`;
- `PROJECT_MODEL.md`;
- `AUTHORIZATION_MODEL.md`;
- `ROLE_MODEL.md`;
- `PERMISSION_MODEL.md`;
- `SESSION_MODEL.md`;
- `RELATION_MODEL.md`;
- `Z_COCKPIT_IDENTITY_INTEGRATION.md`;
- `Z_COCKPIT_AUTHORIZATION_SIMULATION.md`.

## 39. Ergebnis

ProjectOS besitzt ein eigenständiges Delegationsmodell für Berechtigungs- und Verantwortungsdelegation, Stellvertretung, technische Delegation und Nachfolge.

Umfang, Gültigkeitsbereich, Laufzeit, Weiterdelegierbarkeit, Ausschlüsse, Widerruf und Audit bleiben explizit. Delegierte Handlungen bleiben auf die tatsächlich handelnde sowie die delegierende oder vertretene Identität zurückführbar und können vor ihrer Aktivierung im Z_Cockpit sicher simuliert werden.
