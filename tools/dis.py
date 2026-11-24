"""Annotate a slice of the image so hand-decoding stops producing arithmetic errors.

Prints offsets, bytes, and one decoded instruction per line for the 8086 subset this
binary actually uses, including ModRM operands (`[bp+06]`, `[bx+si]`, `ax`, ...), so a
slice can be read without a second tool.  Anything unrecognised is shown as `?` and the
run continues byte by byte, so a wrong guess can never make the tool lie loudly - it just
stops interpreting.

    python tools/dis.py 13d5:000c [length]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = open(os.path.join(ROOT, "..", "giten", "DDS98", "DDS98.EXE"), "rb").read()[896 * 16:339735]
BASE = 0

R16 = ("ax", "cx", "dx", "bx", "sp", "bp", "si", "di")
R8 = ("al", "cl", "dl", "bl", "ah", "ch", "dh", "bh")
SREG = ("es", "cs", "ss", "ds")
ALU = ("add", "or", "adc", "sbb", "and", "sub", "xor", "cmp")
SHIFT = ("rol", "ror", "rcl", "rcr", "shl", "shr", "sal", "sar")

SIMPLE = {
    0x55: ("push bp", 1), 0x56: ("push si", 1), 0x57: ("push di", 1),
    0x5D: ("pop bp", 1), 0x5E: ("pop si", 1), 0x5F: ("pop di", 1),
    0x1E: ("push ds", 1), 0x1F: ("pop ds", 1), 0x16: ("push ss", 1), 0x17: ("pop ss", 1),
    0x06: ("push es", 1), 0x07: ("pop es", 1), 0x0E: ("push cs", 1),
    0x90: ("nop", 1), 0x98: ("cbw", 1), 0x99: ("cwd", 1), 0x9C: ("pushf", 1),
    0x9D: ("popf", 1), 0xFA: ("cli", 1), 0xFB: ("sti", 1), 0xCC: ("int3", 1),
    0xF8: ("clc", 1), 0xF9: ("stc", 1), 0xF5: ("cmc", 1), 0x9E: ("sahf", 1),
    0x9F: ("lahf", 1), 0x4F: ("dec di", 1),
    0xC3: ("ret", 1), 0xCB: ("retf", 1),
    0xA4: ("movsb", 1), 0xA5: ("movsw", 1), 0xAA: ("stosb", 1), 0xAB: ("stosw", 1),
    0xAC: ("lodsb", 1), 0xAD: ("lodsw", 1), 0xA6: ("cmpsb", 1), 0xA7: ("cmpsw", 1),
    0xAE: ("scasb", 1), 0xAF: ("scasw", 1), 0xF3: ("rep", 1), 0xF2: ("repne", 1),
}
for _i in range(8):
    SIMPLE.setdefault(0x40 + _i, ("inc " + R16[_i], 1))
    SIMPLE.setdefault(0x48 + _i, ("dec " + R16[_i], 1))
    SIMPLE.setdefault(0x50 + _i, ("push " + R16[_i], 1))
    SIMPLE.setdefault(0x58 + _i, ("pop " + R16[_i], 1))
    SIMPLE.setdefault(0xB0 + _i, ("mov " + R8[_i] + ", imm8", 2))
    SIMPLE.setdefault(0x91 + _i - 1 if _i else 0x90, ("xchg ax, " + R16[_i], 1))

PREFIX = {0x26: "es:", 0x2E: "cs:", 0x36: "ss:", 0x3E: "ds:"}


def rm(b, i, mod, rm, w8=False):
    """Format a ModRM operand starting at b[i]; return (text, size)."""
    if mod == 3:
        return (R8 if w8 else R16)[rm], 0
    base = ("bx+si", "bx+di", "bp+si", "bp+di", "si", "di", "bp" if mod else "disp16", "bx")[rm]
    if mod == 0 and rm == 6:
        return "[%#06x]" % int.from_bytes(b[i:i + 2], "little"), 2
    if mod == 0:
        return "[%s]" % base, 0
    if mod == 1:
        d = b[i]
        d = d - 256 if d > 127 else d
        return ("[%s+%#x]" if d >= 0 else "[%s-%#x]") % (base, d if d >= 0 else -d), 1
    d = int.from_bytes(b[i:i + 2], "little")
    if d < 0x8000:
        return "[%s+%#x]" % (base, d), 2
    return "[%s-%#x]" % (base, 0x10000 - d), 2


def modrm(b, i, w8=False):
    """Return (reg-text, rm-text, total length, regfield)."""
    m = b[i]
    mod, reg, r = m >> 6, (m >> 3) & 7, m & 7
    rmtxt, extra = rm(b, i + 1, mod, r, w8)
    return (R8 if w8 else R16)[reg], rmtxt, 2 + extra, reg


def decode(b, i):
    """Return (text, length) for the instruction at b[i]."""
    start = i
    pfx = ""
    while b[i] in PREFIX:
        pfx += PREFIX[b[i]]
        i += 1
    op = b[i]
    if op in SIMPLE:
        t, n = SIMPLE[op]
        return (pfx + t, i - start + n)

    if op in range(0x70, 0x80):
        tgt = i + 2 + (b[i + 1] - 256 if b[i + 1] > 127 else b[i + 1])
        JCC = ("jo", "jno", "jb", "jae", "je", "jne", "jbe", "ja",
               "js", "jns", "jp", "jnp", "jl", "jge", "jle", "jg")
        return (pfx + f"{JCC[op - 0x70]} {(tgt + BASE) & 0xFFFF:04x}", 2 + i - start)
    if op in (0xEB, 0xE9, 0xE8):
        if op == 0xEB:
            tgt = i + 2 + (b[i + 1] - 256 if b[i + 1] > 127 else b[i + 1])
            return (pfx + f"jmp {(tgt + BASE) & 0xFFFF:04x}", 2 + i - start)
        d = int.from_bytes(b[i + 1:i + 3], "little", signed=True)
        mn = "jmp" if op == 0xE9 else "call"
        return (pfx + f"{mn} {(i + 3 + d + BASE) & 0xFFFF:04x}", 3 + i - start)
    if op == 0x9A:
        off = int.from_bytes(b[i + 1:i + 3], "little")
        seg = int.from_bytes(b[i + 3:i + 5], "little")
        return (pfx + f"call far {seg:04x}:{off:04x}", 5)
    if op == 0xC9:
        return ("leave", 1 + i - start)
    if op in (0xCA, 0xC2):
        n = int.from_bytes(b[i + 1:i + 3], "little")
        return (("retf" if op == 0xCA else "ret") + f" {n}", 3 + i - start)
    if op == 0xC8:
        return (f"enter {int.from_bytes(b[i+1:i+3],'little'):#x}, {b[i+3]}", 4)
    if op in (0xA0, 0xA1, 0xA2, 0xA3):
        addr = int.from_bytes(b[i + 1:i + 3], "little")
        reg = ("al" if op in (0xA0, 0xA2) else "ax")
        if op in (0xA0, 0xA1):
            return (pfx + f"mov {reg}, [{addr:#06x}]", 3 + i - start)
        return (pfx + f"mov [{addr:#06x}], {reg}", 3 + i - start)

    # ALU r/m16, r16  (0x01..0x3D odd) and r16, r/m16 (0x03..0x3B other odd)
    if 0x00 <= op <= 0x3D and (op & 7) in (1, 3):
        mn = ALU[(op >> 3) & 7]
        reg, rmtxt, n, _ = modrm(b, i + 1)
        if op & 1 and (op & 2) == 0:
            return (pfx + f"{mn} {rmtxt}, {reg}", n + i - start)
        return (pfx + f"{mn} {reg}, {rmtxt}", n + i - start)
    if 0x00 <= op <= 0x3D and (op & 7) in (0, 2):
        mn = ALU[(op >> 3) & 7]
        reg, rmtxt, n, _ = modrm(b, i + 1, w8=True)
        return (pfx + f"{mn} {reg}, {rmtxt}", n + i - start)
    if 0x04 <= op <= 0x3C and (op & 7) == 4:
        mn = ALU[(op >> 3) & 7]
        return (pfx + f"{mn} al, {b[i+1]:#04x}", 2)
    if 0x05 <= op <= 0x3D and (op & 7) == 5:
        mn = ALU[(op >> 3) & 7]
        return (pfx + f"{mn} ax, {int.from_bytes(b[i+1:i+3],'little'):#06x}", 3)

    if op in (0x8B, 0x89, 0x8A, 0x88, 0x8D, 0x84, 0x85, 0x86, 0x87, 0x8E, 0x8C):
        mn = {0x8B: "mov", 0x89: "mov", 0x8A: "mov", 0x88: "mov", 0x8D: "lea",
              0x84: "test", 0x85: "test", 0x86: "xchg", 0x87: "xchg",
              0x8E: "mov", 0x8C: "mov"}[op]
        w8 = op in (0x88, 0x8A)
        reg, rmtxt, n, _ = modrm(b, i + 1, w8)
        if w8:
            m8 = b[i + 1]
            reg = R8[(m8 >> 3) & 7] if (m8 >> 6) == 3 else R8[(b[i + 1] >> 3) & 7]
        if op in (0x8C,):
            return (pfx + f"mov {rmtxt}, {SREG[(b[i+1] >> 3) & 3]}", n + i - start)
        if op in (0x8E,):
            return (pfx + f"mov {SREG[(b[i+1] >> 3) & 3]}, {rmtxt}", n + i - start)
        if op in (0x88, 0x89, 0x8C):
            return (pfx + f"{mn} {rmtxt}, {reg}", n + i - start)
        return (pfx + f"{mn} {reg}, {rmtxt}", n + i - start)
    if op in (0xC6, 0xC7):
        reg, rmtxt, n, _ = modrm(b, i + 1, op == 0xC6)
        if op == 0xC6:
            return (pfx + f"mov {rmtxt}, {b[i+n]:#04x}", n + 1 + i - start)
        return (pfx + f"mov {rmtxt}, {int.from_bytes(b[i+n:i+2+n],'little'):#06x}", n + 2 + i - start)
    if op in (0x83, 0x81):
        mn_i = (b[i + 1] >> 3) & 7
        reg, rmtxt, n, _ = modrm(b, i + 1)
        mn = ALU[mn_i]
        if op == 0x83:
            d = b[i + n]
            return (pfx + f"{mn} {rmtxt}, {d:#04x}", n + 1 + i - start)
        return (pfx + f"{mn} {rmtxt}, {int.from_bytes(b[i+n:i+2+n],'little'):#06x}", n + 2 + i - start)
    if op in (0xC0, 0xC1):
        reg, rmtxt, n, _ = modrm(b, i + 1, op == 0xC0)
        mn = SHIFT[(b[i + 1] >> 3) & 7]
        c = b[i + n]
        return (pfx + f"{mn} {rmtxt}, {c if c != 1 else '1'}", n + 1 + i - start)
    if op in (0xD0, 0xD1, 0xD2, 0xD3):
        reg, rmtxt, n, _ = modrm(b, i + 1, op in (0xD0, 0xD2))
        mn = SHIFT[(b[i + 1] >> 3) & 7]
        c = {0xD0: "1", 0xD1: "1", 0xD2: "cl", 0xD3: "cl"}[op]
        return (pfx + f"{mn} {rmtxt}, {c}", n + i - start)
    if op in (0x69, 0x6B):
        reg, rmtxt, n, _ = modrm(b, i + 1)
        if op == 0x6B:
            return (pfx + f"imul {reg}, {rmtxt}, {b[i+n]:#04x}", n + 1 + i - start)
        return (pfx + f"imul {reg}, {rmtxt}, {int.from_bytes(b[i+n:i+2+n],'little'):#06x}", n + 2 + i - start)
    if op in (0xF6, 0xF7):
        regf = (b[i + 1] >> 3) & 7
        reg, rmtxt, n, _ = modrm(b, i + 1, op == 0xF6)
        if regf in (0, 1):
            return (pfx + f"test {rmtxt}, imm", n + (1 if op == 0xF6 else 2) + i - start)
        mn = ("not", "neg", "mul", "imul", "div", "idiv")[regf - 2]
        return (pfx + f"{mn} {rmtxt}", n + i - start)
    if op in (0xFE, 0xFF):
        regf = (b[i + 1] >> 3) & 7
        reg, rmtxt, n, _ = modrm(b, i + 1, op == 0xFE)
        if op == 0xFE:
            return (pfx + f"{'inc' if regf == 0 else 'dec'} {rmtxt}", n + i - start)
        return (pfx + f"{('inc', 'dec', 'call', 'call far', 'jmp', 'jmp far', 'push')[regf]} {rmtxt}", n + i - start)
    if op in (0xC4, 0xC5):
        reg, rmtxt, n, _ = modrm(b, i + 1)
        return (pfx + f"{'les' if op == 0xC4 else 'lds'} {reg}, {rmtxt}", n + i - start)
    if op == 0x68:
        return (pfx + f"push {int.from_bytes(b[i+1:i+3],'little'):#06x}", 3 + i - start)
    if op == 0x6A:
        d = b[i + 1]
        return (pfx + f"push {(d - 256 if d > 127 else d):#04x}", 2 + i - start)
    if 0xB8 <= op <= 0xBF:
        return (pfx + f"mov {R16[op - 0xB8]}, {int.from_bytes(b[i+1:i+3],'little'):#06x}", 3)
    if op == 0xCD:
        return (f"int {b[i+1]:#04x}", 2)
    if op in (0xE4, 0xE5, 0xE6, 0xE7):
        return (pfx + f"{'in' if op < 0xE6 else 'out'} ... {b[i+1]:#04x}", 2)
    if op == 0xE0:
        return ("loopne", 2)
    return ("?", 1)


def main():
    va = sys.argv[1]
    seg, off = va.split(":")
    lin = int(seg, 16) * 16 + int(off, 16) - 0x10000
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 64
    globals()["BASE"] = (lin + 0x10000) & 0xFFFF
    b = IMG[lin:lin + n]
    i = 0
    while i < len(b):
        try:
            text, ln = decode(b, i)
        except IndexError:
            text, ln = "?", 1
        hexs = " ".join("%02X" % c for c in b[i:i + ln])
        print("%04x  %-16s %s" % (i, hexs, text))
        i += max(ln, 1)


if __name__ == "__main__":
    main()
