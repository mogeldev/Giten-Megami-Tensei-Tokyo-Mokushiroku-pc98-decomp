"""Annotate a slice of the image so hand-decoding stops producing arithmetic errors.

Not a disassembler: it prints offsets, bytes, and the few facts that keep coming up
(jump targets, call forms, returns, push/lea/mov encodings).  Instruction lengths are
only computed for the handful of opcodes listed below; anything else is shown as
`?    ` and the run continues byte by byte, so a wrong guess can never make the tool
lie loudly - it just stops interpreting.

    python tools/dis.py 13d5:000c [length]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = open(os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE"), "rb").read()[896 * 16:339735]

# opcode -> mnemonic and total length (fixed-size forms only)
SIMPLE = {
    0x55: ("push bp", 1), 0x56: ("push si", 1), 0x57: ("push di", 1),
    0x5D: ("pop bp", 1), 0x5E: ("pop si", 1), 0x5F: ("pop di", 1),
    0x1E: ("push ds", 1), 0x1F: ("pop ds", 1), 0x16: ("push ss", 1), 0x17: ("pop ss", 1),
    0x06: ("push es", 1), 0x07: ("pop es", 1), 0x0E: ("push cs", 1),
    0x90: ("nop", 1), 0x98: ("cbw", 1), 0x99: ("cwd", 1), 0x9C: ("pushf", 1),
    0x9D: ("popf", 1), 0xFA: ("cli", 1), 0xFB: ("sti", 1), 0xCC: ("int3", 1),
    0xF8: ("clc", 1), 0xF9: ("stc", 1), 0xF5: ("cmc", 1), 0x9E: ("sahf", 1),
    0x9F: ("lahf", 1), 0x40: ("inc ax", 1), 0x48: ("dec ax", 1),
    0x4A: ("dec dx", 1), 0x4B: ("dec bx", 1), 0x4E: ("dec si", 1),
    0xC3: ("ret", 1), 0xCB: ("retf", 1),
}


def decode(b, i):
    """Return (text, length) for the instruction at b[i]."""
    op = b[i]
    if op in SIMPLE:
        return SIMPLE[op]
    if op in range(0x70, 0x80):
        tgt = i + 2 + (b[i + 1] - 256 if b[i + 1] > 127 else b[i + 1])
        return (f"j{op - 0x70:02x} {tgt:#06x}", 2)
    if op == 0xEB:
        tgt = i + 2 + (b[i + 1] - 256 if b[i + 1] > 127 else b[i + 1])
        return (f"jmp {tgt:#06x}", 2)
    if op == 0xE9:
        d = int.from_bytes(b[i + 1:i + 3], "little", signed=True)
        return (f"jmp {i + 3 + d:#06x}", 3)
    if op == 0xE8:
        d = int.from_bytes(b[i + 1:i + 3], "little", signed=True)
        return (f"call {i + 3 + d:#06x}", 3)
    if op == 0x9A:
        off = int.from_bytes(b[i + 1:i + 3], "little")
        seg = int.from_bytes(b[i + 3:i + 5], "little")
        return (f"call far {seg:04x}:{off:04x}", 5)
    if op == 0xC9:
        return ("leave", 1)
    if op in (0xCA, 0xC2):
        n = int.from_bytes(b[i + 1:i + 3], "little")
        return (("retf" if op == 0xCA else "ret") + f" {n}", 3)
    if op == 0xC8:
        return (f"enter {int.from_bytes(b[i+1:i+3],'little'):#x}, {b[i+3]}", 4)
    if op == 0xB8:
        return (f"mov ax, {int.from_bytes(b[i+1:i+3],'little'):#06x}", 3)
    if op == 0x8B:
        return ("mov r16, r/m16", 2)
    if op == 0x89:
        return ("mov r/m16, r16", 2)
    if op == 0xA1:
        return ("mov ax, [disp16]", 3)
    if op == 0xA3:
        return ("mov [disp16], ax", 3)
    if op == 0xA0:
        return ("mov al, [disp16]", 3)
    if op == 0xC7:
        return ("mov word [..], imm16", 4)
    if op == 0xFF:
        return ("push/call/jmp r/m16", 2)
    if op == 0x83:
        return ("alu r/m16, imm8", 3)
    if op == 0x81:
        return ("alu r/m16, imm16", 4)
    if op == 0xCD:
        return (f"int {b[i+1]:#04x}", 2)
    return ("?", 1)


def main():
    va = sys.argv[1]
    seg, off = va.split(":")
    lin = int(seg, 16) * 16 + int(off, 16) - 0x10000
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 64
    b = IMG[lin:lin + n]
    i = 0
    while i < len(b):
        text, ln = decode(b, i)
        raw = " ".join(f"{x:02X}" for x in b[i:i + ln])
        print(f"{i:04x}  {raw:<17} {text}")
        i += ln


if __name__ == "__main__":
    main()
