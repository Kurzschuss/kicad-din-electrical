# Z_MAIN_SWITCH – Hauptschalter / Lasttrennschalter

## Zweck

`Z_MAIN_SWITCH` stellt herstellerneutrale Hauptschalter beziehungsweise Lasttrennschalter für Installations- und Verteilungspläne bereit. Die Symbole bilden die elektrische Schaltfunktion ab und nicht die äußere Bauform eines bestimmten Herstellers.

## Kanonische Symbole

- `Z_MAIN_SWITCH:MAIN_SWITCH` – 2-polig / L+N
- `Z_MAIN_SWITCH:MAIN_SWITCH_4P` – 4-polig / 3P+N

Beide Symbole verwenden getrennte Schaltkontakte je Pol und eine gestrichelte mechanische Kopplung. Beim 2P-Symbol ist der zweite Pol als Neutralleiter gekennzeichnet; beim 4P-Symbol ist der vierte Pol als Neutralleiter gekennzeichnet.

Die erste freigegebene Paketbasis beschränkt sich bewusst auf 2P und 4P/3P+N, weil diese Varianten in den vorhandenen Installations- und Verteilungsmodellen unmittelbar benötigt werden. Eine reine 3P-Variante wird erst ergänzt, wenn dafür ein konkreter Projektbedarf oder ein eigenes Gerätepaket vorliegt; die abstrakte Altlogik in `distributions/din_switchgear.py` ist dafür allein kein Freigabegrund.

## Geräteserien

Die herstellerneutralen Planungsserien liegen unter:

- `data/device_series/generic/main-switch-2p-template-series.yaml`
- `data/device_series/generic/main-switch-4p-template-series.yaml`

Je Polzahl werden die Nennstromstufen 16 A, 25 A, 40 A und 63 A bereitgestellt. Alle Einträge sind `source_status: template` und müssen vor einer realen Ausführung durch konkrete Produktdaten ersetzt oder verifiziert werden.

## Technischer Referenzrahmen

Als Plausibilitätsrahmen für die neutrale Geräteklasse dienen aktuelle Herstellerangaben zu modularen Schaltern/Trennern:

- ABB SD200: 1- bis 4-polige Ausführungen, 16 bis 63 A, Trennereigenschaften nach DIN EN 60947-3.
- Siemens SENTRON 5TL1: beispielsweise 5TL1240-0 als 2-poliger 40-A-Schalter/Trenner.

Diese Herstellerangaben werden **nicht** als Produktdatensatz in die generischen Gerätevarianten kopiert. Sie belegen nur, dass Polzahlen und Strombereich der neutralen Planungsbasis marktüblich und technisch plausibel sind.

## Footprint- und 3D-Policy

`Z_Footprint_Policy` ist `optional`. Die Modulwerte in den generischen Geräteserien sind Planungswerte für den Verteilungsentwurf und keine Zusicherung einer konkreten Herstellerbreite. Reale Footprints, Gehäuseabmessungen und 3D-Modelle werden erst mit belegten Produktdaten ergänzt.

## Qualitätsstatus

Das Paket darf erst `Geprüft` erhalten, wenn Symbolquelle, Geräteserien, generierte Varianten, Vorschauen, Referenzdokumentation und Regressionstests gemeinsam durch die Projektvalidatoren und die vollständige CI geprüft wurden.
