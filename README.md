# CHIP-8 Emulator
A CHIP-8 emulator written in Python with a **Pygame (GUI)** frontend.

## Features
- Full CHIP-8 instruction set, timers, and keypad
- Pygame windowed mode with audio
- 3 different backends (basic interpreter, pre-decoding, basic blocks)
- Configurable quirks and CPU speed
- Simple, modular codebase


## Configuration
Quirks can be toggled when initializing the Emu object

## Dependencies
- pygame

## Usage
```bash
./main.py --emu-type predecoding <ROM>
```

## Caveats
- Passes all of the tests from [Timendus's test suite](https://github.com/Timendus/chip8-test-suite) in basic interpreter and pre-decoding backends
- Basic block backend can't deal with self modifying code

## ROMs
Some game ROMs can be found [here](https://github.com/kripod/chip8-roms)

## Resources
- https://github.com/Timendus/chip8-test-suite
- https://timendus.github.io/silicon8/
- http://devernay.free.fr/hacks/chip8/C8TECH10.HTM
- https://www.laurencescotford.net/2020/07/19/chip-8-on-the-cosmac-vip-keyboard-input/
- https://www.laurencescotford.net/2020/07/19/chip-8-on-the-cosmac-vip-drawing-sprites/
- https://tobiasvl.github.io/blog/write-a-chip-8-emulator/
- [My other CHIP-8 interpreter implemented in C](https://github.com/alpberkman/chip8c)