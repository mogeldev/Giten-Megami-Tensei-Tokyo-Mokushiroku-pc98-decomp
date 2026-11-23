/* 1aa1:0130 — far Pascal wrapper that forwards the long constant 0x800.
 *
 * The callee below is a LAYOUT SCAFFOLD, not a recovered function: MSC 6 emits
 * the `0E E8` (push cs; call) form only when the callee is defined in the same
 * translation unit, and its rel16 is a linker operand (OMF fixup) that
 * match.py masks. The real target of 1aa1:FEC6 is 1aa1:FECF (linear 0x2A8DF),
 * an entry inside the merged inventory unit 2a8a:0002 — not an inventory
 * boundary, so it cannot be declared from the inventory either.
 *
 * Only the 11 bytes of F_1AA1 are claimed in the ledger.
 *
 * Flag insight: /G0 (8086) makes MSC 6 materialise the long constant as
 * `mov ax,0x800 / cwd / push dx / push ax`; /G1 uses the push-immediate form
 * `6A 00 / 68 00 08`, and MSC 7 always calls through `9A`. */
long far pascal same_segment_callee(long v)
{
    return v;
}

long far pascal F_1AA1(void)
{
    return same_segment_callee(0x800L);
}
