from functools import reduce
from random import randint


class OpcodeNotImplementedError(ValueError):
    def __init__(self, instr):
        super().__init__(f"Opcode {instr} not implemented")


class OpcodeTypeError(TypeError):
    def __init__(self, opcode):
        super().__init__(f"Opcode {opcode} cannot be converted to an Instruction")


# Base class
class Instr:
    id = None
    name = "BASE"

    def __init__(self, opcode: int, **kwargs):
        self.opcode = opcode

    def eval(self, emu):
        raise OpcodeNotImplementedError(self)

    def __call__(self, emu):
        self.eval(emu)
        return emu

    def __str__(self):
        l = [f"{self.name+':':4}"]

        if self.id is not None:
            l.append(f"[{self.id}|{hex(self.opcode)}]")

        for arg in ["x", "y", "n", "nn", "nnn"]:
            if arg in vars(self):
                l.append(f"{arg.upper()}: {self.__dict__[arg]}")

        return " ".join(l)


class Chain(Instr):
    id = None
    name = "CHN"
    seperator = "  "

    def __init__(self, *instrs: Instr, **kwargs):
        super().__init__(None, **kwargs)
        self.instrs = instrs

    def eval(self, emu):
        if self.instrs:
            return reduce(lambda acc, instr: instr(acc), self.instrs, emu)

    def __str__(self, depth: int = 0):
        lines = [f"{self.seperator * depth}{self.name}:"]

        for instr in self.instrs:
            if isinstance(instr, Chain):
                lines.append(instr.__str__(depth + 1))
            else:
                lines.append(f"{self.seperator * (depth + 1)}{instr}")

        return "\n".join(lines)


class Dud(Instr):
    id = None
    name = "DMY"

    def __init__(
        self, opcode: int, x: int, y: int, n: int, nn: int, nnn: int, **kwargs
    ):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.y = y
        self.n = n
        self.nn = nn
        self.nnn = nnn

    def eval(self, emu):
        pass


class Ix00E0(Instr):
    id = "00E0"
    name = "CLS"

    def eval(self, emu):
        emu.scr.clear()
        emu.dirty = 1


class Ix00EE(Instr):
    id = "00EE"
    name = "RET"

    def eval(self, emu):
        emu.pc = emu.stack.pop()


class Ix1NNN(Instr):
    id = "1NNN"
    name = "JP"

    def __init__(self, opcode: int, nnn: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.nnn = nnn

    def eval(self, emu):
        emu.pc = self.nnn


class Ix2NNN(Instr):
    id = "2NNN"
    name = "CALL"

    def __init__(self, opcode: int, nnn: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.nnn = nnn

    def eval(self, emu):
        emu.stack.append(emu.pc)
        emu.pc = self.nnn


class Ix3XNN(Instr):
    id = "3XNN"
    name = "SE"

    def __init__(self, opcode: int, x: int, nn: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.nn = nn

    def eval(self, emu):
        if emu.v[self.x] == self.nn:
            emu.next()


class Ix4XNN(Instr):
    id = "4XNN"
    name = "SNE"

    def __init__(self, opcode: int, x: int, nn: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.nn = nn

    def eval(self, emu):
        if emu.v[self.x] != self.nn:
            emu.next()


class Ix5XY0(Instr):
    id = "5XY0"
    name = "SE"

    def __init__(self, opcode: int, x: int, y: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.y = y

    def eval(self, emu):
        if emu.v[self.x] == emu.v[self.y]:
            emu.next()


class Ix6XNN(Instr):
    id = "6XNN"
    name = "LD"

    def __init__(self, opcode: int, x: int, nn: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.nn = nn

    def eval(self, emu):
        emu.v[self.x] = self.nn


class Ix7XNN(Instr):
    id = "7XNN"
    name = "ADD"

    def __init__(self, opcode: int, x: int, nn: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.nn = nn

    def eval(self, emu):
        emu.v[self.x] = (emu.v[self.x] + self.nn) & 0xFF


class Ix8XY0(Instr):
    id = "8XY0"
    name = "LD"

    def __init__(self, opcode: int, x: int, y: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.y = y

    def eval(self, emu):
        emu.v[self.x] = emu.v[self.y]


class Ix8XY1(Instr):
    id = "8XY1"
    name = "OR"

    def __init__(self, opcode: int, x: int, y: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.y = y

    def eval(self, emu):
        emu.v[self.x] |= emu.v[self.y]
        if emu.quirk_vf_reset:
            emu.v[0xF] = 0


class Ix8XY2(Instr):
    id = "8XY2"
    name = "AND"

    def __init__(self, opcode: int, x: int, y: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.y = y

    def eval(self, emu):
        emu.v[self.x] &= emu.v[self.y]
        if emu.quirk_vf_reset:
            emu.v[0xF] = 0


class Ix8XY3(Instr):
    id = "8XY3"
    name = "XOR"

    def __init__(self, opcode: int, x: int, y: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.y = y

    def eval(self, emu):
        emu.v[self.x] ^= emu.v[self.y]
        if emu.quirk_vf_reset:
            emu.v[0xF] = 0


class Ix8XY4(Instr):
    id = "8XY4"
    name = "ADD"

    def __init__(self, opcode: int, x: int, y: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.y = y

    def eval(self, emu):
        emu.v[self.x] = (emu.v[self.x] + emu.v[self.y]) & 0xFF
        emu.v[0xF] = emu.v[self.x] < emu.v[self.y]


class Ix8XY5(Instr):
    id = "8XY5"
    name = "SUB"

    def __init__(self, opcode: int, x: int, y: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.y = y

    def eval(self, emu):
        flag = emu.v[self.x] >= emu.v[self.y]
        emu.v[self.x] = (emu.v[self.x] - emu.v[self.y]) & 0xFF
        emu.v[0xF] = flag


class Ix8XY6(Instr):
    id = "8XY6"
    name = "SHR"

    def __init__(self, opcode: int, x: int, y: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.y = y

    def eval(self, emu):
        if not emu.quirk_shift:
            emu.v[self.x] = emu.v[self.y]
        flag = emu.v[self.x] & 0x1
        emu.v[self.x] >>= 0x1
        emu.v[0xF] = flag


class Ix8XY7(Instr):
    id = "8XY7"
    name = "SUBN"

    def __init__(self, opcode: int, x: int, y: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.y = y

    def eval(self, emu):
        flag = emu.v[self.y] >= emu.v[self.x]
        emu.v[self.x] = (emu.v[self.y] - emu.v[self.x]) & 0xFF
        emu.v[0xF] = flag


class Ix8XYE(Instr):
    id = "8XYE"
    name = "SHL"

    def __init__(self, opcode: int, x: int, y: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.y = y

    def eval(self, emu):
        if not emu.quirk_shift:
            emu.v[self.x] = emu.v[self.y]
        flag = emu.v[self.x] >> 0x7
        emu.v[self.x] = (emu.v[self.x] << 0x1) & 0xFF
        emu.v[0xF] = flag


class Ix9XY0(Instr):
    id = "9XY0"
    name = "SNE"

    def __init__(self, opcode: int, x: int, y: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.y = y

    def eval(self, emu):
        if emu.v[self.x] != emu.v[self.y]:
            emu.next()


class IxANNN(Instr):
    id = "ANNN"
    name = "LD"

    def __init__(self, opcode: int, nnn: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.nnn = nnn

    def eval(self, emu):
        emu.i = self.nnn


class IxBNNN(Instr):
    id = "BNNN"
    name = "JP"

    def __init__(self, opcode: int, x: int, nnn: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.nnn = nnn

    def eval(self, emu):
        if emu.quirk_jumping:
            emu.pc = self.nnn + emu.v[self.x]
        else:
            emu.pc = self.nnn + emu.v[0x0]


class IxCXNN(Instr):
    id = "CXNN"
    name = "RND"

    def __init__(self, opcode: int, x: int, nn: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.nn = nn

    def eval(self, emu):
        emu.v[self.x] = self.nn & randint(0, 255)


class IxDXYN(Instr):
    id = "DXYN"
    name = "DRW"

    def __init__(self, opcode: int, x: int, y: int, n: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.y = y
        self.n = n

    def eval(self, emu):
        emu.scr.draw(emu, self.x, self.y, self.n)
        emu.dirty = 1


class IxEX9E(Instr):
    id = "EX9E"
    name = "SKP"

    def __init__(self, opcode: int, x: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x

    def eval(self, emu):
        if emu.kbd[emu.v[self.x]] & 0x1:
            emu.next()


class IxEXA1(Instr):
    id = "EXA1"
    name = "SKNP"

    def __init__(self, opcode: int, x: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x

    def eval(self, emu):
        if not emu.kbd[emu.v[self.x]] & 0x1:
            emu.next()


########################################################


class IxFX07(Instr):
    id = "FX07"
    name = "LD"

    def __init__(self, opcode: int, x: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x

    def eval(self, emu):
        emu.v[self.x] = emu.dt


class IxFX0A(Instr):
    id = "FX0A"
    name = "LD"

    def __init__(self, opcode: int, x: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x

    def eval(self, emu):
        if emu.kbd:
            emu.v[self.x] = next(
                (i for i in range(len(emu.kbd)) if (emu.kbd >> i) & 0x1), 0
            )
            emu.release = 1
            emu.unnext()
        else:
            if emu.release:
                emu.release = 0
            else:
                emu.unnext()


class IxFX15(Instr):
    id = "FX15"
    name = "LD"

    def __init__(self, opcode: int, x: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x

    def eval(self, emu):
        emu.dt = emu.v[self.x]


class IxFX18(Instr):
    id = "FX18"
    name = "LD"

    def __init__(self, opcode: int, x: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x

    def eval(self, emu):
        emu.st = emu.v[self.x]


class IxFX1E(Instr):
    id = "FX1E"
    name = "ADD"

    def __init__(self, opcode: int, x: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x

    def eval(self, emu):
        emu.i += emu.v[self.x]


class IxFX29(Instr):
    id = "FX29"
    name = "LD"

    def __init__(self, opcode: int, x: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x

    def eval(self, emu):
        emu.i = emu.v[self.x] * 5


class IxFX33(Instr):
    id = "FX33"
    name = "LD"

    def __init__(self, opcode: int, x: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x

    def eval(self, emu):
        emu.mem[emu.i + 0] = emu.v[self.x] // 100
        emu.mem[emu.i + 1] = emu.v[self.x] // 10 % 10
        emu.mem[emu.i + 2] = emu.v[self.x] % 10


class IxFX55(Instr):
    id = "FX55"
    name = "LD"

    def __init__(self, opcode: int, x: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x

    def eval(self, emu):
        for i in range(self.x + 1):
            emu.mem[emu.i + i] = emu.v[i]
        if emu.quirk_memory:
            emu.i += self.x + 1


class IxFX65(Instr):
    id = "FX65"
    name = "LD"

    def __init__(self, opcode: int, x: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x

    def eval(self, emu):
        for i in range(self.x + 1):
            emu.v[i] = emu.mem[emu.i + i]
        if emu.quirk_memory:
            emu.i += self.x + 1


def match(opcode: int | str):
    import re

    if isinstance(opcode, int):
        opcode_str = f"{opcode:04X}"
    elif isinstance(opcode, str):
        opcode_str = opcode.strip().upper().lstrip("0X")
    else:
        raise OpcodeTypeError(opcode)

    for cls in Instr.__subclasses__():
        pattern = getattr(cls, "id", None)
        if not pattern:
            continue

        regex = "^" + re.sub(r"[NXY]", ".", pattern) + "$"
        if re.match(regex, opcode_str):
            return cls

    return Instr
