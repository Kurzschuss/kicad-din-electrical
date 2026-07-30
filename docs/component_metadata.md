# Component Metadata Standard

All DIN/IEC symbols should support the following fields:

| Field | Purpose |
|---|---|
| Manufacturer | Component manufacturer |
| Part_Number | Ordering reference |
| Description | Functional description |
| Datasheet | Technical documentation link |
| Mounting | DIN rail or panel mounting information |
| Footprint | KiCad footprint assignment |

## Example

```
Reference: K1
Value: CONTACTOR_3P
Manufacturer: <manufacturer>
Part_Number: <order code>
Description: 3 phase contactor with auxiliary contacts
Mounting: DIN rail
Footprint: DIN_RAIL_MODULE
```

## Goal

Enable BOM generation and cabinet documentation directly from KiCad.
