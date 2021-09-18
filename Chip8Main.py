from Chip8Simulator import *
from Chip8Helper import *
from config import *
import pygame, random, time
import numpy as np

# Set up pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

def main():
    Chip = Chip8()
    Chip.loadFontset()
    Chip.loadProgram()

    Chip.populateZeros()
    Chip.populateEights()
    Chip.populateEs()
    Chip.populateFs()
    Chip.populateOpcodeDict()

    running = True
    while running:
        start_time = time.time()

        Chip.emulateCycle()

        if Chip.draw_screen:
            drawGraphics(screen, Chip.gfx)
            Chip.draw_screen = False
            # Sleep if needed to maintain stable Hz
            clock.tick(HZ)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False


main()
