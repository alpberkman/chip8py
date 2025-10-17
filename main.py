#!/usr/bin/env python

from chip8.gui import main
from chip8.emulator import Emu
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("rom", help="Path to CHIP-8 ROM")
    parser.add_argument("--emu-type", type=str, default="predecoded", help="One of the following: basic (b), predecoded (pd), basicblock (bb)")
    parser.add_argument("--debug", action='store_true', help="Enable debug information")
    parser.add_argument("--scale", type=int, default=10, help="Pixel scale")
    parser.add_argument("--fps", type=int, default=Emu.INSTR_FREQ, help="Instruction ticks per second")
    args = parser.parse_args()
    main(args)