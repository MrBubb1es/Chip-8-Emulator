"""
Really helpful website:
    http://multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/
"""
from config import *
from Chip8Helper import *
import numpy as np
import random

class Chip8:
    def __init__(self):
        # Unsigned short
        self.opcode = np.uint16(0)
        # Registers
        self.V = np.array([0] * 16, dtype=np.uint8)
        # Index register
        self.I = np.uint16(0)
        # Program counter to keep track of the current instruction in memory
        self.pc = np.uint16(0x200)

        # 4096 unsigned chars
        # 0x000-0x1FF - Chip 8 interpreter (contains font set in emu)
        # 0x050-0x0A0 - Used for the built in 4x5 pixel font set (0-F)
        # 0x200-0xFFF - Program ROM and work RAM
        self.memory = np.array([0] * 4096, dtype=np.uint8)

        # Graphics array
        self.gfx = np.array([1] * (64 * 32))

        # Timers that count down at 60hz
        self.delay_timer = np.uint8(0)
        self.sound_timer = np.uint8(0)

        # Original Chip8 stack size was 16,
        # but we increased it for funsies
        self.stack = np.array([0] * 256, dtype=np.uint16)
        # Stack pointer to keep track of the level of the stack
        self.sp = np.uint16(0)

        # key array used to keep track of the current state of the keyboard
        self.key = np.array([0] * 16, dtype=np.uint8)

        # Used to determine whether to draw to the screen or not
        self.draw_screen = False

        # Opcode jump tables
        self.opcode_dict = {}
        self.opcode_zeros = {}
        self.opcode_eights = {}
        self.opcode_Es = {}
        self.opcode_Fs = {}

    """
    Full list of opcodes and their functionalities found here:
    https://en.wikipedia.org/wiki/CHIP-8
    """

    def loadFontset(self):
        # Copy fontset into memory starting at 0x50 and ending at 0xA0
        self.memory[0x50 : 0xA0] = FONTSET[0x0 : 0x50]

    def loadProgram(self):
        # Read the bytes from PROGRAM_FILE and write them to the memory array
        self.memory[0x200 : (0x200 + len(PROGRAM_BIN))] = PROGRAM_BIN

    # 00E0 - Clear screen
    def CLS(self):
        # Fill array with 0s
        self.gfx.fill(0)

        # Indicate that the screen should be drawn
        self.draw_screen = True

        # Increment program counter
        self.pc += 2

    # 00EE - Return from subroutine
    def RETURN(self):
        # Set the pc to the location on the top of the stack and decrement the sp
        self.pc = self.stack[self.sp]
        self.sp -= 1

    # 1NNN - Jumps to address NNN
    def JUMP(self):
        NNN = (self.opcode & 0x0FFF)
        self.pc = NNN

    # 2NNN - Calls subroutine at NNN
    def CALL(self):
        NNN = (self.opcode & 0x0FFF)
        # Add this location to stack
        self.sp += 1
        self.stack[self.sp] = self.pc + 2

        # Jump to new location
        self.pc = NNN

    # 3XNN - Skips the next instruction if VX equals NN
    def REQC(self):
        X = (self.opcode & 0x0F00) >> 8
        NN = (self.opcode & 0x00FF)

        # If register == nn
        if self.V[X] == NN:
            # Skip next instruction
            self.pc += 4
        else:
            # Continue normally
            self.pc += 2

    # 4XNN - Skips the next instruction if VX doesn't equal NN
    def RNEQC(self):
        X = (self.opcode & 0x0F00) >> 8
        NN = (self.opcode & 0x00FF)

        if self.V[X] != NN:
            self.pc += 4
        else:
            self.pc += 2

    # 5XY0 - Skips the next instruction if VX equals VY
    def REQR(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4

        if self.V[X] == self.V[Y]:
            self.pc += 4
        else:
            self.pc += 2

    # 6XNN - Sets VX to NN
    def SETRC(self):
        X = (self.opcode & 0x0F00) >> 8
        NN = (self.opcode & 0x00FF)

        self.V[X] = NN

        self.pc += 2

    # 7XNN - Adds NN to VX
    def ADDRC(self):
        X = (self.opcode & 0x0F00) >> 8
        NN = (self.opcode & 0x00FF)

        old_vx = self.V[X]

        self.V[X] += NN

        self.pc += 2

    # 8XY0 - Sets VX to the value of VY
    def SETRR(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4

        self.V[X] = self.V[Y]

        self.pc += 2

    # 8XY1 - Sets VX to VX or VY. (Bitwise OR operation)
    def OR(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4

        # Bitwise OR
        self.V[X] = self.V[X] | self.V[Y]

        self.pc += 2

    # 8XY2 - Sets VX to VX and VY. (Bitwise AND operation)
    def AND(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4

        # Bitwise AND
        self.V[X] = self.V[X] & self.V[Y]

        self.pc += 2

    # 8XY3 - Sets VX to VX xor VY
    def XOR(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4

        # Bitwise XOR
        self.V[X] = self.V[X] ^ self.V[Y]

        self.pc += 2

    # 8XY4 - Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there isn't
    def ADDREG(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4

        # Set V[F] to the 9th bit (carry bit)
        self.V[0xF] = (self.V[X] + self.V[Y]) >> 8

        self.V[X] += self.V[Y]

        self.pc += 2

    # 8XY5 - VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there isn't
    def SUBREG(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4

        # When V[Y] > V[X], there is a borrow
        if (self.V[Y] > self.V[X]):
            self.V[0xF] = 0
        else:
            self.V[0xF] = 1

        self.V[X] -= self.V[Y]

        self.pc += 2

    # 8XY6 - Stores the least significant bit of VX in VF and then shifts VX to the right by 1
    def SHFR(self):
        X = (self.opcode & 0x0F00) >> 8
        #Y = (self.opcode & 0x00F0) >> 4

        self.V[0xF] = (self.V[X] & 0x0001)
        self.V[X] >>= 1

        self.pc += 2

    # 8XY7 - Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there isn't
    def SUBYX(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4

        if (self.V[X] > self.V[Y]):
            self.V[0xF] = 0
        else:
            self.V[0xF] = 1

        self.V[X] = (self.V[Y] - self.V[X]) & 0xFFFF

        self.pc += 2

    # 8XYE - Stores the most significant bit of VX in VF and then shifts VX to the left by 1
    def SHFL(self):
        X = (self.opcode & 0x0F00) >> 8
        #Y = (self.opcode & 0x00F0) >> 4

        # 0x80 -> Most significant bit 1000 0000
        self.V[0xF] = self.V[X] & 0x80
        self.V[X] <<= 1

        self.pc += 2

    # 9XY0 - Skips the next instruction if VX doesn't equal VY
    def RNEQR(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4

        if (self.V[X] != self.V[Y]):
          self.pc += 4
        else:
          self.pc += 2

    # ANNN - Sets I to the address NNN
    def SETI(self):
        NNN = (self.opcode & 0x0FFF)

        self.I = NNN

        self.pc += 2

    # BNNN - Jumps to the address NNN plus V0
    def JUMPOFFSET(self):
        NNN = (self.opcode & 0x0FFF)

        self.pc = NNN + self.V[0]


    # CXNN - Sets VX to the result of a bitwise and operation on a random number (Typically: 0 to 255) and NN.
    def RAND(self):
        X = (self.opcode & 0x0F00) >> 8
        NN = (self.opcode & 0x00FF)

        self.V[X] = (random.randint(0,255) & NN)

        self.pc += 2

    # DXYN - Draw (see link for more)
    def DRAW(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4
        N = (self.opcode & 0x000F)

        flipped = 0

        # Height of N pixels
        for y in range(N):
            # Staring at mem location I, go through the pixels row by row
            pixel_row = self.memory[self.I + y]

            # Width of 8
            for x in range(8):
                # Get the location of the pixel in gfx array
                pixel_location = (self.V[Y] + y) * 64 + (self.V[X] + x)

                # Make sure the location is within the bounds of the array
                if (pixel_location > 0 and pixel_location < 2048):
                    # Place a mask over the pixel row to show only 1 pixel at a time
                    # Iter 0 mask: 1000 0000
                    # Iter 1 mask: 0100 0000
                    # Iter 2 mask: 0010 0000 etc.
                    current_pixel = pixel_row & (0x80 >> x)

                    if (current_pixel != 0):
                        # If the pixel was already on
                        if (self.gfx[pixel_location] == 1):
                            flipped = 1

                        # XOR to get the new pixel on/off value
                        self.gfx[pixel_location] ^= 1

        # Set V[F] to 1 if a pixel was turned from on to off, 0 if that didn't happen
        self.V[0xF] = flipped

        self.draw_screen = True

        self.pc += 2

    # EX9E - Skips the next instruction if the key stored in VX is pressed
    def KEYPRESSED(self):
        X = (self.opcode & 0x0F00) >> 8

        # Update keyboard state
        self.key = getKeyState()

        if (self.key[self.V[X]] == 1):
            self.pc += 4
        else:
            self.pc += 2


    # EXA1 - Skips the next instruction if the key stored in VX isn't pressed
    def KEYNOTPRESSED(self):
        X = (self.opcode & 0x0F00) >> 8

        self.key = getKeyState()

        if (self.key[self.V[X]] != 1):
            self.pc += 4
        else:
            self.pc += 2

    # FX07 - Sets VX to the value of the delay timer
    def GETTIMER(self):
        X = (self.opcode & 0x0F00) >> 8

        self.V[X] = self.delay_timer

        self.pc += 2


    # FX0A - A key press is awaited, and then stored in VX
    def WAITFORKEY(self):
        X = (self.opcode & 0x0F00) >> 8

        # Function in Chip8Helper
        self.V[X] = waitForKeypress()

        self.pc += 2

    # FX15 - Sets the delay timer to VX
    def SETDELAY(self):
        X = (self.opcode & 0x0F00) >> 8

        self.delay_timer = self.V[X]

        self.pc += 2

    # FX18 - Sets the sound timer to VX
    def SETSOUND(self):
        X = (self.opcode & 0x0F00) >> 8

        self.sound_timer = self.V[X]

        self.pc += 2

    # FX1E - Adds VX to I. VF is not affected
    def ADDRI(self):
        X = (self.opcode & 0x0F00) >> 8

        self.I += self.V[X]

        self.pc += 2

    # FX29 - Sets I to the location of the sprite for the character in VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font
    def GETFONT(self):
        X = (self.opcode & 0x0F00) >> 8

        # 0x50 is where the font is loaded into memory
        # 5 is the width of a single character
        self.I = 5 * self.V[X] + 0x50

        self.pc += 2

    # FX33 - BCD (see link for more)
    def BCD(self):
        X = (self.opcode & 0x0F00) >> 8

        # Go through digit by digit of V[X], and store each digit in a subsequent memory location
        # For example: 255 -> 0010 0101 0101 -> memory[I], memory[I+1], memory[I+2]
        self.memory[self.I] = self.V[X] // 100
        self.memory[self.I + 1] = (self.V[X] % 100) // 10
        self.memory[self.I + 2] = (self.V[X] % 100) % 10

        self.pc += 2

    # FX55 - Stores V0 to VX (including VX) in memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified
    def WRITE(self):
        X = (self.opcode & 0x0F00) >> 8
        # Add 1 to X for splicing to work properly
        X += 1

        # Copy a section of the Register array to memory
        self.memory[self.I : (self.I+X)] = self.V[0 : X]

        self.pc += 2


    # FX65 - Fills V0 to VX (including VX) with values from memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified
    def READ(self):
        X = (self.opcode & 0x0F00) >> 8
        X += 1

        self.V[0 : X] = self.memory[self.I : (self.I + X)]

        self.pc += 2


    def populateZeros(self):
        self.opcode_zeros = {
            0x0000 : self.CLS,
            0x000E : self.RETURN
        }

    def populateEights(self):
        self.opcode_eights = {
            0x0000 : self.SETRR,
            0x0001 : self.OR,
            0x0002 : self.AND,
            0x0003 : self.XOR,
            0x0004 : self.ADDREG,
            0x0005 : self.SUBREG,
            0x0006 : self.SHFR,
            0x0007 : self.SUBYX,
            0x000E : self.SHFL
        }

    def populateEs(self):
        self.opcode_Es = {
            0x000E : self.KEYPRESSED,
            0x0001 : self.KEYNOTPRESSED
        }

    def populateFs(self):
        self.opcode_Fs = {
            0x0007 : self.GETTIMER,
            0x000A : self.WAITFORKEY,
            0x0015 : self.SETDELAY,
            0x0018 : self.SETSOUND,
            0x001E : self.ADDRI,
            0x0029 : self.GETFONT,
            0x0033 : self.BCD,
            0x0055 : self.WRITE,
            0x0065 : self.READ
        }

    def populateOpcodeDict(self):
        self.opcode_dict = {
            0x0000 : self.startsWith0,
            0x1000 : self.JUMP,
            0x2000 : self.CALL,
            0x3000 : self.REQC,
            0x4000 : self.RNEQC,
            0x5000 : self.REQR,
            0x6000 : self.SETRC,
            0x7000 : self.ADDRC,
            0x8000 : self.startsWith8,
            0x9000 : self.RNEQR,
            0xA000 : self.SETI,
            0xB000 : self.JUMPOFFSET,
            0xC000 : self.RAND,
            0xD000 : self.DRAW,
            0xE000 : self.startsWithE,
            0xF000 : self.startsWithF
        }


    """ Functions to decode and run opcode """
    def startsWith0(self):
        search_for = (self.opcode & 0x000F)

        # Attempt to run the opcode function
        try:
            self.opcode_zeros[search_for]()
        except:
            print(f"Unknown Opcode: {hex(self.opcode)}")


    def startsWith8(self):
        search_for = (self.opcode & 0x000F)

        try:
            self.opcode_eights[search_for]()
        except:
            print(f"Unknown Opcode: {hex(self.opcode)}")


    def startsWithE(self):
        search_for = (self.opcode & 0x000F)

        try:
            self.opcode_Es[search_for]()
        except:
            print(f"Unknown Opcode: {hex(self.opcode)}")


    def startsWithF(self):
        search_for = (self.opcode & 0x00FF)

        try:
            self.opcode_Fs[search_for]()
        except:
            print(f"Unknown Opcode: {hex(self.opcode)}")


    """ Emulate Cycle Function """
    def emulateCycle(self):
        # Grab the 16 bit opcode from memory in 2 8 bit sections
        self.opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

        #print(hex(self.opcode))

        search_for = (self.opcode & 0xF000)

        try:
            self.opcode_dict[search_for]()
        except:
            print(f"Unknown Opcode: {hex(self.opcode)}")


        if (self.delay_timer > 0):
            self.delay_timer -= 1

        if (self.sound_timer > 0):
            if (self.sound_timer == 1):
                print("BEEP!")
                self.sound_timer -= 1
