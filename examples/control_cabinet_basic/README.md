# Basic Control Cabinet Example

This example demonstrates the intended use of the DIN electrical library.

## Components

- X_Terminal_PE_N_L - supply terminals
- F_CircuitBreaker_1P - protection device
- K_Contactor_3P - motor switching contactor

## Intended circuit

```
L/N/PE supply
      |
      +-- F_CircuitBreaker_1P
              |
              +-- K_Contactor_3P
                      |
                      +-- Load output
```

## Purpose

This example is used to validate symbol naming, documentation fields and library consistency.
