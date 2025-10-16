from chip8.instructions import *
from pathlib import Path


class OpcodeSizeError(ValueError):
    def __init__(self, expected: int, actual: int):
        self.expected = expected
        self.actual = actual
        super().__init__(f"Opcode must be {expected} bytes, got {actual}")


class Screen(bytearray):
    SCREEN_WIDTH = 64
    SCREEN_HEIGHT = 32

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        self.width = width
        self.height = height
        self.size = width * height // 8
        super().__init__(self.size)

    def clear(self):
        for i in range(self.size):
            self[i] = 0

    def draw(self, emu, x: int, y: int, n: int):
        if emu.quirk_disp_wait:
            if emu.it:
                emu.unnext()
                return
            else:
                emu.it = 1

        xx = emu.v[x] % emu.scr.width
        yy = emu.v[y] % emu.scr.height
        emu.v[0xF] = 0

        if emu.quirk_clipping:
            if yy + n > emu.scr.height:
                n = emu.scr.height - yy

        # print(f"x: {xx}, y: {yy}, n: {n}")
        for i in range(n):
            bi = emu.mem[emu.i + i]
            if xx % 8 == 0:
                upper_nibble = bi
                lower_nibble = 0
            else:
                upper_nibble = (bi >> (xx % 8)) & 0xFF
                lower_nibble = (bi << (8 - (xx % 8))) & 0xFF

            emu.scr[xx // 8 + emu.scr.width // 8 * (yy + i)] = upper_nibble
            emu.scr[xx // 8 + 1 + emu.scr.width // 8 * (yy + i)] = lower_nibble

        #     print(f"i: {i:x}, {upper_nibble:08b}-{lower_nibble:08b}")
        # emu.scr[0] = 0xFF
        # print(f"{xx // 8 + emu.scr.width // 8 * yy} {xx // 8 + 1 + emu.scr.width // 8 * yy}")
        # print(super.__str__(self))

        pass

    def __str__(self):
        acc = f"w: {self.width} h: {self.height}\n"
        # acc += super.__str__(self)
        for i in range(self.size):
            bytei = self[i]
            for bit in range(7, -1, -1):
                if bytei & (1 << bit):
                    acc += "#"
                else:
                    acc += " "
            if i % 8 == 0:
                acc += "\n"
        return acc


class Keyboard(bytearray):
    KEYBOARD_WIDTH = 4
    KEYBOARD_HEIGHT = 4

    def __init__(self, width: int = KEYBOARD_WIDTH, height: int = KEYBOARD_HEIGHT):
        self.width = width
        self.height = height
        self.size = width * height // 8
        super().__init__(self.size)

    def __str__(self):
        acc = f"w: {self.width} h: {self.height}\n"
        for i in range(self.height):
            for j in range(self.width // 8):
                # acc += str(self[j + self.width // 8 * i])
                # acc += " "
                byte_val = self[j + self.width // 8 * i]
                # Iterate over 8 bits, most-significant bit first
                for bit in range(7, -1, -1):
                    if byte_val & (1 << bit):
                        acc += "#"
                    else:
                        acc += " "
            acc += "\n"
        return acc


class Emu:
    INSTRUCTION_SIZE = 2
    MEM_SIZE = 0x1000
    # STACK_DEPTH = 16
    START_ADDR = 0x200

    TIMER_FREQ = 60  # in Hz
    INSTR_FREQ = 600  # in Hz
    RATIO = INSTR_FREQ / TIMER_FREQ

    FONT = bytes(
        [
            0xF0,
            0x90,
            0x90,
            0x90,
            0xF0,  # 0
            0x20,
            0x60,
            0x20,
            0x20,
            0x70,  # 1
            0xF0,
            0x10,
            0xF0,
            0x80,
            0xF0,  # 2
            0xF0,
            0x10,
            0xF0,
            0x10,
            0xF0,  # 3
            0x90,
            0x90,
            0xF0,
            0x10,
            0x10,  # 4
            0xF0,
            0x80,
            0xF0,
            0x10,
            0xF0,  # 5
            0xF0,
            0x80,
            0xF0,
            0x90,
            0xF0,  # 6
            0xF0,
            0x10,
            0x20,
            0x40,
            0x40,  # 7
            0xF0,
            0x90,
            0xF0,
            0x90,
            0xF0,  # 8
            0xF0,
            0x90,
            0xF0,
            0x10,
            0xF0,  # 9
            0xF0,
            0x90,
            0xF0,
            0x90,
            0x90,  # A
            0xE0,
            0x90,
            0xE0,
            0x90,
            0xE0,  # B
            0xF0,
            0x80,
            0x80,
            0x80,
            0xF0,  # C
            0xE0,
            0x90,
            0x90,
            0x90,
            0xE0,  # D
            0xF0,
            0x80,
            0xF0,
            0x80,
            0xF0,  # E
            0xF0,
            0x80,
            0xF0,
            0x80,
            0x80,  # F
        ]
    )

    def __init__(
        self,
        rom: str,
        start_addr: int = START_ADDR,
        mem_size: int = MEM_SIZE,
        ratio: int = RATIO,
        quirk_vf_reset=True,
        quirk_memory=True,
        quirk_disp_wait=True,
        quirk_clipping=True,
        quirk_shifting=False,
        quirk_jumping=False,
    ):
        self.rom = rom

        self.mem = bytearray(mem_size)
        self.mem[: len(self.FONT)] = self.FONT

        rom_bytes = Path(rom).read_bytes()
        self.mem[self.START_ADDR : self.START_ADDR + len(rom_bytes)] = rom_bytes

        self.pc = start_addr

        self.i = 0x0
        self.v = bytearray(16)

        self.stack = []

        self.scr = Screen()
        self.kbd = Keyboard()

        self.dt = 0
        self.st = 0
        self.it = 0

        self.release = 0
        self.ctr = ratio
        self.dirty = 1

        self.quirk_vf_reset = quirk_vf_reset
        self.quirk_memory = quirk_memory
        self.quirk_disp_wait = quirk_disp_wait
        self.quirk_clipping = quirk_clipping
        self.quirk_shifting = quirk_shifting
        self.quirk_jumping = quirk_jumping

    def next(self):
        self.pc = (self.pc + 2) & 0x0FFF

    def unnext(self):
        self.pc = (self.pc - 2) & 0x0FFF

    def tick(self):
        pass

    def __str__(self):
        acc = ""
        acc += f"pc: {self.pc} i: {self.i}\n"
        acc += f"{self.v}\n"
        acc += f"{self.scr}\n"

        return acc

    def compose(self, *instrs: Instr):
        return Chain(*instrs)


class EmuInterpreter(Emu):

    def fetch(self) -> int:
        opcode_bytes = self.mem[self.pc : self.pc + self.INSTRUCTION_SIZE]
        opcode = int.from_bytes(opcode_bytes, byteorder="big")
        self.next()
        return opcode

    def decode(self, opcode: int) -> Instr:

        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F
        nn = opcode & 0x00FF
        nnn = opcode & 0x0FFF

        instr = match(opcode)
        kwargs = {"opcode": opcode, "x": x, "y": y, "n": n, "nn": nn, "nnn": nnn}

        return instr(**kwargs)

    def execute(self, instr: Instr):
        instr.eval(self)

    def tick(self):
        opcode = self.fetch()
        instr = self.decode(opcode)
        self.execute(instr)


class EmuPreDecoded(EmuInterpreter):
    def __init__(self, rom: str, **kwargs):
        super().__init__(rom, **kwargs)
        self.cc = [Instr()] * len(self.mem)
        self._build_cache()

    def _build_cache(self, beg: int = Emu.START_ADDR, end: int = Emu.MEM_SIZE):
        for addr in range(beg, end, Emu.INSTRUCTION_SIZE):
            opcode_bytes = self.mem[addr : addr + self.INSTRUCTION_SIZE]
            opcode = int.from_bytes(opcode_bytes, byteorder="big")
            instr = self.decode(opcode)
            self.cc[addr] = instr

    def fetch(self) -> Instr:
        instr = self.cc(self.pc)
        self.next()
        return instr

    def tick(self):
        instr = self.fetch()
        self.execute(instr)


class EmuBasicBlock(EmuPreDecoded):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dp = {}

    def fetch(self):
        pass

    def tick(self):
        pass
