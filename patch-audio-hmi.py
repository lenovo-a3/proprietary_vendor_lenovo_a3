#!/usr/bin/env python3
# Re-run after extract-files.sh: python3 patch-audio-hmi.py proprietary/lib
# audio.primary.mt6589.so's HAL_MODULE_INFO_SYM has id "libaudio"; L's hw_get_module
# requires "audio" (AUDIO_HARDWARE_MODULE_ID). Point HMI.id (an R_ARM_RELATIVE addend
# at file offset 0x72010, VA 0x73010) 3 bytes into "libaudio\0", i.e. at "audio\0".
# Refuses to touch unexpected bytes.
import struct, sys
p = f"{sys.argv[1]}/hw/audio.primary.mt6589.so"
b = bytearray(open(p, "rb").read())
OFF, OLD, NEW = 0x72010, 0x5bb78, 0x5bb7b
assert b[OFF-8:OFF-4] == b"TMWH", "HMI tag not found"  # HARDWARE_MODULE_TAG
assert b[OLD:OLD+9] == b"libaudio\0", b[OLD:OLD+9]
assert struct.unpack_from("<I", b, OFF)[0] == OLD, hex(struct.unpack_from("<I", b, OFF)[0])
struct.pack_into("<I", b, OFF, NEW)
open(p, "wb").write(b)
print("patched", p, "HMI.id -> \"audio\"")
