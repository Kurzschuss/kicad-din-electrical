# Start/Stop Contactor Control Example

## Purpose

Example of a typical industrial 24 V DC contactor control circuit.

## Components

- S_Stop_NC - Stop push button (normally closed)
- S_Start_NO - Start push button (normally open)
- K_Coil_24VDC - Contactor coil
- K_AuxContact_NO - Contactor self-holding contact

## Control logic

```
+24V
 |
 +-- S_Stop_NC
       |
       +--+-- S_Start_NO ----+
          |                  |
          +-- K_AuxContact_NO+
                             |
                         K_Coil_24VDC
                             |
                            0V
```

## Function

Pressing START energizes the contactor coil. The auxiliary NO contact closes and maintains the circuit after START is released. STOP interrupts the control voltage.

## Future symbols

- S_Stop_NC
- S_Start_NO
