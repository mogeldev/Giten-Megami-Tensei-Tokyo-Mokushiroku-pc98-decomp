#!/usr/bin/env python3
"""unexepack.py <packed.exe> <out.exe> - unpack a Microsoft EXEPACK'd MZ executable.

Why this exists: the only DOS-hosted MS C 5.1 in the workspace has every compiler pass packed
with EXEPACK, and this DOSBox-X build has no LOADFIX, so the packed stubs cannot run
(`Packed file is corrupt`). Unpacking offline removes the stub entirely.

Format (EXEPACK 4.05/4.06, which is what MS C 5.1 shipped):

  MZ header; the packed image sits after it. CS:IP point at the stub, whose first 16 bytes
  (at CS:0000) are a header of eight words:

      +00 real_ip   +02 real_cs   +04 mem_start   +06 exepack_size
      +08 real_sp   +0A real_ss   +0C dest_len     +0E skip_len (or 0x0000 / signature)
      +10 signature "RB"   (the header is 0x10 or 0x12 bytes, depending on version)

  The packed data is the load image up to CS:0000. The *last* byte of it is padding (0xFF, any
  number); decoding goes **backwards** from there. Each command byte has its low bit set on the
  final command; bits 7..1 select the kind:

      0xB0 / 0xB1   fill:  word count (LE), then the fill byte
      0xB2 / 0xB3   copy:  word count (LE), then that many literal bytes

  The stub is followed by an error string and the packed relocation table:
  16 groups of (count, then count offsets); group n belongs to segment n * 0x1000.

Verified round 262 against C1/C2/C3/CL of the MSC 5.1 tree by checking that the unpacked image
length equals dest_len*16 and that the result is a valid MZ.
"""
import struct
import sys


def unpack(d: bytes) -> bytes:
    if d[:2] != b"MZ":
        raise SystemExit("not an MZ executable")
    last, pages, nrel, hdr, minalloc, maxalloc, ss, sp, csum, ip, cs, reloff = \
        struct.unpack_from("<HHHHHHHHHHHH", d, 2)
    size = (pages - 1) * 512 + (last or 512)
    image = d[hdr * 16:size]

    stub = cs * 16                       # offset of the stub header inside the image
    hdr_words = struct.unpack_from("<8H", image, stub)
    real_ip, real_cs, _mem_start, _ep_size, real_sp, real_ss, dest_len, skip_len = hdr_words
    sig = image[stub + 0x10:stub + 0x12]
    hlen = 0x12 if sig == b"RB" else 0x10
    if sig != b"RB":
        # some versions put the signature at +0x0E and have a 14-byte header
        if image[stub + 0x0E:stub + 0x10] == b"RB":
            real_ip, real_cs, _m, _e, real_sp, real_ss, dest_len = struct.unpack_from("<7H", image, stub)
            skip_len = 1
            hlen = 0x10
        else:
            raise SystemExit("no EXEPACK signature (RB) found at the stub header")

    packed = bytearray(image[:stub])
    # trailing 0xFF padding
    while packed and packed[-1] == 0xFF:
        packed.pop()

    out = bytearray(dest_len * 16)
    src = len(packed) - 1
    dst = len(out) - 1
    while True:
        cmd = packed[src]
        src -= 1
        count = packed[src - 1] | (packed[src] << 8)     # LE word stored at src-1
        src -= 2
        kind = cmd & 0xFE
        if kind == 0xB0:                 # fill
            val = packed[src]
            src -= 1
            for _ in range(count):
                out[dst] = val
                dst -= 1
        elif kind == 0xB2:               # copy
            for _ in range(count):
                out[dst] = packed[src]
                dst -= 1
                src -= 1
        else:
            raise SystemExit(f"bad EXEPACK command {cmd:#04x} at {src + 1:#x}")
        if cmd & 1:
            break
    # Whatever precedes the first command is stored raw: copy it to the front unchanged.
    # src and dst must agree here, otherwise the stream was decoded wrongly.
    if src != dst:
        raise SystemExit(f"decode mismatch: src={src} dst={dst} (expected equal)")
    out[0:src + 1] = packed[0:src + 1]

    # relocation table: right after the stub, past the error message
    rpos = stub + hlen
    rpos = image.find(b"Packed file is corrupt", rpos)
    rpos += len(b"Packed file is corrupt")
    relocs = []
    for seg in range(16):
        n = struct.unpack_from("<H", image, rpos)[0]
        rpos += 2
        for _ in range(n):
            off = struct.unpack_from("<H", image, rpos)[0]
            rpos += 2
            relocs.append((off, seg * 0x1000))

    # build the new MZ
    hdr_size = ((0x1C + len(relocs) * 4 + 15) // 16) * 16
    tot = hdr_size + len(out)
    mz = bytearray(hdr_size)
    struct.pack_into("<2sHHHHHHHHHHHHH", mz, 0, b"MZ",
                     tot % 512, (tot + 511) // 512, len(relocs), hdr_size // 16,
                     minalloc, maxalloc, real_ss, real_sp, 0, real_ip, real_cs, 0x1C, 0)
    for i, (off, seg) in enumerate(relocs):
        struct.pack_into("<HH", mz, 0x1C + i * 4, off, seg)
    return bytes(mz) + bytes(out)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    data = open(sys.argv[1], "rb").read()
    res = unpack(data)
    open(sys.argv[2], "wb").write(res)
    print(f"{sys.argv[1]}: {len(data)} -> {len(res)} bytes")
