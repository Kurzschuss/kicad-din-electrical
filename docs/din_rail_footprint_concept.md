# DIN Rail Footprint Concept

## Purpose

Define a common approach for DIN rail mounted components in KiCad.

## Mounting classes

- DIN_Module_18mm
- DIN_Module_36mm
- DIN_Terminal_Block
- DIN_Power_Supply
- DIN_Contactor

## Metadata fields

Required:

- Mounting
- Width_mm
- DIN_Rail_Type
- Manufacturer
- Part_Number
- Footprint

## Example

```
Component: K1
Mounting: DIN rail
Width_mm: 45
DIN_Rail_Type: TS35
Footprint: DIN_Contactor_45mm
```

## Goal

Enable consistent cabinet layout planning and future 3D integration.
