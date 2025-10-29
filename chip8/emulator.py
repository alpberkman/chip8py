from chip8.instructions import match, Instr, Dud, Chain, Branch, Graphics, IxFX55
from chip8.io import Screen, Keyboard
from pathlib import Path


class OpcodeSizeError(ValueError):
    def __init__(self, expected: int, actual: int):
        self.expected = expected
        self.actual = actual
        super().__init__(f"Opcode must be {expected} bytes, got {actual}")


class Emu:
    INSTRUCTION_SIZE = 2
    MEM_SIZE = 0x1000
    START_ADDR = 0x200

    TIMER_FREQ = 60  # in Hz
    INSTR_FREQ = 600  # in Hz
    RATIO = INSTR_FREQ / TIMER_FREQ

    FONT = bytes([
        0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
    ])

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
        debug=False,
    ):
        self.debug = debug

        self.mem = bytearray(mem_size)
        self.mem[: len(self.FONT)] = self.FONT

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

        self.load(rom)

    def load(self, rom):
        self.rom = rom
        opcodes = Path(rom).read_bytes()
        self.rom_size = len(opcodes)
        self.mem[self.pc : self.pc + self.rom_size] = opcodes

    def next(self):
        self.pc = (self.pc + self.INSTRUCTION_SIZE) & 0x0FFF

    def unnext(self):
        self.pc = (self.pc - self.INSTRUCTION_SIZE) & 0x0FFF

    def ifetch(self, addr: int) -> int:
        opcode_bytes = self.mem[addr : addr + self.INSTRUCTION_SIZE]
        opcode = int.from_bytes(opcode_bytes, byteorder="big")
        return opcode

    def tick(self):
        pass

    def timer(self):
        self.ctr -= 1
        if not self.ctr:
            self.ctr = Emu.RATIO
            if self.dt:
                self.dt -= 1
            if self.st:
                self.st -= 1
            if self.it:
                self.it -= 1

    def __str__(self):
        acc = []
        acc.append(f"pc: {self.pc} i: {self.i}")
        acc.append(" ".join([f"v{i:x}: {self.v[i]:3}" for i in range(0, 8)]))
        acc.append(" ".join([f"v{i:x}: {self.v[i]:3}" for i in range(8, 16)]))
        acc.append(f"dt: {self.dt:3} st: {self.st:3} it: {self.it:3}")
        acc.append(str(self.scr))

        return "\n".join(acc)

    def compose(self, *instrs: Instr) -> Chain:
        return Chain(*[i for i in instrs if type(i) is not Dud])


class EmuInterpreter(Emu):

    def fetch(self) -> int:
        return self.ifetch(self.pc)

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
        if type(instr) is Chain:
            for _ in range(len(instr.instrs)):
                self.timer()
        else:
            self.timer()

    def tick(self):
        opcode = self.fetch()
        instr = self.decode(opcode)

        if self.debug:
            print(f"{self.pc:06X}: {instr}")

        self.next()
        self.execute(instr)


class EmuPreDecoded(EmuInterpreter):
    def __init__(self, rom: str, **kwargs):
        super().__init__(rom, **kwargs)
        self.cc = [Dud(0x0000)] * len(self.mem)
        self._build_cache(beg=self.pc, end=self.pc + self.rom_size)

        if self.debug:
            for i in range(self.pc, self.pc + self.rom_size):
                print(f"{i:06X}: {self.cc[i]}")
            print("End of code cache")

    def _build_cache(self, beg: int = Emu.START_ADDR, end: int = Emu.MEM_SIZE):
        for addr in range(beg, end, Emu.INSTRUCTION_SIZE):
            opcode = self.ifetch(addr)
            instr = self.decode(opcode)
            self.cc[addr] = instr
            if self.debug:
                print(f"Decoding 0x{addr:06X}: {instr}")

    def fetch(self) -> Instr:
        return self.cc[self.pc]

    def tick(self):
        instr = self.fetch()

        if self.debug:
            print(f"{self.pc:06X}: {instr}")

        self.next()
        self.execute(instr)


class EmuBasicBlock(EmuPreDecoded):
    def __init__(self, rom: str, **kwargs):
        super().__init__(rom, **kwargs)

        self.bb = {}

    def nnext(self, instr: Chain):
        n = self.INSTRUCTION_SIZE * len(instr.instrs)
        self.pc = (self.pc + n) & 0x0FFF

    def fetch(self):
        if self.pc not in self.bb:
            if self.debug:
                print(f"Fetching BB starting at {self.pc:06X}")

            beg = self.pc
            end = beg
            while not isinstance(self.cc[end], (Branch, Graphics, IxFX55)):
                end += self.INSTRUCTION_SIZE

            self.bb[self.pc] = self.compose(*self.cc[beg : end + self.INSTRUCTION_SIZE])

            if self.debug:
                print(f"{self.pc:06X}: {self.bb[self.pc]}")

        return self.bb[self.pc]

    def tick(self):
        instr = self.fetch()

        if self.debug:
            print(f"{self.pc:06X}: {instr}")

        self.nnext(instr)
        self.execute(instr)
