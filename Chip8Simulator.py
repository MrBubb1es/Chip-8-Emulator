"""
Really helpful website:

    http://multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/

"""
# Hello
import numpy as np

class Chip8:
    def __init__(self):
        # Unsigned short
        self.opcode = np.uint16
        # Registers
        self.V = np.array([0] * 16, dtype=np.uint16)
        # Index register
        self.I = np.uint16
        # Program counter to keep track of the current instruction in memory
        self.pc = np.uint16

        # 4096 unsigned chars
        # 0x000-0x1FF - Chip 8 interpreter (contains font set in emu)
        # 0x050-0x0A0 - Used for the built in 4x5 pixel font set (0-F)
        # 0x200-0xFFF - Program ROM and work RAM
        self.memory = np.array([0] * 4096, dtype=np.uint8)

        # Graphics array
        self.gfx = np.array([1] * (64 * 32))

        # Timers that count down at 60hz
        self.delay_timer = np.uint8
        self.sound_timer = np.uint8

        # Original Chip8 stack size was 16,
        # but we increased it for funsies
        self.stack = np.array([0] * 256, dtype=np.uint16)
        # Stack pointer to keep track of the level of the stack
        self.sp = np.uint16

        # key array used to keep track of the current state of the keyboard
        self.key = np.array([0] * 16, dtype=np.uint8)

    """
    Full list of opcodes and their functionalities found here:
    https://en.wikipedia.org/wiki/CHIP-8
    """

    # 00E0 - Clear screen
    def CLS(self):
        # Fill array with 0s
        self.gfx.fill(0)

        # Increment program counter
        self.pc += 2

    # 00EE - Return from subroutine
    def RETURN(self):
        # Set the pc to the location on the top of the stack and decrement the sp
        self.pc = self.stack[self.sp]
        self.sp -= 1

        self.pc += 2

    # 1NNN - Jumps to address NNN
    def GOTO(self):
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

    # 7XNN - Adds NN to VX
    def ADDRC(self):
        X = (self.opcode & 0x0F00) >> 8
        NN = (self.opcode & 0x00FF)

        self.V[X] += NN

    # 8XY0 - Sets VX to the value of VY
    def SETRR(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4

        self.V[X] = self.V[Y]

    # 8XY1 - Sets VX to VX or VY. (Bitwise OR operation)
    def OR(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4

        # Bitwise OR
        self.V[X] = self.V[X] | self.V[Y]

    # 8XY2 - Sets VX to VX and VY. (Bitwise AND operation)
    def AND(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4

        # Bitwise AND
        self.V[X] = self.V[X] & self.V[Y]

    # 8XY3 - Sets VX to VX xor VY
    def XOR(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4

        # Bitwise XOR
        self.V[X] = self.V[X] ^ self.V[Y]

    # 8XY4 - Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there isn't
    def ADDRR(self):
        X = (self.opcode & 0x0F00) >> 8
        Y = (self.opcode & 0x00F0) >> 4


    # 8XY5 - VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there isn't
    def (self):


    # 8XY6 - Stores the least significant bit of VX in VF and then shifts VX to the right by 1
    def (self):


    # 8XY7 - Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there isn't
    def (self):


    # 8XYE - Stores the most significant bit of VX in VF and then shifts VX to the left by 1
    def (self):


    # 9XY0 - Skips the next instruction if VX doesn't equal VY
    def (self):


    # ANNN - Sets I to the address NNN
    def (self):


    # BNNN - Jumps to the address NNN plus V0
    def (self):


    # CXNN - Sets VX to the result of a bitwise and operation on a random number (Typically: 0 to 255) and NN.
    def (self):


    # DXYN - Draw (see link for more)
    def (self):


    # EX9E - Skips the next instruction if the key stored in VX is pressed
    def (self):


    # EXA1 - Skips the next instruction if the key stored in VX isn't pressed
    def (self):


    # FX07 - Sets VX to the value of the delay timer
    def (self):


    # FX0A - A key press is awaited, and then stored in VX
    def (self):


    # FX15 - Sets the delay timer to VX
    def (self):


    # FX18 - Sets the sound timer to VX
    def (self):


    # FX1E - Adds VX to I. VF is not affected
    def (self):


    # FX29 - Sets I to the location of the sprite for the character in VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font
    def (self):


    # FX33 - BCD (see link for more)
    def (self):


    # FX55 -  	Stores V0 to VX (including VX) in memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified
    def (self):


    # FX65 - Fills V0 to VX (including VX) with values from memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified
    def (self):



test = Chip8()

test.CLS()


# hilo kermit the FRORG here
