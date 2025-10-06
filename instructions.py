class OpcodeNotImplementedError(ValueError):
    def __init__(self, instr):
        super().__init__(f"Opcode {instr} not implemented")


# Base class
class Instr:
    id = None
    name = None

    def __init__(self, **kwargs):
        pass

    def exec(self, emu):
        raise OpcodeNotImplementedError(self)

    def __str__(self):
        return f"{self.__class__.__name__}({self.id}): {self.kwargs}"


class Ix00E0(Instr):
    id = "00E0"
    name = "CLS"

    def __init__(self, **kwargs):
        # super().__init__("00E0", "CLS")
        pass

    def exec(self, emu):
        emu.screen.clear()


class Ix00EE(Instr):
    id = "00EE"
    name = "RET"

    def __init__(self, **kwargs):
        # super().__init__("00EE", "RET")
        pass

    def exec(self, emu):
        emu.pc = emu.stack.pop()


class Ix1NNN(Instr):
    id = "1NNN"
    name = "JP"

    def __init__(self, nnn, **kwargs):
        # super().__init__("1NNN", "JP")
        self.nnn = nnn

    def exec(self, emu):
        emu.pc = self.nnn


class Ix2NNN(Instr):
    id = "2NNN"
    name = "CALL"

    def __init__(self, nnn, **kwargs):
        # super().__init__("2NNN", "CALL")
        self.nnn = nnn

    def exec(self, emu):
        emu.stack.append(emu.pc)
        emu.pc = self.nnn

#Instr.__subclasses__()[0].id