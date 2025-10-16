#!/usr/bin/env python

from chip8.emulator import EmuInterpreter as Emu


roms = [
    "1-chip8-logo.ch8",
    "2-ibm-logo.ch8",
    "3-corax+.ch8",
    "4-flags.ch8",
    "5-quirks.ch8",
    "6-keypad.ch8",
    "7-beep.ch8",
    "8-scrolling.ch8",
]

emu = Emu(roms[3])
print(emu)
while 1:
    emu.tick()

    if emu.dirty:
        print(emu)
        #     print("Dirty")
        emu.dirty = 0
    # else:
    #     print("Clean")
    # print(emu.scr)
