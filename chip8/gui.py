import pygame

KEY_MAP = {
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_4: 0xC,
    pygame.K_q: 0x4,
    pygame.K_w: 0x5,
    pygame.K_e: 0x6,
    pygame.K_r: 0xD,
    pygame.K_a: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_f: 0xE,
    pygame.K_z: 0xA,
    pygame.K_x: 0x0,
    pygame.K_c: 0xB,
    pygame.K_v: 0xF,
}

def set_key_bit(kbd, key_num, down):
    """Set or clear a key bit in the 2-byte keyboard buffer."""
    byte = key_num // 8
    bit = key_num % 8
    if down:
        kbd[byte] |= (1 << bit)
    else:
        kbd[byte] &= ~(1 << bit)

def draw_screen(surface, emu, scale):
    """Render the packed 64x32 buffer to the pygame surface."""
    scr = emu.scr
    width = scr.width
    height = scr.height
    bpr = width // 8  # bytes per row

    # Clear surface
    surface.fill((0, 0, 0))

    # For each row and byte, paint 8 pixels left-to-right (bit7 to bit0)
    for y in range(height):
        base = y * bpr
        for bx in range(bpr):
            byte = scr[base + bx]
            # bit7 is leftmost within this byte
            for px in range(8):
                if byte & (1 << (7 - px)):
                    x = bx * 8 + px
                    pygame.draw.rect(
                        surface,
                        (255, 255, 255),
                        (x * scale, y * scale, scale, scale),
                    )

def make_square_wave(freq=44100, duration=0.1, volume=0.2, sample_rate=44100):
    """Create a short square-wave buffer and return a pygame Sound."""
    from array import array
    n = int(duration * sample_rate)
    period = sample_rate / float(freq)
    amp = int(32767 * max(0.0, min(1.0, volume)))
    buf = array('h')
    for i in range(n):
        s = amp if (i % period) < (period / 2) else -amp
        buf.append(int(s))
    return pygame.mixer.Sound(buffer=buf.tobytes())

def main(args):
    pygame.init()
    pygame.display.set_caption("CHIP-8")
    pygame.mixer.pre_init(frequency=44100, size=8, channels=1, buffer=2048)
    clock = pygame.time.Clock()

    if args.emu_type.lower() in ["basic", "b"]:
        from chip8.emulator import EmuInterpreter as Emu
    elif args.emu_type.lower() in ["predecoded", "pd"]:
        from chip8.emulator import EmuPreDecoded as Emu
    elif args.emu_type.lower() in ["basicblock", "bb"]:
        from chip8.emulator import EmuBasicBlock as Emu
    else:
        from chip8.emulator import EmuPreDecoded as Emu

    emu = Emu(args.rom, debug=args.debug)

    beep_sound = make_square_wave(freq=880, duration=0.1, volume=0.2)
    beeping = False

    # Create window
    w = emu.scr.width * args.scale
    h = emu.scr.height * args.scale
    screen = pygame.display.set_mode((w, h))

    running = True
    while running:
        # Input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key in KEY_MAP:
                    set_key_bit(emu.kbd, KEY_MAP[event.key], True)

            elif event.type == pygame.KEYUP:
                if event.key in KEY_MAP:
                    set_key_bit(emu.kbd, KEY_MAP[event.key], False)

        # Execute one interpreter tick (fetch-decode-execute + timer cadence)
        emu.tick()

        st = emu.st
        if st > 0 and not beeping:
            beep_sound.play(loops=-1)  # loop indefinitely
            beeping = True
        elif st == 0 and beeping:
            beep_sound.stop()
            beeping = False

        # Redraw only if something changed the display
        if emu.dirty:
            draw_screen(screen, emu, args.scale)
            pygame.display.flip()
            emu.dirty = 0

        # Pace to desired instruction frequency
        clock.tick(args.fps)

    pygame.quit()

