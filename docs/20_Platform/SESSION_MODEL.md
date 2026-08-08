# Sitzungsmodell

**Dokument-ID:** PLT-0009  
**Titel:** Fachliches Modell einer Nutzungssitzung  
**Version:** 0.1.0  
**Status:** Entwurf  
**Stabilitätsklasse:** B  
**Autoritätsebene:** Plattformmodell  
**Erstellt:** 8. August 2026  
**Zuletzt geändert:** 8. August 2026

---

## 1. Zweck

Dieses Dokument definiert die Sitzung als zeitlich begrenzten, bestätigten Nutzungskontext innerhalb von ProjectOS.

Eine Sitzung verbindet eine erfolgreich authentifizierte Akteursidentität mit einem konkreten Nutzungskontext. Sie ist weder das Konto selbst noch die Identität noch eine Rolle oder Berechtigung.

## 2. Architekturstellung

Das Sitzungsmodell gehört zur Plattformebene und baut insbesondere auf `IDENTITY_MODEL.md`, `ACCOUNT_MODEL.md` und `AUTHENTICATION_MODEL.md` auf.

Die Trennung lautet:

```text
Identität
    ↓
Konto
    ↓
Authentifizierung
    ↓
Sitzung
    ↓
Autorisierung
```

Die Sitzung trägt den zur Laufzeit relevanten Sicherheits- und Nutzungskontext, entscheidet jedoch nicht selbst über fachliche Berechtigungen.

## 3. Grundsatz

Eine Sitzung beantwortet die Frage:

> In welchem bestätigten Nutzungskontext handelt ein Akteur gerade?

Sie enthält dafür nur die erforderlichen Referenzen und Zustände.

Sie darf keine zweite Benutzer-, Rollen- oder Berechtigungsquelle bilden.

## 4. Sitzungsidentität

Jede Sitzung besitzt eine eigene stabile Sitzungs-ID für ihre Lebensdauer.

Die Sitzungs-ID:

- ist nicht identisch mit Konto-ID oder Akteursidentitäts-ID;
- darf nicht als dauerhafte Identität des Akteurs verwendet werden;
- wird nach Beendigung nicht für eine neue Sitzung wiederverwendet;
- muss im Audit eindeutig referenzierbar sein.

## 5. Sitzungskern

Eine Sitzung beschreibt mindestens:

- Sitzungs-ID;
- Akteursidentitätsreferenz;
- verwendete Konto-ID, sofern ein Konto beteiligt ist;
- Authentifizierungsergebnis und Authentifizierungsgrad;
- Beginn;
- letzte relevante Aktivität;
- Ablaufzeitpunkt oder Ablaufbedingung;
- Lebenszyklusstatus;
- Nutzungskontext;
- optionalen Projekt-, Workspace- oder Organisationskontext;
- optionalen Geräte- oder Clientkontext;
- Delegations- oder Stellvertretungskontext, sofern aktiv;
- relevante Sicherheits- und Auditbezüge.

Geheimnisse, Kennwörter oder vollständige Authentifizierungstokens gehören nicht in den fachlichen Sitzungskern.

## 6. Sitzung und Konto

Eine Sitzung kann aus einem Konto hervorgehen, ist aber davon getrennt.

Ein Konto kann gleichzeitig mehrere zulässige Sitzungen besitzen.

Das Sperren, Deaktivieren oder Stilllegen eines Kontos kann bestehende Sitzungen beeinflussen. Die Plattform muss dafür klare Widerrufs- und Neubewertungsregeln bereitstellen.

## 7. Sitzung und Identität

Die tatsächlich handelnde Akteursidentität bleibt in jeder Sitzung eindeutig erkennbar.

Mehrere Konten oder mehrere parallele Sitzungen derselben Identität erzeugen keine neuen fachlichen Personen.

## 8. Sitzung und Authentifizierung

Die Sitzung übernimmt aus der Authentifizierung mindestens:

- bestätigte Identität;
- verwendeten Authentifizierungsweg;
- Authentifizierungsgrad;
- Zeitpunkt der letzten erfolgreichen Authentifizierung;
- gegebenenfalls relevante Sicherheitsmerkmale.

Bei sicherheitskritischen Aktionen kann eine erneute oder stärkere Authentifizierung erforderlich werden.

## 9. Step-up-Authentifizierung

Eine bestehende Sitzung kann für bestimmte Aktionen einen höheren Authentifizierungsgrad benötigen.

Nach erfolgreichem Step-up kann der erhöhte Grad:

- für genau eine Aktion;
- für einen begrenzten Zeitraum;
- für einen begrenzten Gültigkeitsbereich

gültig sein.

Er darf nicht unbegrenzt auf alle zukünftigen Aktionen übertragen werden.

## 10. Sitzung und Autorisierung

Die Sitzung liefert Kontext an die Autorisierung, entscheidet aber nicht selbst über Berechtigungen.

Die Autorisierung kann unter anderem berücksichtigen:

- Akteursidentität;
- Konto- und Kontostatus;
- Authentifizierungsgrad;
- Projekt- oder Organisationskontext;
- Workspace-Kontext;
- aktive Delegation oder Stellvertretung;
- Sitzungsalter;
- Geräte- oder Clientkontext;
- Offline-Status;
- Sicherheitsereignisse und Richtlinien.

## 11. Projekt- und Workspace-Kontext

Eine Sitzung kann einen aktuellen Projekt- oder Workspace-Kontext referenzieren.

Dieser Kontext ist jedoch kein Eigentum der Sitzung.

Ein Wechsel des geöffneten Projekts oder Workspace kann innerhalb derselben Sitzung zulässig sein, sofern die Autorisierung dies erlaubt.

## 12. Delegation und Stellvertretung

Wenn ein Akteur innerhalb einer Sitzung delegiert oder stellvertretend handelt, müssen getrennt nachvollziehbar bleiben:

- tatsächlich ausführende Identität;
- vertretene oder delegierende Identität;
- Delegationsreferenz;
- Gültigkeitsbereich;
- Beginn und Ende;
- begründeter Zweck, soweit erforderlich.

Die Sitzung darf diese Identitäten nicht verschmelzen.

## 13. Lebenszyklus

Konzeptionell werden mindestens folgende Sitzungszustände unterschieden:

- vorbereitet;
- aktiv;
- eingeschränkt;
- inaktiv;
- abgelaufen;
- widerrufen;
- beendet.

Die genaue Zustandsmaschine wird über das Sitzungsschema festgelegt.

## 14. Inaktivität und Ablauf

Sitzungen können durch unterschiedliche Regeln beendet oder eingeschränkt werden, beispielsweise:

- maximale Sitzungsdauer;
- Inaktivitätsdauer;
- Ablauf des Authentifizierungsnachweises;
- Kontosperrung;
- Identitätssperrung;
- Widerruf einer Delegation;
- Sicherheitsereignis;
- Richtlinienänderung;
- explizite Abmeldung.

Ablaufbedingungen müssen deterministisch und auditierbar sein.

## 15. Widerruf

Sitzungen müssen kontrolliert widerrufbar sein.

Widerruf kann mindestens erfolgen durch:

- den Benutzer selbst;
- berechtigte Administratoren;
- Sicherheitsrichtlinien;
- Kontosperrung;
- Identitätssperrung;
- Änderung kritischer Authentifizierungsdaten;
- Verlust eines Geräts oder Clients;
- festgestellte Kompromittierung.

Ein Widerruf muss zeitnah wirksam werden, soweit der Betriebsmodus dies technisch zulässt.

## 16. Offline-First

ProjectOS muss Sitzungen für den vorgesehenen lokalen Offline-Betrieb unterstützen können.

Dabei gilt:

- nur lokal zulässige und ausreichend geprüfte Identitäten dürfen eine Offline-Sitzung erhalten;
- Offline-Sitzungen müssen als solche erkennbar sein;
- Gültigkeitsdauer und Berechtigungsumfang können enger begrenzt sein;
- lokal vorhandene Richtlinien und Autorisierungsinformationen müssen maßgeblich verwendet werden;
- nicht verfügbare externe Prüfungen dürfen nicht stillschweigend als erfolgreich angenommen werden;
- bei Wiederverbindung muss eine definierte Neubewertung möglich sein.

## 17. Geräte- und Clientkontext

Eine Sitzung kann an ein bestimmtes Gerät, einen Client oder eine technische Umgebung gebunden sein.

Diese Bindung kann sicherheitsrelevant sein, ersetzt aber nicht die Akteursidentität.

Geräteinformationen dürfen nur in dem Umfang gespeichert und angezeigt werden, der für Sicherheit, Betrieb und Audit erforderlich ist.

## 18. Parallele Sitzungen

Mehrere parallele Sitzungen derselben Identität können zulässig sein.

Richtlinien können Anzahl, Art oder Kontext paralleler Sitzungen begrenzen.

Das Z_Cockpit soll aktive parallele Sitzungen nachvollziehbar darstellen können, sofern der Benutzer dazu berechtigt ist.

## 19. Notfallsitzungen

Notfall- oder Wiederherstellungszugänge können besondere Sitzungen erzeugen.

Diese müssen mindestens:

- eindeutig als Notfallkontext markiert sein;
- stärker auditierbar sein;
- zeitlich eng begrenzt sein;
- nur den erforderlichen Umfang erhalten;
- nachträglich überprüfbar sein.

Eine Notfallsitzung erzeugt keine dauerhafte Sonderrolle.

## 20. Sicherheitsereignisse

Sicherheitsrelevante Sitzungsereignisse sollen auf das kanonische Sicherheitsereignismodell der Plattform abgebildet werden.

Dazu gehören insbesondere:

- Sitzung erzeugt;
- Sitzung beendet;
- Sitzung abgelaufen;
- Sitzung widerrufen;
- Step-up erforderlich;
- Step-up erfolgreich oder fehlgeschlagen;
- ungewöhnlicher Kontextwechsel;
- Notfallsitzung gestartet;
- sicherheitsbedingte Einschränkung.

Es darf keine neue parallele Sicherheitsereigniskette nur für Sitzungen entstehen.

## 21. Audit

Mindestens folgende Informationen müssen für relevante Sitzungsaktionen nachvollziehbar sein:

- Sitzungs-ID;
- handelnde Identität;
- Konto, sofern beteiligt;
- Authentifizierungsgrad;
- Beginn und Ende;
- Beendigungs- oder Widerrufsgrund;
- Projekt-/Workspace-Kontext, soweit relevant;
- aktive Delegation oder Stellvertretung;
- sicherheitsrelevante Kontextänderungen.

Geheimnisse und vollständige Tokens dürfen nicht im Audit erscheinen.

## 22. Z_Cockpit

Das Z_Cockpit darf berechtigungsabhängig unter anderem anzeigen:

- eigene aktive Sitzungen;
- Zeitpunkt und Status;
- verwendetes Konto;
- Authentifizierungsgrad;
- Offline-/Online-Status;
- Client- oder Gerätebezug in zulässigem Umfang;
- aktive Stellvertretung oder Delegation;
- Ablauf oder Einschränkungen;
- sicherheitsrelevante Warnungen.

Bei entsprechender Berechtigung können administrative Ansichten zusätzlich andere aktive Sitzungen und Widerrufsmöglichkeiten anbieten.

Das Z_Cockpit darf niemals vollständige Sitzungstokens, Kennwörter oder private Schlüssel darstellen.

## 23. Datenschutz

Sitzungen können sensible Nutzungs- und Sicherheitsmetadaten enthalten.

Daher müssen Anzeige, Speicherung, Aufbewahrung und Audit nach dem Prinzip der erforderlichen Datenminimierung erfolgen.

Die konkrete Aufbewahrungsdauer wird nicht in diesem Dokument festgelegt.

## 24. Validierung

Eine Sitzung ist mindestens darauf zu prüfen, dass:

1. eine eindeutige Sitzungs-ID vorhanden ist;
2. eine gültige Akteursidentität referenziert wird;
3. ein gegebenenfalls verwendetes Konto zur Identität passt;
4. ein gültiger Authentifizierungszustand vorliegt;
5. Lebenszyklusstatus und Zeitgrenzen konsistent sind;
6. Delegations- oder Stellvertretungsbezüge gültig sind;
7. abgelaufene oder widerrufene Sitzungen nicht regulär weiterverwendet werden;
8. Offline-Sitzungen eindeutig gekennzeichnet und regelkonform sind;
9. sicherheitsrelevante Zustandsänderungen auditierbar sind.

## 25. Invarianten

1. Sitzung, Konto und Identität sind getrennte Konzepte.
2. Eine Sitzung verleiht allein keine fachliche Berechtigung.
3. Eine Sitzung besitzt genau eine tatsächlich handelnde Akteursidentität.
4. Delegation und Stellvertretung verschmelzen keine Identitäten.
5. Abgelaufene oder widerrufene Sitzungen dürfen nicht als aktiv gelten.
6. Authentifizierungsgrad und Autorisierung bleiben getrennt.
7. Offline-Sitzungen müssen als solche erkennbar sein.
8. Geheimnisse werden nicht Bestandteil des fachlichen Sitzungsobjekts.
9. Sicherheitsereignisse verwenden das kanonische Sicherheitsereignismodell.
10. Sitzungs-UI ist keine Sicherheitsquelle der Wahrheit.

## 26. Abgrenzung

Dieses Dokument definiert ausdrücklich nicht:

- konkrete Cookie- oder Tokenformate;
- konkrete Kryptografie;
- konkrete Web- oder Desktop-Session-Technik;
- Berechtigungsauflösung;
- Rollenmodelle;
- Delegationsregeln im Detail;
- konkrete Authentifizierungsprotokolle;
- Aufbewahrungsfristen im Detail.

## 27. Abhängigkeiten

Dieses Dokument basiert auf:

- `IDENTITY_MODEL.md`;
- `USER_MODEL.md`;
- `ACCOUNT_MODEL.md`;
- `AUTHENTICATION_MODEL.md`;
- `WORKSPACE_MODEL.md`;
- `PROJECT_MODEL.md`;
- `Z_COCKPIT_IDENTITY_INTEGRATION.md`;
- `ADR-0002-identitaet-als-plattformkonzept.md`.

## 28. Ergebnis

Die Sitzung ist als eigenständiger, zeitlich begrenzter Nutzungskontext definiert. Sie verbindet erfolgreiche Authentifizierung mit dem zur Laufzeit erforderlichen Kontext, ohne Identität, Konto, Rolle oder Berechtigung zu duplizieren.
