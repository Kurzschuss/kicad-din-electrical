# DIN Rail Cabinet Layout

## Cabinet structure

```
Control cabinet
|
+-- X1 Incoming power terminals
|   +-- L1
|   +-- L2
|   +-- L3
|   +-- PE
|
+-- Q1 Motor protection
|
+-- K1 Contactor
|
+-- K_SafetyRelay
|
+-- X2 Control terminals
|   +-- +24V
|   +-- 0V
|
+-- X3 Field terminals
    +-- Start
    +-- Stop
    +-- Enable
```

## DIN rail grouping

- Power components are separated from control components.
- Safety components are grouped in the safety section.
- Terminal blocks are placed at the cabinet interfaces.

## Future extensions

- Manufacturer part numbers
- DIN rail footprints
- 3D enclosure layout
