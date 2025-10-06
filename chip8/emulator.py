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
    MEM_SIZE = 0x1000
    # STACK_DEPTH = 16

    def __init__(self, mem_size=MEM_SIZE):
        self.mem = bytearray(mem_size)

        self.pc = 0x200

        self.v = bytearray(16)
        self.i = 0x0

        self.stack = []  # [0] * self.STACK_DEPTH
        # self.sp = 0

        self.delay_timer = 0
        self.sound_timer = 0

        self.keyboard = Keyboard()
        self.screen = Screen()

    def next(self):
        self.pc = (self.pc + 2) & 0x0FFF

    def unnext(self):
        self.pc = (self.pc - 2) & 0x0FFF

    def fetch(self) -> int:
        opcode = int.from_bytes(self.mem[self.pc : self.pc + 2], byteorder="big")
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

        # lut = {
        #     0x0000: {0x00E0: Cls(), 0x00EE: Ret()}[nnn],
        #     0x1000: Jp1(nnn=nnn),
        #     0x2000: Call(nnn=nnn),
        #     0x3000: Se3(x=x, nn=nn),
        #     0x4000: Sne4(x=x, nn=nn),
        #     0x5000: Se5(x=x, y=y),
        #     0x6000: Ld6(x=x, nn=nn),
        #     0x7000: Add7(x=x, nn=nn),
        #     0x8000: {
        #         0x0: Ld8(x=x, y=y),
        #         0x1: Or(x=x, y=y),
        #         0x2: And(x=x, y=y),
        #         0x3: Xor(x=x, y=y),
        #         0x4: Add8(x=x, y=y),
        #         0x5: Sub(x=x, y=y),
        #         0x6: Shr(x=x, y=y),
        #         0x7: Subn(x=x, y=y),
        #         0xE: Shl(x=x, y=y),
        #     }[n],
        #     0x9000: Sne9(x=x, y=y),
        #     0xA000: LdA(nnn=nnn),
        #     0xB000: JpB(nnn=nnn),
        #     0xC000: Rnd(x=x, nn=nn),
        #     0xD000: Drw(x=x, y=y, n=n),
        #     0xE000: {0x9E: Skp(x=x), 0xA1: Sknp(x=x)}[nn],
        #     0xF000: {
        #         0x07: Lddt(x=x),
        #         0x0A: Getk(x=x),
        #         0x15: Strdt(x=x),
        #         0x18: Strst(x=x),
        #         0x1E: Addi(x=x),
        #         0x29: Ldi(x=x),
        #         0x33: Bcd(x=x),
        #         0x55: Save(x=x),
        #         0x65: Load(x=x),
        #     }[nn],
        # }

        # return lut[ival & 0xF000]

    def execute(self, instr: Instr):
        instr(self)

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


x = Sys(N=123, X=23)
print(x)
