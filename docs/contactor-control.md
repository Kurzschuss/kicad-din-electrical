# Contactor Control Circuit Concept

## Purpose

Defines the planned representation of contactors with power and control sections.

## Contactors

A contactor consists of:

- Power contacts
  - L1/T1
  - L2/T2
  - L3/T3

- Coil
  - A1
  - A2

## Planned symbol extension

The `K_Contactor_3P` symbol will be extended with a coil representation or a separate coil symbol.

## Typical control voltages

Supported examples:

- 24 V DC control
- 24 V AC control
- 230 V AC control

## Naming proposal

- `K_Contactor_3P` - power section
- `K_Coil_24VDC` - control coil
- `K_AuxContact_NO` - auxiliary normally open contact
- `K_AuxContact_NC` - auxiliary normally closed contact
