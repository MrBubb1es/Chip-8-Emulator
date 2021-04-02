from Chip8Simulator import *
from Chip8Helper import *
from config import *
import pygame, random, time
import numpy as np
# Set up pygame
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
Chip = Chip8()

Chip.loadFontset()
Chip.loadProgram()

running = True
while running:
    start_time = time.time()

    Chip.emulateCycle()

    if Chip.draw_screen:
        drawGraphics(screen, Chip.gfx)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False

    if pygame.key.get_pressed()[pygame.K_SPACE]:
        time.sleep(3)

    # Sleep if needed to maintain stable Hz
    time.sleep(1.0 / (HZ - (time.time() - start_time)))
