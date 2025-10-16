#!/usr/bin/env python

from chip8.emulator import EmuInterpreter as Emu

emu = Emu("1-chip8-logo.ch8")
print(emu)
while 1:
    emu.tick()
    # if emu.dirty:
    #     print("Dirty")
    #     emu.dirty = 0
    # else:
    #     print("Clean")
    print(emu.scr)
