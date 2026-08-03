EESchema Schematic File Version 4
LIBS:Z_RCD_Reference-cache
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
Sheet 1 1
Title "Z_RCD Referenzprojekt"
Date "2026-08-03"
Rev "1.0"
Comp "Kurzschuss/kicad-din-electrical"
Comment1 "KiCad ist der Standard; eigene Erweiterungen tragen Z_."
Comment2 "Herstellerneutrale Referenz: 2P, 40 A, 30 mA, Typ A"
Comment3 "ERC ist vor Freigabe lokal mit KiCad auszuführen."
Comment4 ""
$EndDescr
Text Notes 3600 1800 0    100  ~ 20
Z_RCD – herstellerneutrale 2-polige Referenz
Text Notes 3600 2050 0    60   ~ 0
230 V AC · 40 A · 30 mA · Typ A · Prüftaste
$Comp
L Z_RCD:RCD Q1
U 1 1 64D00001
P 5200 3600
F 0 "Q1" H 5200 4050 50  0000 C CNN
F 1 "RCD 2P 40A 30mA Typ A" H 5200 3950 50 0000 C CNN
F 2 "Z_DIN_Module_36mm:Z_DIN_Module_36mm" H 5200 3500 50 0001 C CNN
F 3 "" H 5200 3500 50 0001 C CNN
	1    5200 3600
	1    0    0    -1
$EndComp
Text Label 4400 3400 2    50   ~ 0
L_IN
Text Label 6000 3400 0    50   ~ 0
L_OUT
Text Label 4400 3800 2    50   ~ 0
N_IN
Text Label 6000 3800 0    50   ~ 0
N_OUT
Wire Wire Line
	4400 3400 4900 3400
Wire Wire Line
	5500 3400 6000 3400
Wire Wire Line
	4400 3800 4900 3800
Wire Wire Line
	5500 3800 6000 3800
NoConn ~ 4400 3400
NoConn ~ 6000 3400
NoConn ~ 4400 3800
NoConn ~ 6000 3800
Text Notes 3800 4700 0    60   ~ 0
Die vier Anschlüsse sind absichtlich offen markiert. Dadurch bleibt das Beispiel elektrisch neutral und ERC-reproduzierbar.
$EndSCHEMATC
