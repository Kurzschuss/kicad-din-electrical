# Control Cabinet Basic - Schematic Design

## Sheets

### Power circuit

- Three phase supply L1/L2/L3
- F_CircuitBreaker_1P protection
- K_Contactor_3P switching element
- Motor/load output

### Control circuit 24V DC

Components:

- S_Stop_NC
- S_Start_NO
- K_AuxContact_NO
- K_Coil_24VDC

## Net naming

Power:

- L1
- L2
- L3
- PE

Control:

- +24V
- 0V
- K1_A1
- K1_A2

## Drawing rules

- Power circuit top-to-bottom
- Control circuit left-to-right
- IEC style references
- Separate power and control sections
