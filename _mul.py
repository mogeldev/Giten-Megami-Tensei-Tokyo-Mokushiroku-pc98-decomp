import csv, re
IMG = open(r"../giten/DDS98/DDS98.EXE","rb").read()[896*16:339735]
led = open(r"../docs/MATCHING.md", encoding="utf-8").read()
done = {int(m.group(1),16)*16+int(m.group(2),16) for m in re.finditer(r"^\|\s*([0-9a-f]{4}):([0-9a-f]{4})\s*\|", led, re.M)}
units = {int(r["linear"],16): (r["va"], int(r["size"])) for r in csv.DictReader(open(r"../ground_truth/units.csv"))}
hits = []
for lin,(va,size) in units.items():
    if lin in done: continue
    b = IMG[lin-0x10000:lin-0x10000+size]
    if len(b) >= 6 and b[0] == 0xB8 and b[3] == 0xF7 and b[4] == 0x26:
        hits.append((va, size, b.hex()))
print(f"{len(hits)} units start with `mov ax,imm / mul word [disp]`")
for va,size,hx in hits[:10]: print(f"   {va} {size:>2}B {hx}")
