# MK300 — Click + Hold LED colours

See which effects are on at a glance, even when one footswitch controls two
different groups of effects.

This patch adds clearer footswitch LED feedback to the **M-VAVE MK300**. It is
based on the original **V75 firmware**, with changes to how the footswitch
lights show the state of your effects. It has been tested successfully by a
user on a physical MK300 and remains an experimental community modification.

## What it does

The MK300 lets you use a short press (**Click**) and a long press (**Hold**) to
control different effects on the same footswitch. With this patch, the light
shows whether the effects assigned to Click, Hold, or both are switched on.

You keep choosing your preset colour as usual. The patch automatically derives
two additional colours from it:

| Effects controlled by Click | Effects controlled by Hold | Footswitch light |
|---|---|---|
| ON | OFF | Your original preset colour |
| OFF | OFF | Light off |
| ON | ON | A second colour: both groups are active |
| OFF | ON | An opposite colour: only the Hold group is active |

For example, with **red** as your preset colour, Click-only is red, both groups
on is yellow-green, and Hold-only is cyan. If a group contains several effects,
it counts as ON when **at least one** of them is enabled.

The light shows the effects' actual state. It stays that way after you release
the footswitch and updates when you change presets or switch effects through
the editor or MIDI. The normal fade between colours still applies.

## How to use it

Choose **Module CTL** for the Click and Hold actions on a footswitch, then
select the effects each action should control. Use different effects for the
two actions if you want to see all four combinations in the table above.

The patch also supports simpler setups:

- **Only Click controls effects:** the light uses your preset colour when any
  selected effect is on, and turns off when they are all off.
- **Only Hold controls effects:** the light uses your preset colour when any
  selected effect is on, and the opposite colour when they are all off.
- **No effects selected:** that assignment counts as off. An empty single
  assignment leaves the light off.
- **Other footswitch actions:** their existing light behaviour is retained.

This works independently on all four footswitches. If Click and Hold select
exactly the same effects, their states match, so you will see only the both-on
colour or the light off. Gray and white preset colours remain neutral, so
their lit states will not be distinguishable by colour.

## How to install

Download the **`.fwsc` firmware file** attached to the version you want on the
[Releases page](https://github.com/Pribm/mk300-v75-led-colours/releases).
The source ZIP and TAR archives are for developers.

**Downgrade first, then install the patch.** The installation sequence confirmed
by the tester is an earlier official MK300 firmware followed by this patched
V75 firmware. The patch is **V75 with the LED changes**.

1. **Back up your presets and other user data** in the MK300 editor. Keep a copy
   of your known working firmware.
2. Get **M-UPGRADE** and an earlier official MK300 firmware from the
   [manufacturer's download page](https://www.cuvave.com/download).
3. Connect the pedal by USB and use M-UPGRADE to **install the earlier official
   firmware first**. Let that update finish and follow any initialization
   instructions supplied with it.
4. Use M-UPGRADE again to install
   **`MK300_V75_Combined_Click_Hold_Colours_EXPERIMENTAL.fwsc`**.
5. Keep power and USB connected until the update and startup finish. Load a
   preset, set up your Click/Hold assignments, and try the combinations above.

The downgrade recommendation comes from the successful installation procedure;
a specific older version and compatibility with every older release have not
been established. Follow the manufacturer's instructions for the version you use.

This repository also contains source code and build tools. To build the patch
yourself, follow [Building](docs/BUILDING.md). The updater takes the **`.fwsc` file**.
See [Installation](docs/INSTALLING.md) for file verification and checks after
updating.

## Things to know

**NES game sound is disabled** because the patch reuses that part of the
firmware for its LED logic. The normal guitar-effects audio code is unchanged.

The SAVE screen, colour wheel and screen colour previews still behave as they
did before. The additional colours are currently shown on the footswitch LEDs.

## How it was developed — technical details

The reverse engineering and decompilation were carried out using **Codex + REA**,
with **Ghidra and the JieLi instruction tools** used to inspect and verify the
firmware. REA's native analyzer could not process this PI32V2 application, so
the instruction-level analysis used Ghidra with a corrected processor definition,
checked against the vendor disassembler. The code here is the reconstructed
patch implementation, not the manufacturer's complete original source project.

### Finding the right state to display

The investigation traced the footswitch action dispatcher, the module-state
setter and the existing LED update path. Click and Hold have separate module
selections in each preset. Each selection is a little-endian 16-bit mask:
bits 0–10 select the eleven module enable bytes, bit 11 disables the selection,
and the remaining bits do not select modules. Any nonzero selected enable byte
counts as ON.

This led to the final rule: calculate `click_active` and `hold_active`
independently from the current preset and module states. Earlier Click-priority
and last-action approaches could not show both assignments at once. Reading both
states gives the four combinations above and keeps the indication meaningful
after release, preset changes and external updates.

### Producing and publishing the colours

For dual Module CTL assignments, the original preset colour is A. When both
assignments are active, colour B is
an HSV hue rotation of **+90°**. When only Hold is active, colour C is **+180°**.
Both rotations preserve saturation and value; zero-chroma colours remain gray.
The +90° conversion uses integer arithmetic with half-component rounding upward.
The +180° conversion is exact at 8-bit RGB precision.

The patch reuses the existing LED group/pixel writers and fade pipeline.
Synchronization hooks recalculate the target colours after relevant module,
preset and assignment updates. Critical sections and dirty-flag handling keep
those targets available to the refresh callback. Empty or disabled selections
are inactive; a single empty selection publishes black instead of retaining a
stale colour or suggesting that an unassigned group is active.

### Keeping the working firmware architecture

The combined policy and hue helpers occupy **646 bytes** inside reclaimed NES APU handler
space. The original APU entry returns immediately, which disables NES sound.
The application keeps its original size and layout, without new startup DMA
operations or bootloader changes.

An earlier prototype exposed an **r12 preservation defect**: inserted far-call
routes overwrote a register that the original dispatcher still needed. The
instruction regression reproduced an invalid counter access after the callback
returned. Saving and restoring r12 corrected that defect, and the resulting
baseline was tested successfully on hardware. The combined-colour implementation
retains that correction and preserves r4–r12 plus the return address at both
policy entry points.

### How the result was checked

Host validation covered **5,400 policy cases**, **26,043 hue-conversion cases**,
dispatcher continuation, editor updates, register preservation, target-buffer
publication and fading. Negative regressions rejected the earlier r12-corrupting
image and distinguished the final combined-state behaviour from Click-priority
and last-action behaviour.

The firmware package was independently extracted and checked against the built
application. The combined candidate was then reported working on a physical
MK300. That hardware report is separate from the host checks; the tests do not
claim exhaustive hardware, timing or audio validation.

The clean source build reproduces that tested application and `.fwsc` **byte for
byte** from original V75. It checks the input and output SHA-256 hashes before
writing an installation image. Small unchanged instruction windows are read
from the local original firmware during the build.

| Source | Purpose |
|---|---|
| `src/policy.S`, `src/routes.S` | Combined state policy and register-safe entry routes |
| `src/hue90.c`, `src/hue180_ordered.c` | Hue rotations |
| Other `src/*.S` files | State synchronization, assignment updates, locking and fade |
| `src/*.ld` | Fixed executable placement |
| `tools/build.py` | Compile and apply the patch to original V75 |
| `tools/firmware.py` | Validate and repack the V75 container |
