from Chip8Graphics import *
from config import *
import pygame, random
import numpy as np
# Set up pygame
pygame.init()

testScreen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
testGfx = np.array([random.randint(0,1) for i in range(64*32)])

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if cpu.draw_flag:
        drawGraphics(testScreen, testGfx)
