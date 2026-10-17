# Building

## Requirements

- Linux x86-64 and Python 3.10 or newer; no Python packages are required.
- JieLi Linux toolchain **20260730.1**, using its `pi32v2/bin` tools.
  The vendor provides a [toolchain download](https://pkgman.jieliapp.com/s/linux-toolchain)
  and [Linux documentation](https://doc.zh-jieli.com/Tools/zh-cn/dev_tools/toolchains/linux_lib.html).
  Extract the entire archive so its `common/` and `pi32v2/` directories stay
  together. This project accepts its path directly; no system installation is needed.
- The original **MK300 V75 `MK300.fwsc`**, obtained separately. This build does
  not accept other firmware versions or an already patched package.

The tested toolchain archive SHA-256 is:

```text
a1545cddbc451a06bac43eb5cd96d831470c42a97c5c0b1f98879a20fc7647bd
```

The vendor download endpoint can change versions. The required archive directory
is `jieli-linux-toolchains-20260730.1`; its compiler reports Clang 4.0.1.

The original firmware must be 1,363,828 bytes with SHA-256:

```text
16c9fd41b85c3b55db2b69a7f48191bf4f9c015276fd6a0455f17fdf34307592
```

## Command

Run from the repository directory, replacing the two example paths:

```sh
python3 tools/build.py \
  --firmware /path/to/original/MK300.fwsc \
  --toolchain /path/to/jieli-linux-toolchains-20260730.1/pi32v2/bin
```

Outputs go into `build/`, which Git ignores:

```text
MK300_V75_Combined_Click_Hold_Colours_EXPERIMENTAL.app.bin
MK300_V75_Combined_Click_Hold_Colours_EXPERIMENTAL.fwsc
SHA256SUMS
```

Use `--output /path/to/directory` to choose another output directory. The input
firmware is never modified. Different existing output files are not overwritten.
Temporary objects and extracted instruction windows are removed after compilation.

## Verify the result

```sh
cd build
sha256sum -c SHA256SUMS
```

| Output | Bytes | SHA-256 |
|---|---:|---|
| `.app.bin` | 1,307,704 | `a069b8c3fec60121f5fb4f6aaec61dc16e8ddd800d3bd6df586bc5d47665dc23` |
| `.fwsc` | 1,363,828 | `e3bcb3c7c3c2707db9636b34b873f46ae9cb82ee64b6adde981334f25c4d3122` |

These identify the firmware reported working on hardware. The clean source
distribution has reproduced both files byte for byte. The script also validates
container CRCs, fixed sizes, patch boundaries and extraction of the rebuilt app.

The build deliberately stops if changed source or a different compiler produces
another image. Those checks identify the tested release; they are not a substitute
for validating a newly modified firmware.

## Implementation details

The active preset begins at `0x1844A454`. Each footswitch record is at
`preset + 0x14A + 6 * slot`, for slots 0–3. Byte fields +0/+1 are Click/Hold
action IDs; Module CTL is 0. Fields +2/+4 are separate little-endian 16-bit masks.
Bits 0–10 select enable bytes `preset + 0x2B` through `preset + 0x35`.
Bit 11 (`0x0800`) disables a mask; bits 12–15 are ignored. Any nonzero selected
enable byte counts as ON.

The policy occupies 646 bytes starting at `0x1804726E`, inside the reclaimed
NES APU handler. Its outer entries preserve r4–r12 and the return address.
The synchronization hooks, critical sections and dirty/fade backend are included
in the source build; no earlier experimental package is required.

Hue +90° uses integer arithmetic and rounds half components upward. Hue +180°
is exact at 8-bit RGB precision. Both preserve HSV saturation/value, before the
existing LED hardware quantization and fade.
