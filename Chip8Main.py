from Chip8Simulator import *
from Chip8Helper import *
from config import *
import pygame, random
import numpy as np
# Set up pygame
pygame.init()

testScreen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
testChip = Chip8()

testChip.loadFontset()
testChip.loadProgram()

running = True
while running:

    testChip.emulateCycle()
    drawGraphics(testScreen, testGfx)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
