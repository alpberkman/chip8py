# class Instr():

#    def __init__(self):
#        pass


# class Instruction:
#     def __init__(self, id, **kwargs):
#         self.id = id
#         self.args = kwargs

# class InstructionFactory:
#     pass

from instructions import *


class OpcodeSizeError(ValueError):
    def __init__(self, expected: int, actual: int):
        self.expected = expected
        self.actual = actual
        super().__init__(f"Opcode must be {expected} bytes, got {actual}")


class BooleanMatrix2D(list):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        super().__init__([False] * (width * height))

    def clear(self):
        for i in self:
            self[i] = False

    def set(self, x: int, y: int, val: bool):
        self[x + self.width * y] = val

    def get(self, x: int, y: int):
        return self[x + self.width * y]

    def toggle(self, x, y):
        self[x + self.width * y] ^= True

    def __str__(self):
        acc = ""
        for i in range(self.height):
            for j in range(self.width):
                acc += "#" if self[j + self.width * i] else " "
            acc += "\n"
        return acc


class Screen(BooleanMatrix2D):
    SCREEN_WIDTH = 64
    SCREEN_HEIGHT = 32

    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        super().__init__(width, height)


class Keyboard(BooleanMatrix2D):
    KEYBOARD_WIDTH = 4
    KEYBOARD_HEIGHT = 4

    def __init__(self, width=KEYBOARD_WIDTH, height=KEYBOARD_HEIGHT):
        super().__init__(width, height)


class Emu:
    INSTRUCTION_SIZE = 2
    MEM_SIZE = 0x1000
    # STACK_DEPTH = 16
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
        quirk_vf_reset = True,
        quirk_memory = True,
        quirk_disp_wait = True,
        quirk_clipping = True,
        quirk_shifting = False,
        quirk_jumping = False,
    ):
        self.mem = bytearray(mem_size)
        self.mem[: self.START_ADDR] = self.FONT

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

        kwargs = {"opcode": opcode, "x": x, "y": y, "n": n, "nn": nn, "nnn": nnn}

        return Instr(**kwargs)


    def execute(self, instr: Instr):
        instr.eval(self)

    def tick(self):
        opcode = self.fetch()
        instr = self.decode(opcode)
        self.execute(instr)

    def __str__(self):
        acc = ""
        acc += self.screen
        acc += self.keyboard
        return acc

    def compose(self, *instrs: Instr):
        return Chain(*instrs)

    # def composed_execute(self, *instrs: Instr):
    #     self.compose(*instrs)(self)
    # for i in instrs: self.execute(i)


class EmuPreDecoded(Emu):
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
    
    def tick(self):
        pass