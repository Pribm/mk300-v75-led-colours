"""Fixed-layout MK300 V75 package reader/writer. No device access."""
from __future__ import annotations

import binascii
import hashlib
import struct

STOCK_PACKAGE_SHA256 = "16c9fd41b85c3b55db2b69a7f48191bf4f9c015276fd6a0455f17fdf34307592"
STOCK_APP_SHA256 = "b921f503b8725afb56999e4f7296c6af1013349b65c906fe5e7d130bebb0649b"
RELEASE_PACKAGE_SHA256 = "e3bcb3c7c3c2707db9636b34b873f46ae9cb82ee64b6adde981334f25c4d3122"
RELEASE_APP_SHA256 = "a069b8c3fec60121f5fb4f6aaec61dc16e8ddd800d3bd6df586bc5d47665dc23"
APP_SIZE = 0x13F438
PACKAGE_SIZE = 0x14CF74
FLASH_BASE = 0x414
APP_AREA = 0x5414
AREA_SIZE = 0x13F6D8
AREA_END = APP_AREA + AREA_SIZE + 0x80
CHIP_KEY = 0x980F


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def crc(data: bytes) -> int:
    return binascii.crc_hqx(data, 0)


def transform(data: bytes, key: int = 0xFFFF) -> bytes:
    out = bytearray(data)
    for i in range(len(out)):
        out[i] ^= key & 255
        key = ((key << 1) ^ (0x1021 if key & 0x8000 else 0)) & 0xFFFF
    return bytes(out)


def sfc(data: bytes) -> bytes:
    return b"".join(transform(data[p:p + 32], CHIP_KEY ^ (p >> 2))
                    for p in range(0, len(data), 32))


def header(data: bytes) -> dict:
    require(len(data) == 32, "Truncated JLFS header")
    hcrc, dcrc, offset, size, flags, reserved, index, name = struct.unpack(
        "<HHIIBBH16s", data)
    require(crc(data[2:]) == hcrc, "JLFS header CRC mismatch")
    return dict(data_crc=dcrc, offset=offset, size=size,
                name=name.split(b"\0", 1)[0])


def inspect(image: bytes) -> tuple[bytes, bytearray, bytearray, list[bytearray]]:
    """Validate the known V75 layout and CRCs; return decoded components."""
    require(len(image) == PACKAGE_SIZE, "Wrong firmware package size")
    cfg = image[0x4864:0x4AFE]
    require(crc(cfg[:32]) == int.from_bytes(cfg[32:34], "little"),
            "Chip configuration CRC mismatch")
    threshold = sum(cfg[:16]) & 255
    threshold = 0xAA if threshold >= 0xE0 else 0x55 if threshold <= 0x10 else threshold
    key = sum(1 << i for i in range(16) if (cfg[16 + i] ^ cfg[15 - i]) < threshold)
    require(key == CHIP_KEY, "Unexpected chip key")

    decoded = bytearray(sfc(image[APP_AREA:AREA_END]))
    area = header(decoded[:32])
    require(area["size"] == AREA_SIZE, "Unexpected app area size")
    child = header(decoded[32:64])
    require((child["name"], child["offset"], child["size"]) ==
            (b"app.bin", 0x120, APP_SIZE), "Unexpected app record")
    app = bytes(decoded[0x120:0x120 + APP_SIZE])
    require(b"MK300_075" in app, "Missing V75 marker")
    require(crc(app) == child["data_crc"], "App data CRC mismatch")
    require(crc(decoded[32:AREA_SIZE]) == area["data_crc"], "App area CRC mismatch")
    for p in range(64, 0x120, 32):
        header(decoded[p:p + 32])
    ext = header(decoded[AREA_SIZE:AREA_SIZE + 32])
    require((ext["name"], ext["size"]) == (b"EXT_RESERVED", 0x80),
            "Unexpected extension record")
    for p in range(AREA_SIZE + 32, AREA_SIZE + 128, 32):
        header(decoded[p:p + 32])

    # The UFW prefix interleaves one preserved byte after each 47 logical bytes.
    logical = bytearray(image[i + i // 47] for i in range(940))
    outer = bytearray(transform(logical[:64]))
    hcrc, lcrc, size, count, _, _, chip = struct.unpack("<HHIHHI48s", outer)
    require(hcrc == crc(outer[2:]), "UFW header CRC mismatch")
    require(count == 10 and size + 20 == len(image), "Unexpected UFW layout")
    require(chip.split(b"\0", 1)[0] == b"AC792N", "Wrong chip type")
    require(lcrc == crc(logical[64:864]), "UFW directory CRC mismatch")
    entries = [bytearray(transform(logical[64 + i * 80:144 + i * 80]))
               for i in range(count)]
    typ, index, flash_crc, _, off, size, allocation = struct.unpack_from(
        "<HHHHIII", entries[0])
    require((typ, index, off, size, allocation) ==
            (0, 0, 0x400, 0x145000, 0x145000), "Unexpected flash record")
    require(crc(image[FLASH_BASE:FLASH_BASE + size]) == flash_crc,
            "Flash image CRC mismatch")
    return app, decoded, logical, entries


def read_stock(image: bytes) -> bytes:
    require(sha(image) == STOCK_PACKAGE_SHA256,
            "Input must be the exact original V75 MK300.fwsc; SHA-256 does not match")
    app, _, _, _ = inspect(image)
    require(sha(app) == STOCK_APP_SHA256, "Original app SHA-256 mismatch")
    return app


def repack(image: bytes, app: bytes) -> bytes:
    """Replace only the app and required CRCs in a hash-pinned stock package."""
    require(sha(image) == STOCK_PACKAGE_SHA256, "Repack input is not original V75")
    require(len(app) == APP_SIZE, "App size changed")
    _, decoded, logical, entries = inspect(image)
    out = bytearray(image)
    decoded[0x120:0x120 + APP_SIZE] = app
    struct.pack_into("<H", decoded, 34, crc(app))
    struct.pack_into("<H", decoded, 32, crc(decoded[34:64]))
    struct.pack_into("<H", decoded, 2, crc(decoded[32:AREA_SIZE]))
    struct.pack_into("<H", decoded, 0, crc(decoded[2:32]))
    out[APP_AREA:AREA_END] = sfc(decoded)
    struct.pack_into("<H", entries[0], 4, crc(out[FLASH_BASE:FLASH_BASE + 0x145000]))
    logical[64:864] = b"".join(transform(entry) for entry in entries)
    outer = bytearray(transform(logical[:64]))
    struct.pack_into("<H", outer, 2, crc(logical[64:864]))
    struct.pack_into("<H", outer, 0, crc(outer[2:]))
    logical[:64] = transform(outer)
    for i in range(864):
        out[i + i // 47] = logical[i]
    require(len(out) == len(image), "Package size changed")
    require(all(a == b or i < 0x3C0 or APP_AREA <= i < AREA_END
                for i, (a, b) in enumerate(zip(image, out))),
            "Unexpected modification outside package header/app area")
    extracted, _, _, _ = inspect(bytes(out))
    require(extracted == app, "Repacked app differs after extraction")
    return bytes(out)
