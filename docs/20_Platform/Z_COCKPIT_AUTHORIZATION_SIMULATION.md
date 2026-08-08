# Z_Cockpit – Rechtesimulation

**Dokument-ID:** INT-0002  
**Titel:** Simulation und Auswirkungsanalyse von Rollen und Berechtigungen im Z_Cockpit  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Integrationsvertrag  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert eine sichere Rechtesimulation für `Z_Cockpit`.

Die Simulation ermöglicht, geplante Änderungen an Rollen, Berechtigungen, Delegationen, Stellvertretungen, Whitelist-/Blacklist-Regeln und Ausnahmerechten vor ihrer Aktivierung auf ihre Auswirkungen zu prüfen.

Sie beantwortet beispielsweise:

> Welche effektiven Rechte hätte Benutzer X in Projekt Y, wenn Rolle Z zugewiesen oder entfernt würde?

> Welche Rechte würden durch eine Delegation, ein `DENY`, eine Ausnahme oder einen Ablauf tatsächlich hinzugefügt oder entzogen?

## 2. Grundsatz

Die Rechtesimulation ist eine **Was-wäre-wenn-Auswertung**.

Sie darf niemals:

- echte Rollen oder Berechtigungen verändern;
- produktive Autorisierungsdaten überschreiben;
- eine echte Autorisierungsentscheidung ersetzen;
- aus einem simulierten `ALLOW` eine reale Berechtigung ableiten;
- simulierte Änderungen stillschweigend aktivieren.

Simulation und produktive Autorisierung müssen technisch und fachlich unterscheidbar bleiben.

## 3. Simulationsszenario

Ein Simulationsszenario basiert auf einem bekannten Ausgangsstand und einem isolierten Satz hypothetischer Änderungen.

Ein Szenario beschreibt mindestens:

- Szenario-ID;
- Ausgangsstand bzw. Referenz auf den Autorisierungsstand;
- betroffene Akteursidentität oder Akteursgruppe;
- Projekt-, Organisations-, Workspace-, Domänen- oder Objektkontext;
- simulierte Änderungen;
- Zeitpunkt bzw. angenommener Bewertungszeitpunkt;
- optionalen Sitzungs- und Authentifizierungskontext;
- Ersteller des Szenarios;
- Erstellungszeitpunkt.

## 4. Simulierbare Änderungen

Mindestens folgende Änderungen sollen simuliert werden können:

- Rolle zuweisen;
- Rolle entziehen;
- Rollenversion ändern;
- direkte Berechtigung `ALLOW` hinzufügen oder entfernen;
- direkte Berechtigung `DENY` hinzufügen oder entfernen;
- Delegation hinzufügen, ändern, aktivieren, pausieren oder widerrufen;
- Stellvertretung aktivieren oder beenden;
- Gültigkeitsbereich ändern;
- Beginn oder Ablauf ändern;
- Whitelist-Regel hinzufügen oder entfernen;
- Blacklist-Regel hinzufügen oder entfernen;
- Ausnahmerecht hinzufügen, ändern oder auslaufen lassen;
- Projekt-, Organisations- oder Verantwortungsbeziehung ändern;
- Authentifizierungsgrad oder Offline-Kontext als Prüfannahme verändern.

## 5. Vorher-Nachher-Vergleich

Die wichtigste Darstellung ist der Vergleich:

```text
Ist-Zustand
    ↓
hypothetische Änderung
    ↓
simulierter Zustand
    ↓
Differenz
```

Die Differenz soll mindestens unterscheiden:

- neu erlaubte Handlungen;
- neu verweigerte Handlungen;
- unveränderte Handlungen;
- Rechte, die nur durch Ausnahme wirksam würden;
- Rechte, die durch Delegation entstehen oder entfallen;
- Rechte mit geändertem Gültigkeitsbereich;
- Rechte mit geändertem Ablauf;
- Rechte mit geändertem Authentifizierungsbedarf;
- Konflikte oder `INDETERMINATE`-Ergebnisse.

## 6. Herkunft einer simulierten Berechtigung

Für jedes simulierte effektive Recht soll die Herkunft erklärbar sein.

Mindestens sind darstellbar:

- Rolle;
- direkte Zuweisung;
- Delegation;
- Stellvertretung;
- Organisations- oder Projektbeziehung;
- Whitelist-Bedingung;
- Blacklist- oder `DENY`-Quelle;
- Ausnahmerecht;
- Risikoklasse;
- Gültigkeitsbereich;
- Beginn und Ablauf;
- Authentifizierungsanforderung;
- maßgebliche Regelreferenzen.

## 7. Simulation für den eigenen Benutzer

Ein Benutzer soll – soweit autorisiert – insbesondere seine **eigenen** effektiven Rechte simulieren können.

Beispiele:

- „Was dürfte ich als Projektleiter?“
- „Was verliere ich, wenn diese Rolle entfernt wird?“
- „Was ändert sich während einer Stellvertretung?“
- „Welche Aktionen wären nach Ablauf dieser Delegation nicht mehr möglich?“
- „Welche Berechtigung fehlt mir für diese Operation?“

Die Simulation eigener Rechte darf keine Möglichkeit bieten, sich Rechte selbst zu erteilen.

## 8. Simulation anderer Benutzer

Die Simulation für andere Akteure ist eine privilegierte Analysefunktion.

Sie muss gesondert autorisiert werden und darf nur die Informationen offenlegen, die der simulierende Benutzer sehen darf.

Personenbezogene, sicherheitskritische oder geheime Informationen dürfen durch die Simulation nicht umgangen werden.

## 9. Rollen- und Berechtigungsänderungen vor Freigabe

Besonders wertvoll ist die Simulation vor einer tatsächlichen Änderung.

Vor dem Anwenden einer kritischen Änderung soll das Z_Cockpit eine Auswirkungsanalyse anbieten können, beispielsweise:

- wie viele Benutzer gewinnen ein neues kritisches Recht;
- wie viele Benutzer verlieren Zugriff;
- welche Projekte sind betroffen;
- welche `DENY`-Regeln werden relevant;
- welche Delegationen werden unwirksam;
- welche Vier-Augen- oder Unvereinbarkeitsregeln werden verletzt;
- welche Konten oder Sitzungen müssten neu bewertet werden.

## 10. Risikobewertung

Die Simulation soll Auswirkungen nach Risikoklasse gruppieren können.

Besonders hervorzuheben sind:

- neu entstehende administrative Rechte;
- neu entstehende Sicherheitsrechte;
- Freigabe- und Genehmigungsrechte;
- Rechte zur Rollen- oder Berechtigungsverwaltung;
- Rechte zum Ändern von Audit-, Sicherheits- oder Identitätsdaten;
- neu mögliche Notfall- oder Ausnahmewege;
- Verlust kritischer Betriebsrechte.

## 11. Delegation und Stellvertretung

Bei Delegation und Stellvertretung muss die Simulation getrennt zeigen:

- originäre Rechte der handelnden Identität;
- zusätzlich delegierte Rechte;
- explizit ausgeschlossene Rechte;
- nicht delegierbare Rechte;
- vertretene bzw. delegierende Identität;
- zeitliche Gültigkeit;
- Gültigkeitsbereich;
- Auswirkungen eines Widerrufs oder Ablaufs.

Die Simulation darf keine Identitäten verschmelzen.

## 12. Zeitreise-Simulation

Ein Szenario darf einen zukünftigen oder vergangenen Bewertungszeitpunkt verwenden, sofern die erforderlichen versionierten Daten vorhanden sind.

Damit sollen beispielsweise folgende Fragen beantwortbar sein:

- Welche Rechte gelten nach Ablauf einer Delegation?
- Was passiert nach Beginn einer geplanten Stellvertretung?
- Welche Rechte hätte ein Nachfolger nach einer definierten Aktivierung?
- Welche Rolle oder Berechtigung war zu einem früheren Auditzeitpunkt wirksam?

Historische Simulation muss klar von einer Rekonstruktion tatsächlich getroffener Autorisierungsentscheidungen unterschieden werden.

## 13. Offline-Simulation

Die Simulation kann offline arbeiten, wenn der notwendige Autorisierungsstand lokal vollständig verfügbar ist.

Dabei muss sichtbar sein:

- auf welchem Snapshot die Simulation basiert;
- wann dieser zuletzt bestätigt wurde;
- welche Regeln möglicherweise veraltet sind;
- welche externen Informationen fehlen;
- ob das Ergebnis dadurch eingeschränkt oder `INDETERMINATE` ist.

## 14. Simulationsengine

Das Z_Cockpit implementiert keine eigene vereinfachte Berechtigungslogik.

Die Simulation verwendet dieselben fachlichen Regeln wie die Autorisierungsplattform, jedoch gegen einen isolierten hypothetischen Zustand.

Konzeptionell gilt:

```text
Autorisierungsregeln
        ↓
Simulationseingang + hypothetische Änderungen
        ↓
isolierte Simulationsauswertung
        ↓
Simulationsresultat / Differenz
        ↓
Z_Cockpit-Read-Model
```

## 15. Simulationsresultat

Ein Simulationsresultat beschreibt mindestens:

- Szenario-ID;
- Ausgangsstand;
- simulierten Stand;
- betroffene Identität(en);
- Kontext;
- hinzugewonnene effektive Rechte;
- verlorene effektive Rechte;
- veränderte Einschränkungen;
- Konflikte;
- `STEP_UP_REQUIRED`-Fälle;
- `CONTEXT_REQUIRED`-Fälle;
- `INDETERMINATE`-Fälle;
- Regelherkunft;
- Warnungen;
- Auswertungszeitpunkt.

## 16. Keine Produktionswirkung

Ein Simulationsresultat besitzt keinerlei produktive Autorisierungswirkung.

Es darf nicht als Token, Berechtigungsnachweis oder Ersatz für eine reale Autorisierungsentscheidung verwendet werden.

Eine produktive Änderung erfordert immer einen getrennten, autorisierten Plattformbefehl.

## 17. Übernahme eines Szenarios

Ein geprüftes Szenario kann als Vorlage für eine echte Änderungsanforderung dienen.

Die Übernahme muss jedoch:

1. ausdrücklich ausgelöst werden;
2. die aktuellen produktiven Daten erneut laden;
3. auf zwischenzeitliche Änderungen prüfen;
4. vollständig validieren;
5. erneut autorisieren;
6. gegebenenfalls Freigaben oder Vier-Augen-Prinzip prüfen;
7. die produktive Änderung separat auditieren.

Ein Simulationserfolg ist keine automatische Freigabe.

## 18. Z_Cockpit-Darstellung

Das Cockpit soll mindestens folgende Sichten anbieten können:

- Ist-Rechte;
- simulierte Rechte;
- Differenzansicht;
- Herkunft je Recht;
- Risikofilter;
- Projekt-/Organisations-/Domänenfilter;
- Zeit- und Ablaufansicht;
- Delegations- und Stellvertretungsansicht;
- Konflikt- und Warnungsansicht.

Eine simulierte Information muss visuell eindeutig als **Simulation** gekennzeichnet sein.

## 19. Tests

Mindestens zu testen sind:

- Simulation verändert keine produktiven Daten;
- identischer Ausgangsstand ohne Änderungen erzeugt keine Differenz;
- Rollenänderungen erzeugen erwartete Rechtedifferenzen;
- `DENY` und Blacklist wirken in der Simulation korrekt;
- Delegation überschreitet keine Delegierbarkeitsgrenzen;
- abgelaufene Regeln sind unwirksam;
- Zeitreise berücksichtigt Start und Ablauf korrekt;
- Offline-Simulation kennzeichnet veraltete oder fehlende Daten;
- simuliertes `ALLOW` kann nicht als reale Autorisierung verwendet werden;
- Z_Cockpit zeigt Simulation eindeutig als nicht produktiv.

## 20. Audit

Reine Simulationen sind keine produktiven Berechtigungsänderungen.

Trotzdem können Simulationen sicherheitsrelevant sein, insbesondere bei Analyse anderer Benutzer oder privilegierter Rollen.

Daher soll auditierbar sein können:

- wer eine privilegierte Simulation ausgeführt hat;
- welcher Kontext analysiert wurde;
- welcher Ausgangsstand verwendet wurde;
- ob das Szenario später als Änderungsanforderung übernommen wurde.

Das Audit darf keine Geheimnisse enthalten.

## 21. Invarianten

1. Simulation verändert keine produktiven Autorisierungsdaten.
2. Simuliertes `ALLOW` ist kein reales `ALLOW`.
3. Die Simulation verwendet dieselben fachlichen Regeln wie die Autorisierung.
4. Hypothetische Daten bleiben isoliert.
5. Jede Differenz ist auf konkrete Regelquellen zurückführbar.
6. Delegation und Stellvertretung verschmelzen keine Identitäten.
7. Veraltete oder unvollständige Daten werden sichtbar gemacht.
8. Kritische Änderungen werden nach Risiko hervorhebbar.
9. Z_Cockpit ist Bedien- und Darstellungsschicht, nicht Simulations-Source-of-Truth.
10. Übernahme in Produktion verlangt eine vollständige neue Autorisierung und Validierung.

## 22. Abhängigkeiten

Dieses Dokument basiert insbesondere auf:

- `Z_COCKPIT_IDENTITY_INTEGRATION.md`;
- `AUTHORIZATION_MODEL.md`;
- `ROLE_MODEL.md`;
- `PERMISSION_MODEL.md`;
- `SESSION_MODEL.md`;
- `IDENTITY_MODEL.md`;
- `PROJECT_MODEL.md`.

Es wird später durch `DELEGATION_MODEL.md`, `ORGANIZATION_MODEL.md` und `AUDIT_MODEL.md` ergänzt.

## 23. Ergebnis

`Z_Cockpit` erhält eine ausdrücklich vorgesehene Rechtesimulation. Benutzer und Administratoren können damit – innerhalb ihrer Sicht- und Analyseberechtigungen – die Auswirkungen geplanter Rollen-, Berechtigungs-, Delegations- und Richtlinienänderungen vor der Aktivierung prüfen.

Die Simulation bleibt vollständig von produktiver Autorisierung getrennt und liefert eine nachvollziehbare Vorher-Nachher-Analyse inklusive Herkunft, Risiko, Gültigkeitsbereich, Ablauf und Konflikten.
