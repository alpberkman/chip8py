class ByteArrayExtended(bytearray):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.size = width * height // 8
        super().__init__(self.size)

    def clear(self):
        for i in range(self.size):
            self[i] = 0

    def __str__(self):
        acc = ""
        acc += "*" * (self.width + 2)
        acc += "\n*"
        for i in range(self.size):
            if i != 0 and i % 8 == 0:
                acc += "*\n*"

            bytei = self[i]
            for bit in range(7, -1, -1):
                if bytei & (1 << bit):
                    acc += "#"
                else:
                    acc += " "

        acc += "*\n"
        acc += "*" * (self.width + 2)
        return acc


class Screen(ByteArrayExtended):
    SCREEN_WIDTH = 64
    SCREEN_HEIGHT = 32

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        super().__init__(width=width, height=height)

    def draw(self, emu, x: int, y: int, n: int):
        if emu.quirk_disp_wait:
            if emu.it:
                emu.unnext()
                return
            else:
                emu.it = 1

        xx = emu.v[x] % self.width
        yy = emu.v[y] % self.height
        emu.v[0xF] = 0

        if emu.quirk_clipping:
            if yy + n > self.height:
                n = self.height - yy

        for i in range(n):
            bytei = emu.mem[emu.i + i]
            xxiu = xx // 8
            xxil = (xx + 8) % self.width // 8
            yyi = (yy + i) % self.height

            upper = (bytei >> (xx % 8)) & 0xFF
            baseu = xxiu + self.width // 8 * yyi

            if self[baseu] & upper:
                emu.v[0xF] = 1

            self[baseu] ^= upper

            if not emu.quirk_clipping or xxil > xxiu:
                lower = (bytei << (8 - (xx % 8))) & 0xFF
                basel = xxil + self.width // 8 * yyi

                if self[basel] & lower:
                    emu.v[0xF] = 1

                self[basel] ^= lower


class Keyboard(ByteArrayExtended):
    KEYBOARD_WIDTH = 4
    KEYBOARD_HEIGHT = 4

    def __init__(self, width: int = KEYBOARD_WIDTH, height: int = KEYBOARD_HEIGHT):
        super().__init__(width=width, height=height)

    def mask(self) -> int:
        return int(self[0]) | (int(self[1]) << 8)
