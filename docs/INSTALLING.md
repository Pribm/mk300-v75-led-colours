# Installation

This patch is **original MK300 V75 with the LED changes**. Install an earlier
official MK300 firmware first, then install this patched V75 package. This
downgrade-and-update sequence is the procedure reported by the successful tester;
no specific older version or compatibility with every older release has been
established.

Download the `.fwsc` attached to the release on the
[Releases page](https://github.com/Pribm/mk300-v75-led-colours/releases), or
generate it using the [build instructions](BUILDING.md). Its SHA-256 is:

```text
e3bcb3c7c3c2707db9636b34b873f46ae9cb82ee64b6adde981334f25c4d3122
```

## Update the pedal

1. Back up presets and other user data using the MK300 editor. Keep your known
   working firmware package available.
2. Obtain **M-UPGRADE**, an earlier official MK300 firmware, and its update
   instructions from the
   [manufacturer's download page](https://www.cuvave.com/download).
3. Connect the MK300 to the computer by USB and open M-UPGRADE, following the
   manufacturer's connection procedure.
4. **Downgrade to the earlier official firmware first.** Let the update and
   startup finish, including any initialization required by that version.
5. Load `MK300_V75_Combined_Click_Hold_Colours_EXPERIMENTAL.fwsc` and start the
   update. The `.app.bin` file is a build artifact, not the updater input.
6. Keep power and USB connected until the updater and pedal complete the update.
   Follow the manufacturer's instructions for any initialization required when
   moving from a different stock firmware version.
7. Load a preset and configure the Click/Hold Module CTL assignments normally.
   Test the combinations below.

This is an experimental patch with a successful user-reported physical test;
that report does not establish compatibility with every hardware revision.
NES sound is unavailable because the patch reuses its APU code space.

## Check the LEDs

Use a saturated preset colour and assign different modules to Click and Hold
on one footswitch. Toggle them through all four states:

| Click module | Hold module | Expected colour |
|---|---|---|
| ON | OFF | Original preset colour |
| OFF | OFF | OFF |
| ON | ON | Hue +90° |
| OFF | ON | Hue +180° |

Allow the normal fade to finish. The resulting colour should remain after
releasing the footswitch. Repeat on the other switches, then check a preset
change and an editor module-state change. Gray colours intentionally retain
their hue-neutral appearance in all lit states.

With only Click assigned to Module CTL, expect original colour/OFF. With only
Hold assigned, expect original colour/+180° for a nonempty selection. Empty or
disabled single assignments are OFF.

## Returning to a previous firmware

If the pedal still connects normally to M-UPGRADE, load your known working
`.fwsc` through the same update procedure. Follow its version-specific migration
instructions; a downgrade may require restoring backed-up user data. This
project does not supply a bootloader recovery tool.
