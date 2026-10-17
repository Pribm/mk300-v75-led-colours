#!/usr/bin/env python3
"""Reproduce the tested combined Click/Hold firmware from original MK300 V75."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

from firmware import (APP_SIZE, RELEASE_APP_SHA256, RELEASE_PACKAGE_SHA256,
                      read_stock, repack, require, sha)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BASE = 0x18000120
NAME = "MK300_V75_Combined_Click_Hold_Colours_EXPERIMENTAL"


class Builder:
    def __init__(self, toolchain: Path, work: Path, original: bytes):
        self.tc, self.work, self.original = toolchain, work, original
        self.app = bytearray(original)
        self.used: set[int] = set()

    def run(self, name: str, *args) -> str:
        result = subprocess.run([str(self.tc / name), *map(str, args)], cwd=self.work,
                                capture_output=True, text=True)
        require(result.returncode == 0, f"{name} failed:\n{result.stdout}{result.stderr}")
        return result.stdout

    def compile(self, filename: str, output: str) -> Path:
        obj = self.work / (output + ".o")
        flags = ["-Oz"] if filename.endswith(".c") else []
        self.run("clang", "-target", "pi32v2", "-mcpu=r3", *flags,
                 "-c", SRC / filename, "-o", obj)
        return obj

    def extract(self, elf: Path, section: str, name: str) -> bytes:
        binary = self.work / (name + ".bin")
        self.run("objcopy", "-O", "binary", "-j", section, elf, binary)
        return binary.read_bytes()

    def assemble(self, filename: str, address: int, **symbols: int) -> bytes:
        name = Path(filename).stem
        obj = self.compile(filename, name)
        elf = self.work / (name + ".elf")
        args = ["-Ttext", hex(address), "-e", hex(address), "-o", elf, obj]
        for key, value in symbols.items():
            args.extend(["--defsym", f"{key}={hex(value)}"])
        self.run("ld", *args)
        return self.extract(elf, ".text", name)

    def put(self, address: int, data: bytes, size: int) -> None:
        require(len(data) == size, f"Wrong fragment size at {address:#x}: {len(data)} != {size}")
        off = address - BASE
        require(0 <= off < off + size <= APP_SIZE, "Patch outside app")
        positions = set(range(off, off + size))
        require(not self.used.intersection(positions), f"Overlapping patch at {address:#x}")
        self.used.update(positions)
        self.app[off:off + size] = data

    def stock_window(self, filename: str, start: int, end: int) -> None:
        (self.work / filename).write_bytes(self.original[start - BASE:end - BASE])

    def build(self) -> bytes:
        # Combined policy, register-safe far routes, and HSV hue transforms.
        objects = [self.compile("policy.S", "policy"),
                   self.compile("hue180_ordered.c", "hue180"),
                   self.compile("hue90.c", "hue90"),
                   self.compile("routes.S", "routes")]
        elf = self.work / "combined.elf"
        self.run("ld", "-T", SRC / "patch.ld", "--defsym",
                 "hue_opposite=hold_hue_opposite", "-o", elf, *objects)
        self.put(0x180348BA, self.extract(elf, ".routes", "routes"), 196)
        self.put(0x1804726E, self.extract(elf, ".extension", "extension"), 646)
        self.put(0x18047212, self.assemble("apu_stub.S", 0x18047212), 2)

        # Synchronize only the active preset, including external state changes.
        self.put(0x1803D78E, self.assemble("setter.S", 0x1803D78E,
                 module3_check=0x1803BDD6, setter_sync=0x18085530), 68)
        self.put(0x1803D778, self.assemble("post_update_wrapper.S", 0x1803D778,
                 original_prepare=0x1803BCB4, original_apply=0x1803CA68,
                 active_sync_guard=0x18085530), 22)
        self.put(0x18058480, self.assemble("post_update_direct.S", 0x18058480,
                 original_select=0x18034994, original_apply=0x1803CA68,
                 module_only_sync=0x180348C0), 44)
        normal = self.assemble("preset_normal_loop.S", 0x18055976,
                               module_sync=0x180348BA)
        require(len(normal) == 0x180, "Normal preset fragment size changed")
        for off, size in [(0, 4), (0x16, 4), (0x16E, 18)]:
            self.put(0x18055976 + off, normal[off:off + size], size)
        self.put(0x180557B4, self.assemble("preset_special_tail.S", 0x180557B4,
                 module_sync=0x180348BA), 32)

        # Preserve unchanged manufacturer instructions directly from local input.
        self.stock_window("validator-original-window.bin", 0x18042426, 0x18042564)
        obj = self.compile("validator-hook.S", "validator-hook")
        elf = self.work / "validator-hook.elf"
        self.run("ld", "-T", SRC / "validator-hook.ld", "-o", elf, obj)
        validator = self.extract(elf, ".text", "validator-hook")
        require(len(validator) == 318, "Validator fragment size changed")
        for address, size in [(0x18042426, 56), (0x18042492, 2), (0x180424A6, 2),
                              (0x18042528, 2), (0x1804252A, 4), (0x18042550, 20)]:
            off = address - 0x18042426
            self.put(address, validator[off:off + size], size)

        action = self.assemble("assignment_action.S", 0x180453BA, full_policy=0x180348BA)
        require(len(action) == 58, "Assignment action fragment size changed")
        self.put(0x180453BA, action[:14], 14)
        self.put(0x180453E4, action[0x2A:0x3A], 16)
        for stem, address, size in [("prepare", 0x180455B2, 14),
                                    ("clear", 0x180455D8, 36),
                                    ("loop", 0x1804561A, 4),
                                    ("set", 0x18045712, 26)]:
            self.put(address, self.assemble(f"assignment_mask_{stem}.S", address,
                     full_policy=0x180348BA), size)

        # Original V3 locking/fade corrections, with no startup or DMA changes.
        wrapper = self.assemble("critical-wrapper.S", 0x18085540,
                                policy_critical_exit=0x18034968)
        require(len(wrapper) <= 74, "Critical wrapper exceeds allocation")
        self.put(0x18085540, wrapper.ljust(74, b"\0"), 74)
        guard = self.assemble("active-guard.S", 0x18085530, module_only_sync=0x180348C0)
        require(len(guard) <= 16, "Active guard exceeds allocation")
        self.put(0x18085530, guard.ljust(16, b"\0"), 16)
        self.stock_window("original-timer.bin", 0x18085468, 0x1808552E)
        self.stock_window("original-flag.bin", 0x1808552E, 0x18085540)
        self.put(0x18085468, self.assemble("refresh-dirty.S", 0x18085468), 200)

        require(len(self.app) == APP_SIZE, "App size changed")
        require(sha(self.app) == RELEASE_APP_SHA256,
                "Build differs from the tested app. Check source and toolchain version; "
                "no installation image will be written.")
        return bytes(self.app)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--firmware", required=True, type=Path,
                        help="Original V75 MK300.fwsc (verified by SHA-256)")
    parser.add_argument("--toolchain", required=True, type=Path,
                        help="Jieli toolchain pi32v2/bin directory")
    parser.add_argument("--output", type=Path, default=ROOT / "build",
                        help="Output directory (default: build/)")
    args = parser.parse_args()
    image = args.firmware.read_bytes()
    original = read_stock(image)
    tc = args.toolchain.resolve()
    for name in ("clang", "ld", "objcopy"):
        require((tc / name).is_file(), f"Missing compiler tool: {tc / name}")
    output = args.output.resolve()
    targets = [output / (NAME + ".app.bin"), output / (NAME + ".fwsc"),
               output / "SHA256SUMS"]
    require(all(path.resolve() != args.firmware.resolve() for path in targets),
            "Output would overwrite input")
    # Compile in a disposable directory: no blobs are needed in the source tree.
    with tempfile.TemporaryDirectory(prefix="mk300-build-") as temporary:
        app = Builder(tc, Path(temporary), original).build()
    packed = repack(image, app)
    require(sha(packed) == RELEASE_PACKAGE_SHA256,
            "Package differs from the tested release; no installation image written")
    sums = (f"{sha(app)}  {targets[0].name}\n"
            f"{sha(packed)}  {targets[1].name}\n").encode()
    contents = [app, packed, sums]
    for path, data in zip(targets, contents):
        require(not path.exists() or path.read_bytes() == data,
                f"Refusing to overwrite different existing file: {path}")
    output.mkdir(parents=True, exist_ok=True)
    for path, data in zip(targets, contents):
        path.write_bytes(data)
    print("Build matches the physically tested firmware byte for byte.")
    print(sums.decode(), end="")
    print(f"Output: {output}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        sys.exit(f"Build failed: {exc}")
