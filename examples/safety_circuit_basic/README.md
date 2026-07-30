# Basic Safety Circuit Example

## Purpose

Example of a two-channel emergency stop safety circuit.

## Components

- S_EStop_2NC - emergency stop push button
- S_Reset_NO - reset push button
- K_SafetyRelay - safety relay
- K_Coil_24VDC - controlled contactor coil

## Function

```
+24V
 |
 S_EStop_2NC
 |
 K_SafetyRelay
 |
 Reset
 |
 Contactor enable
```

## Safety concept

- Two normally closed emergency stop channels
- Manual reset after emergency stop activation
- Separate safety and standard control circuits

## Reference standards

- EN ISO 13850
- EN ISO 13849
