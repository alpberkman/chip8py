# from cpu import Emu
from random import randint

class OpcodeNotImplementedError(ValueError):
    def __init__(self, instr):
        super().__init__(f"Opcode {instr} not implemented")


# Base class
class Instr:
    def __init__(self, id, **kwargs):
        self.id = id
        self.kwargs = kwargs

    def exec(self, emu):
        raise OpcodeNotImplementedError(self)

    def __str__(self):
        return f"{self.__class__.__name__}({self.id}): {self.kwargs}"


# Classes that are used for organization
class SpecialInstr(Instr):
    pass


class AluInstr(Instr):
    pass


class LoadInstr(Instr):
    pass


class StoreInstr(Instr):
    pass


class KeyboardInstr(Instr):
    pass


class ScreenInstr(Instr):
    pass


class JumpInstr(Instr):
    pass


class Sys(Instr):
    def __init__(self, **kwargs):
        super().__init__("0NNN", **kwargs)

    def exec(self, emu):
        pass


class Cls(Instr):
    def __init__(self, **kwargs):
        super().__init__("00E0", **kwargs)

    def exec(self, emu):
        emu.screen.clear()


class Ret(Instr):
    def __init__(self, **kwargs):
        super().__init__("00EE", **kwargs)

    def exec(self, emu):
        emu.pc = emu.stack.pop()


class Jp1(Instr):
    def __init__(self, **kwargs):
        super().__init__("1NNN", **kwargs)

    def exec(self, emu):
        emu.pc = self.nnn


class Call(Instr):
    def __init__(self, **kwargs):
        super().__init__("2NNN", **kwargs)

    def exec(self, emu):
        emu.stack.append(emu.pc)
        emu.pc = self.nnn


class Se3(Instr):
    def __init__(self, **kwargs):
        super().__init__("3XNN", **kwargs)

    def exec(self, emu):
        if emu.v[self.x] == self.nn:
            emu.pc = (emu.pc + 2) & 0x0FFF


class Sne4(Instr):
    def __init__(self, **kwargs):
        super().__init__("4XNN", **kwargs)

    def exec(self, emu):
        if emu.v[self.x] != self.nn:
            emu.pc = (emu.pc + 2) & 0x0FFF


class Se5(Instr):
    def __init__(self, **kwargs):
        super().__init__("5XY0", **kwargs)

    def exec(self, emu):
        if emu.v[self.x] == emu.v[self.y]:
            emu.pc = (emu.pc + 2) & 0x0FFF


class Ld6(Instr):
    def __init__(self, **kwargs):
        super().__init__("6XNN", **kwargs)

    def exec(self, emu):
        emu.v[self.x] = self.nn


class Add7(Instr):
    def __init__(self, **kwargs):
        super().__init__("7XNN", **kwargs)

    def exec(self, emu):
        emu.v[self.x] += self.nn


class Ld8(Instr):
    def __init__(self, **kwargs):
        super().__init__("8XY0", **kwargs)

    def exec(self, emu):
        emu.v[self.x] = emu.v[self.y]


class Or(Instr):
    def __init__(self, **kwargs):
        super().__init__("8XY1", **kwargs)

    def exec(self, emu):
        emu.v[self.x] |= emu.v[self.y]


class And(Instr):
    def __init__(self, **kwargs):
        super().__init__("8XY2", **kwargs)

    def exec(self, emu):
        emu.v[self.x] &= emu.v[self.y]


class Xor(Instr):
    def __init__(self, **kwargs):
        super().__init__("8XY3", **kwargs)

    def exec(self, emu):
        emu.v[self.x] ^= emu.v[self.y]


class Add8(Instr):
    def __init__(self, **kwargs):
        super().__init__("8XY4", **kwargs)

    def exec(self, emu):
        emu.v[self.x] += emu.v[self.y]
        emu.v[0xF] = int(emu.v[self.x] < emu.v[self.x])


class Sub(Instr):
    def __init__(self, **kwargs):
        super().__init__("8XY5", **kwargs)

    def exec(self, emu):
        flag = int(emu.v[self.x] > emu.v[self.y])
        emu.v[self.x] -= emu.v[self.y]
        emu.v[0xF] = flag


class Shr(Instr):
    def __init__(self, **kwargs):
        super().__init__("8XY6", **kwargs)

    def exec(self, emu):
        emu.v[0xF] = emu.v[self.x] & 0x1
        emu.v[self.x] >>= 1


class Subn(Instr):
    def __init__(self, **kwargs):
        super().__init__("8XY7", **kwargs)

    def exec(self, emu):
        emu.v[0xF] = int(emu.v[self.x] <= emu.v[self.x])
        emu.v[self.x] = emu.v[self.y] - emu.v[self.x]


class Shl(Instr):
    def __init__(self, **kwargs):
        super().__init__("8XYE", **kwargs)

    def exec(self, emu):
        emu.v[0xF] = emu.v[self.x] >> 7
        emu.v[self.x] <<= 1


############################
class Sne9(Instr):
    def __init__(self, **kwargs):
        super().__init__("9XY0", **kwargs)

    def exec(self, emu):
        if emu.v[self.x] != emu.v[self.y]:
            emu.pc = (emu.pc + 2) & 0x0FFF


class LdA(Instr):
    def __init__(self, **kwargs):
        super().__init__("ANNN", **kwargs)

    def exec(self, emu):
        emu.i = self.nnn


class JpB(Instr):
    def __init__(self, **kwargs):
        super().__init__("BNNN", **kwargs)

    def exec(self, emu):
        emu.pc = (self.nnn + emu.v[0]) & 0x0FFF


class Rnd(Instr):
    def __init__(self, **kwargs):
        super().__init__("CXNN", **kwargs)

    def exec(self, emu):
        emu.v[self.x] = randint(0x00, 0xff) & self.nn

class Drw(Instr):
    def __init__(self, **kwargs):
        super().__init__("DXYN", **kwargs)


class Skp(Instr):
    def __init__(self, **kwargs):
        super().__init__("EX9E", **kwargs)


class Sknp(Instr):
    def __init__(self, **kwargs):
        super().__init__("EXA1", **kwargs)


class Lddt(Instr):
    def __init__(self, **kwargs):
        super().__init__("FX07", **kwargs)


class Getk(Instr):
    def __init__(self, **kwargs):
        super().__init__("FX0A", **kwargs)


class Strdt(Instr):
    def __init__(self, **kwargs):
        super().__init__("FX15", **kwargs)


class Strst(Instr):
    def __init__(self, **kwargs):
        super().__init__("FX18", **kwargs)


class Addi(Instr):
    def __init__(self, **kwargs):
        super().__init__("FX1E", **kwargs)


class Ldi(Instr):
    def __init__(self, **kwargs):
        super().__init__("FX29", **kwargs)


class Bcd(Instr):
    def __init__(self, **kwargs):
        super().__init__("FX33", **kwargs)


class Save(Instr):
    def __init__(self, **kwargs):
        super().__init__("FX55", **kwargs)


class Load(Instr):
    def __init__(self, **kwargs):
        super().__init__("FX65", **kwargs)
