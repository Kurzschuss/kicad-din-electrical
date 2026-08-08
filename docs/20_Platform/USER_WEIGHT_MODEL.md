# Benutzergewichtungsmodell

**Dokument-ID:** PLT-0016  
**Titel:** Fachliches Modell für Benutzer-, Kompetenz- und Vertrauensgewichtung  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert die kanonische Gewichtung menschlicher Benutzer in ProjectOS.

Gewichtung dient dazu, fachliche Beiträge, Reviews, Verbesserungsvorschläge, Bewertungen und Priorisierungen kontextabhängig einordnen zu können.

Gewichtung ist ausdrücklich keine Berechtigung und keine Autorisierungsentscheidung.

## 2. Grundsatz

ProjectOS verwendet keinen einzigen globalen Benutzerwert, der eine Person pauschal als wichtig, vertrauenswürdig oder kompetent klassifiziert.

Gewichtungen sind mehrdimensional, nachvollziehbar und an einen Gültigkeitsbereich gebunden.

Ein Benutzer kann beispielsweise im Bereich Elektrotechnik ein hohes Fachgewicht besitzen und in einer anderen Domäne kein besonderes Gewicht haben.

## 3. Trennung von Gewichtung und Autorisierung

Es gilt zwingend:

> Gewichtung ≠ Rolle ≠ Berechtigung ≠ Autorisierung.

Eine hohe Gewichtung darf niemals:

- ein fehlendes `ALLOW` erzeugen;
- ein `DENY` überschreiben;
- eine Blacklist umgehen;
- administrative Rechte erzeugen;
- MFA- oder Step-up-Anforderungen umgehen;
- das Vier-Augen-Prinzip ersetzen;
- eine Delegation vortäuschen;
- einen Benutzer zum Projektleiter machen;
- eine fachlich notwendige Freigabe ersetzen.

Die Autorisierungsplattform bleibt alleinige Instanz für effektive Rechte.

## 4. Gewichtungsdimensionen

Eine Gewichtung kann insbesondere folgende voneinander getrennte Dimensionen besitzen:

- Fachkompetenz;
- praktische Erfahrung;
- Domänenerfahrung;
- Projekterfahrung;
- Review-Erfahrung;
- Qualität bisheriger Beiträge;
- Zuverlässigkeit von Bewertungen;
- Aktualität der Erfahrung;
- formale Qualifikation, sofern fachlich erforderlich;
- ausdrücklich bestätigtes Vertrauensniveau für einen definierten Prozess.

Nicht jede Dimension muss in jedem Kontext verwendet werden.

## 5. Gültigkeitsbereich

Jede Gewichtung benötigt einen expliziten Gültigkeitsbereich.

Mögliche Bereiche sind insbesondere:

- Plattform;
- Organisation;
- Organisationseinheit;
- Projekt;
- Domäne;
- Objektklasse;
- Gerätetyp;
- Normenbereich;
- Improvement-Kategorie;
- Review-Typ;
- definierter Prozess.

Globale Gewichtungen sind nur zulässig, wenn ihre Bedeutung tatsächlich global ist.

## 6. Herkunft

Jeder Gewichtungsanteil muss eine nachvollziehbare Herkunft besitzen.

Mögliche Quellen sind:

- ausdrücklich bestätigte Qualifikation;
- Projekt- oder Domänenerfahrung;
- abgeschlossene Reviews;
- akzeptierte Verbesserungsvorschläge;
- nachträglich bestätigte fachliche Entscheidungen;
- organisatorisch bestätigte Einstufung;
- definierte Systemmetrik;
- manuelle Einstufung durch eine berechtigte Instanz.

Die Herkunft muss im Z_Cockpit erklärbar sein.

## 7. Keine versteckte Personenbewertung

ProjectOS darf Gewichtung nicht als undurchsichtigen Personen- oder Sozialscore verwenden.

Insbesondere unzulässig sind pauschale Aussagen wie:

- „Benutzer ist zu 83 % vertrauenswürdig“;
- „Benutzer ist besser als Benutzer B“ ohne fachlichen Kontext;
- automatische Abwertung aufgrund fachfremder Aktivität;
- geheime Gewichtungsfaktoren mit personeller Wirkung;
- Vermischung von Sicherheitsvertrauen und fachlicher Kompetenz.

Jede relevante Gewichtung muss fachlich begründbar sein.

## 8. Kompetenzgewicht

Kompetenzgewicht beschreibt fachliche Aussagekraft in einem definierten Bereich.

Beispiele:

- MCB;
- RCCB;
- Selektivität;
- Schutztechnik;
- KiCad-Symbolik;
- Dokumentation;
- Normenprüfung.

Ein Kompetenzgewicht darf aus mehreren Nachweisen zusammengesetzt werden, muss aber in seine Herkunft zerlegbar bleiben.

## 9. Erfahrungsgewicht

Erfahrungsgewicht beschreibt nachweisbare Erfahrung innerhalb eines Gültigkeitsbereichs.

Dabei können unter anderem berücksichtigt werden:

- Dauer relevanter Tätigkeit;
- Anzahl abgeschlossener fachlicher Vorgänge;
- Anzahl qualifizierter Reviews;
- Projekterfahrung;
- Aktualität der Erfahrung.

Reine Aktivitätsmenge darf nicht automatisch mit Qualität gleichgesetzt werden.

## 10. Beitragsqualitätsgewicht

Für Verbesserungs- und Wissenssysteme kann die Qualität bisheriger Beiträge berücksichtigt werden.

Mögliche Signale sind:

- Vorschlag akzeptiert;
- Vorschlag teilweise übernommen;
- Vorschlag als Dublette erkannt;
- Vorschlag fachlich widerlegt;
- Review bestätigt;
- Review nachträglich korrigiert;
- Änderung führte zu Regression;
- Änderung wurde langfristig bestätigt.

Negative Signale dürfen nicht ohne Kontext zu dauerhafter persönlicher Abwertung führen.

## 11. Vertrauensgewicht

Vertrauensgewicht ist von Kompetenzgewicht getrennt.

Es darf nur für ausdrücklich definierte Prozesse verwendet werden, beispielsweise für die Gewichtung von Improvement-Bewertungen oder Review-Empfehlungen.

Ein Vertrauensgewicht ist niemals Ersatz für eine Berechtigung, Sicherheitsrichtlinie oder Freigabe.

## 12. Zeitliche Wirkung

Gewichtungen können zeitabhängig sein.

Unterstützt werden müssen insbesondere:

- Beginn;
- optionales Ende;
- letzter Bewertungszeitpunkt;
- Verfalls- oder Abschwächungsregeln;
- Revalidierung;
- historische Werte.

Alte Erfahrung kann weiterhin relevant sein, darf aber nicht automatisch als aktuell behandelt werden.

## 13. Manuelle und berechnete Gewichtung

ProjectOS unterscheidet mindestens:

- manuell bestätigte Gewichtung;
- regelbasiert berechnete Gewichtung;
- aus Nachweisen abgeleitete Gewichtung;
- kombinierte Gewichtung.

Eine berechnete Gewichtung muss auf erklärbaren Eingangsdaten und einer versionierten Regel beruhen.

## 14. Gewichtungsregel

Eine Gewichtungsregel muss mindestens referenzieren können:

- Regel-ID;
- Version;
- Gültigkeitsbereich;
- verwendete Dimensionen;
- Eingangssignale;
- Gewichtungsfaktoren;
- Grenzwerte;
- zeitliche Regeln;
- verantwortliche Instanz;
- Aktivierungsstatus.

Änderungen an Regeln dürfen historische Ergebnisse nicht rückwirkend unsichtbar umdeuten.

## 15. Normalisierung

Falls numerische Werte verwendet werden, muss ihre Bedeutung je Dimension eindeutig definiert sein.

Ein Zahlenwert ohne Skala, Gültigkeitsbereich und Herkunft ist nicht ausreichend.

Unterschiedliche Gewichtungsmodelle dürfen nicht ungeprüft miteinander verrechnet werden.

## 16. Improvement-System

Das Improvement-System ist ein primärer Verbraucher der Benutzergewichtung.

Bei der Bewertung von Verbesserungsvorschlägen kann insbesondere berücksichtigt werden:

- fachlicher Gültigkeitsbereich des Vorschlags;
- Kompetenzgewicht der bewertenden Benutzer;
- Qualität früherer Beiträge;
- Review-Erfahrung;
- Interessenkonflikte;
- organisatorische oder projektbezogene Nähe;
- Anzahl unabhängiger Bewertungen.

Ein einzelner Benutzer mit hoher Gewichtung darf nicht automatisch allein über kritische Änderungen entscheiden.

## 17. Dublettenerkennung

Gewichtung kann bei der Behandlung erkannter Dubletten helfen.

Beispielsweise können fachlich hoch gewichtete Bestätigungen stärker in eine Priorisierung einfließen.

Die technische Dublettenerkennung selbst darf jedoch nicht allein vom Benutzergewicht abhängen.

## 18. Reviews und Freigaben

Gewichtung kann anzeigen, wie aussagekräftig eine Review-Empfehlung fachlich ist.

Sie ersetzt keine vorgeschriebene Reviewerrolle und keine formale Freigabe.

Wenn ein Prozess zwei unabhängige Freigaben verlangt, darf eine hohe Gewichtung einer Person nicht als zweite Freigabe zählen.

## 19. Interessenkonflikte

Gewichtungsberechnung und Verwendung müssen Interessenkonflikte berücksichtigen können.

Beispiele:

- Bewertung des eigenen Vorschlags;
- Bewertung eigener Änderungen;
- direkte organisatorische Abhängigkeit;
- delegierte Verantwortung;
- fachlich nicht unabhängige Review-Kette.

Ein Interessenkonflikt kann die verwendbare Gewichtung reduzieren oder eine unabhängige Bewertung erforderlich machen.

## 20. Z_Cockpit

Z_Cockpit soll Gewichtungen transparent darstellen können.

Mindestens vorgesehen sind:

- aktuelle Gewichtungsdimensionen;
- Gültigkeitsbereich;
- Herkunft;
- zugrunde liegende Nachweise;
- verwendete Regelversion;
- zeitliche Gültigkeit;
- letzte Neubewertung;
- historische Entwicklung;
- Hinweise auf Interessenkonflikte;
- Abgrenzung zu Rollen und effektiven Rechten.

Z_Cockpit ist nicht die Source of Truth für Gewichtungen.

## 21. Simulation

Z_Cockpit soll Gewichtungsänderungen simulieren können, ohne produktive Werte zu verändern.

Beispiele:

- Welche Auswirkung hätte eine neue Qualifikation?
- Wie verändert sich die Improvement-Priorisierung bei geänderter Kompetenzgewichtung?
- Was passiert, wenn ein Nachweis abläuft?
- Wie wirkt ein Interessenkonflikt?
- Welche Bewertungen gewinnen oder verlieren Gewicht?

Die Gewichtungssimulation ist von der Rechtesimulation zu unterscheiden.

Eine simulierte höhere Gewichtung darf niemals simulierte oder reale Berechtigungen erzeugen.

## 22. Audit

Auditpflichtig können insbesondere sein:

- manuelle Gewichtungsänderungen;
- Aktivierung oder Änderung einer Gewichtungsregel;
- Anerkennung oder Widerruf eines Nachweises;
- administrative Korrekturen;
- Änderungen mit erheblicher Wirkung auf Improvement- oder Review-Entscheidungen.

Das Audit muss tatsächlichen Akteur, Grund, Gültigkeitsbereich und Ergebnis nachvollziehbar halten.

## 23. Datenschutz

Gewichtungsdaten können personenbezogene Daten sein.

Es gelten Datenminimierung, Zweckbindung und Sichtbarkeitsbeschränkung.

Nicht jeder Benutzer darf sämtliche Bewertungsdetails anderer Benutzer einsehen.

Sensible oder nicht erforderliche personenbezogene Merkmale dürfen nicht als Gewichtungssignale verwendet werden.

## 24. Offline-First

Für Offline-Betrieb dürfen erforderliche Gewichtungsstände lokal verfügbar sein.

Dabei muss erkennbar bleiben:

- Datenstand;
- Regelversion;
- Zeitpunkt der letzten Synchronisation;
- eventuell fehlende Nachweise;
- Unsicherheit durch veraltete Daten.

Offline berechnete Änderungen dürfen beim Synchronisieren nicht stillschweigend konkurrierende Wahrheiten erzeugen.

## 25. Historie

Gewichtungen müssen historisch nachvollziehbar sein, wenn sie relevante Entscheidungen beeinflusst haben.

Eine spätere Neubewertung darf nicht so erscheinen, als hätte der neue Wert bereits bei einer früheren Entscheidung gegolten.

Entscheidungen sollen daher auf den damals verwendeten Gewichtungsstand oder dessen Referenz verweisen können.

## 26. Validierung

Eine Gewichtung ist mindestens darauf zu prüfen, dass:

1. Benutzer bzw. Akteursidentität eindeutig referenziert ist;
2. Dimension bekannt ist;
3. Gültigkeitsbereich eindeutig ist;
4. Herkunft nachvollziehbar ist;
5. Regelversion bekannt ist, sofern berechnet;
6. zeitliche Gültigkeit konsistent ist;
7. Wert zur definierten Skala passt;
8. Gewichtung keine Berechtigung kodiert;
9. Interessenkonflikte berücksichtigt werden können;
10. historische Referenzen erhalten bleiben.

## 27. Invarianten

1. Es gibt keinen pauschalen globalen Personenwert als allgemeine Wahrheit über einen Benutzer.
2. Gewichtung ist keine Berechtigung.
3. Gewichtung überschreibt niemals `DENY`.
4. Gewichtung ersetzt keine Rolle.
5. Gewichtung ersetzt keine Delegation.
6. Gewichtung ersetzt keine MFA- oder Step-up-Anforderung.
7. Gewichtung ersetzt keine vorgeschriebene unabhängige Freigabe.
8. Jede relevante Gewichtung besitzt einen erklärbaren Gültigkeitsbereich.
9. Jede relevante Gewichtung besitzt nachvollziehbare Herkunft.
10. Historische Entscheidungen behalten den damals verwendeten Gewichtungsstand.
11. Z_Cockpit ist nicht die Source of Truth.
12. Simulation verändert keine produktiven Gewichtungen.
13. Fachkompetenz und Sicherheitsvertrauen bleiben getrennte Dimensionen.
14. Aktivitätsmenge ist nicht automatisch Qualität.
15. Gewichtung darf nicht zu einem versteckten Sozialscore werden.

## 28. Abgrenzung

Dieses Dokument definiert nicht:

- konkrete numerische Skalen;
- endgültige Gewichtungsformeln;
- konkrete Machine-Learning-Verfahren;
- konkrete GUI-Layouts;
- konkrete Improvement-Prioritätsformeln;
- Rollen oder Berechtigungen;
- Authentifizierungsvertrauen;
- arbeitsrechtliche Leistungsbewertung.

## 29. Folgemodelle

Auf diesem Modell bauen insbesondere auf:

- `IMPROVEMENT_SYSTEM.md`;
- Review- und Freigabemodelle;
- Kompetenz- und Nachweismodelle;
- Z_Cockpit-Gewichtungsansichten;
- Z_Cockpit-Gewichtungssimulation;
- spätere Wissens- und Projektgedächtnismodelle.

## 30. Abhängigkeiten

Dieses Dokument basiert insbesondere auf:

- `PLATFORM_MODEL.md`;
- `IDENTITY_MODEL.md`;
- `USER_MODEL.md`;
- `ORGANIZATION_MODEL.md`;
- `PROJECT_MODEL.md`;
- `ROLE_MODEL.md`;
- `PERMISSION_MODEL.md`;
- `AUTHORIZATION_MODEL.md`;
- `DELEGATION_MODEL.md`;
- `AUDIT_MODEL.md`;
- `Z_COCKPIT_IDENTITY_INTEGRATION.md`;
- `Z_COCKPIT_AUTHORIZATION_SIMULATION.md`.

## 31. Ergebnis

ProjectOS besitzt ein eigenständiges, kontextabhängiges Benutzergewichtungsmodell. Fachkompetenz, Erfahrung, Beitragsqualität und prozessbezogenes Vertrauen können nachvollziehbar gewichtet werden, ohne Rollen, Berechtigungen oder Autorisierung zu vermischen. Die Gewichtung kann insbesondere Improvement, Review und Priorisierung unterstützen und im Z_Cockpit erklärt und simuliert werden.