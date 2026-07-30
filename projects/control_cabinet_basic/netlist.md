# Control Cabinet Basic V1.0 Net Structure

## Power Circuit

NET_L1 -> X1 -> Q1 -> K1 -> M1
NET_L2 -> X1 -> Q1 -> K1 -> M1
NET_L3 -> X1 -> Q1 -> K1 -> M1
NET_PE -> PE_Rail -> Devices

## Control Circuit

NET_24V -> K2 A1
NET_0V -> K2 A2

SAFETY_OK -> K2 -> K1 Coil A1
COIL_RETURN -> K1 A2 -> 0V

## ERC Preparation

- All power nets named
- Safety signals separated
- PE connection defined
