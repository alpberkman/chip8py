from functools import reduce


class OpcodeNotImplementedError(ValueError):
    def __init__(self, instr):
        super().__init__(f"Opcode {instr} not implemented")


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
        emu.screen.clear()


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
        emu.v[self.x] += self.nn
        

class Ix8XY0(Instr):
    id = "8XY0"
    name = "LD"

    def __init__(self, opcode: int, x: int, y: int, **kwargs):
        super().__init__(opcode, **kwargs)
        self.x = x
        self.y = y

    def eval(self, emu):
        emu.v[self.x] = emu.v[self.y]

# Instr.__subclasses__()[0].id
