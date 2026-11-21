#!/usr/bin/env python3
# Re-run after extract-files.sh: python3 patch-nvram-gid.py proprietary/lib
# Changes the hardcoded nvram gid in chown(path, -1, 9997) to 9995 (AID_NVRAM in
# our system/core; 9997 is AID_EVERYBODY in L). Refuses to touch unexpected bytes.
import sys
SITES = {"libnvram.so": [0x1668, 0x16e4, 0x2282], "libfile_op.so": [0x1378, 0x13ec, 0x41be, 0x41e4]}
OLD, NEW = bytes.fromhex("42f20d72"), bytes.fromhex("42f20b72")  # movw r2,#9997 -> #9995
libdir = sys.argv[1]
for name, offs in SITES.items():
    p = f"{libdir}/{name}"
    b = bytearray(open(p, "rb").read())
    assert b.count(OLD) == len(offs), (name, b.count(OLD))
    for o in offs:
        assert bytes.fromhex("4ff0ff31") in (b[o-4:o], b[o+4:o+8], b[o+8:o+12]), (name, hex(o))  # mov.w r1,#-1 (uid unchanged)
        assert b[o:o+4] == OLD, (name, hex(o), b[o:o+4].hex())
        b[o:o+4] = NEW
    open(p, "wb").write(b)
    print("patched", name, [hex(o) for o in offs])
