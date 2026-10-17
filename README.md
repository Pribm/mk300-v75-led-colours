# MK300 V75 — Click + Hold LED colours

A firmware patch for the M-VAVE MK300 that shows the current state of both
Module CTL assignments on each footswitch. The combined firmware has been
reported working on a physical MK300. It remains an experimental modification.

This repository contains the patch's C and reconstructed PI32V2 assembly,
plus tools to reproduce the tested firmware from an original V75 package.
It is not the manufacturer's complete firmware source. Firmware images and
the compiler are supplied locally by the person building it.

## What changes

When **both Click and Hold are Module CTL**, each assignment is evaluated
independently. “ON” means at least one module selected by that assignment is
enabled.

| Click modules | Hold modules | Footswitch LED |
|---|---|---|
| Any ON | All OFF | A: original preset colour |
| All OFF | All OFF | OFF |
| Any ON | Any ON | B: original hue +90° |
| All OFF | Any ON | C: original hue +180° |

Saturation and brightness are preserved by the hue conversion. Grays remain
gray; black remains black. For example, a red preset colour produces
yellow-green at +90° and cyan at +180°. The existing LED fade still applies.

The colour follows actual module states, including state synchronization after
footswitch actions, preset changes and external editor/MIDI updates. It persists
after release; neither the last action nor the physical held state determines it.

Single assignments behave as follows:

- **Click only:** original colour when any selected module is ON; otherwise OFF.
- **Hold only:** original colour when any selected module is ON; hue +180° when
  every selected module is OFF.
- **Neither action is Module CTL:** existing LED behaviour.
- **Empty or disabled assignment:** contributes no active modules. A single
  empty/disabled assignment is OFF, including Hold-only. In a dual assignment,
  the other side still determines its part of the table.

Identical Click and Hold selections naturally produce only the both-ON and
both-OFF states. The same rules apply to all four footswitches.

## Scope

The patch includes the register-preservation correction and synchronization/fade
fixes used by the working firmware. Startup, bootloader, USB update handling and
normal audio/DSP code retain their original bytes. SAVE-screen indicators,
the colour wheel and LCD previews are unchanged.

**NES sound is disabled:** its APU handler space holds the additional LED code.
The application and firmware package keep their original sizes.

## Build and install

1. Follow [Building](docs/BUILDING.md) to generate the exact tested `.fwsc` from
   your original V75 package.
2. Follow [Installation](docs/INSTALLING.md) to install it using M-UPGRADE.

The build script checks the complete input and output hashes. It writes files
only and never connects to or flashes a pedal.

## Source layout

| Location | Purpose |
|---|---|
| `src/policy.S`, `src/routes.S` | Combined state policy and register-safe entry routes |
| `src/hue90.c`, `src/hue180_ordered.c` | HSV hue rotations |
| Other `src/*.S` files | Module/preset synchronization, assignment updates, locking and fade |
| `src/*.ld` | Fixed executable placement |
| `tools/build.py` | Compile and apply the patch to original V75 |
| `tools/firmware.py` | Read, validate and repack the V75 container |

All modified application bytes are reproduced by the build. Small unchanged
instruction windows used by the assembly are extracted from the local original
firmware at build time.
