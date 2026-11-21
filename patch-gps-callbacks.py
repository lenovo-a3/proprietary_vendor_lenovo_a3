#!/usr/bin/env python3
# Re-run after extract-files.sh: python3 patch-gps-callbacks.py proprietary/lib
# gps.default.so was built against an MTK GpsCallbacks with one extra field before
# create_thread_cb: mt3326_init calls create_thread_cb from offset 36 of the struct,
# which in AOSP L is request_utc_time_cb (create_thread_cb is at 32). The HAL never
# gets its state thread, takes the error path and blocks forever in cleanup, wedging
# system_server's android.bg thread inside GpsLocationProvider init. All other
# callbacks it uses (location 4, status 8, sv_status 12, nmea 16, acquire_wakelock 24)
# match AOSP. Fix: in mt3326_init (VA 0x3430 == file offset, first LOAD at 0),
# "ldr r6, [r5, #44]" (0x6aee; callbacks copy at r5+8) -> "ldr r6, [r5, #40]" (0x6aae).
# Refuses to touch unexpected bytes.
import struct, sys
p = f"{sys.argv[1]}/hw/gps.default.so"
b = bytearray(open(p, "rb").read())
OFF, OLD, NEW = 0x3430, 0x6aee, 0x6aae
cur = struct.unpack_from("<H", b, OFF)[0]
if cur == NEW:
    sys.exit(f"already patched: {p}")
assert cur == OLD, hex(cur)
assert struct.unpack_from("<H", b, OFF + 8)[0] == 0x47b0, "blx r6 not found"
struct.pack_into("<H", b, OFF, NEW)
open(p, "wb").write(b)
print("patched", p, "create_thread_cb offset 36 -> 32")
