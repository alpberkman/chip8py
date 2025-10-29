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
- Passes all of the tests from [Timendus's test suite](https://github.com/Timendus/chip8-test-suite) in all backends

## ROMs
Some game ROMs can be found [here](https://github.com/kripod/chip8-roms)

## Implementations
This section is meant for people who are interested in emulation techniques. This is not meant to be a full guide but exists to give some ideas.

### Common Techniques - Object Oriented Programming
- During the implementation I have followed an object oriented aproach in which every Instruction is the subclass of an Instr class. Thanks to that I can controll the default behaviour of every unchanged/unimplemented instruction. This helps greatly when disassembling, debugging or logging.
- I have implemented middle level classes (Branch, Bitwise, Math, Load, Graphics) that help with organizing the instructions become relevant in basic block version.
- I have implmented the instruction decoding using regex. Generally this is a terrible idea, however in this case once it was implemented I didn't needed to change or add anything for new instructions. A better/faster/more efficent aproach would have been using look-up tables via Python dictionaries (up to depth 2)

### Basic Interpreter
This is the simples emulator possible. It is also the one least likely to have bugs. However it is also theoretically the slowest. A tick in this emulator is as follows:
- Fetch: get the opcode from memory
- Decode: turn the opcode into something the interpreter can understand (here the correct instruction class)
- Next: increase the PC by the size of an instruction
- Execute & Timer: evaluate the instruction and increse the timer

### Pre-Decoding
This is a slightly more advanced emulator. Instead of decoding the instruction as they come up they are all decoded once at the start. This has two main benefits:
1. Once the emulator starts it is faster since there is no decoding step
2. Since everything is already decoded, same opcodes that make up a loop/function need not be decoded again and again

However this technique has two drawbacks:
1. Opcode boundries are not always very simple. For CHIP-8 each instruction is 2 bytes long, however there are other architectures that have variable sized instructions, which when split may yield more instructions
2. Care should be taken when working with self modifying code. And as I came to find out CHIP-8 often uses such techniques. To prevent problems that arise from ignoring self modification, either before each execution the opcode in the memory can be compared with the predecoded one to establish whether it has been changed or if any instruction overwrites memory (especially the code section), these sections should be re-decoded.

Once the emulator is started it should build a code cache, basically decode everything. A tick in this emulator is as follows:
- Fetch: get the instruction from the code cache
- Next: increase the PC by the size of an instruction
- Execute, Re-Decode & Timer: evaluate the instruction, if the memory has been changed decode it, and increse the timer

### Basic Blocks
This is an even more advanced technique. Here basic blocks are supposed to be compiled for increasing the speed. In my implementation I split the code in basic blocks however there is no compilation. Just like in pre-decoded emulator, if the code modifies itself, we need to handle the newly changed basic blocks. We do this by deleting them.A tick in this emulator is as follows:
- Fetch: get the basic block, if it doesn't exist prepare it
- Nnext: increase the PC by the size of an instruction times number of instructions
- Execute, Re-Decode/Delete BB & Timer: evaluate the instruction, if the memory has been changed decode it and delete the relevant basic block, and increse the timer

## Resources
- https://github.com/Timendus/chip8-test-suite
- https://timendus.github.io/silicon8/
- http://devernay.free.fr/hacks/chip8/C8TECH10.HTM
- https://www.laurencescotford.net/2020/07/19/chip-8-on-the-cosmac-vip-keyboard-input/
- https://www.laurencescotford.net/2020/07/19/chip-8-on-the-cosmac-vip-drawing-sprites/
- https://tobiasvl.github.io/blog/write-a-chip-8-emulator/
- [My other CHIP-8 interpreter implemented in C](https://github.com/alpberkman/chip8c)