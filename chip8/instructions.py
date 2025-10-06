
from functools import reduce


class OpcodeNotImplementedError(ValueError):
    def __init__(self, instr):
        super().__init__(f"Opcode {instr} not implemented")


# Base class
class Instr:
    id = None
    name = None

    def __init__(self, opcode, **kwargs):
        self.opcode = opcode

    def eval(self, emu):
        raise OpcodeNotImplementedError(self)
        return emu

    def __str__(self):
        return f"{self.id}({self.name}): {self.kwargs}"
    
class Chain(Instr):
    id = None
    name = "CHN"
    def __init__(self, *instrs: Instr):
        self.instrs = instrs

    def eval(self, emu):
        return reduce(lambda acc, instr: instr.eval(acc), self.instrs, emu)


class Ix00E0(Instr):
    id = "00E0"
    name = "CLS"

    def __init__(self, opcode, **kwargs):
        super().__init__(opcode, **kwargs)

    def eval(self, emu):
        emu.screen.clear()
        return emu


class Ix00EE(Instr):
    id = "00EE"
    name = "RET"

    def __init__(self, opcode, **kwargs):
        super().__init__(opcode, **kwargs)

    def eval(self, emu):
        emu.pc = emu.stack.pop()
        return emu


class Ix1NNN(Instr):
    id = "1NNN"
    name = "JP"

    def __init__(self, opcode, nnn, **kwargs):
        super().__init__(opcode, **kwargs)
        self.nnn = nnn

    def eval(self, emu):
        emu.pc = self.nnn
        return emu


class Ix2NNN(Instr):
    id = "2NNN"
    name = "CALL"

    def __init__(self, opcode, nnn, **kwargs):
        super().__init__(opcode, **kwargs)
        self.nnn = nnn

    def eval(self, emu):
        emu.stack.append(emu.pc)
        emu.pc = self.nnn
        return emu

#Instr.__subclasses__()[0].id