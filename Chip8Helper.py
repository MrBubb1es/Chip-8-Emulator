from config import *
import pygame, sys

def drawGraphics(screen, gfx):
    # Create a new pygame surface that has the same dimensions as the gfx array
    gfx_surface = pygame.Surface((64, 32))

    # For each pixel in the gfx array,
    # set the corresponding pixel on the
    # gfx_surface to white or black
    for pixel_location, pixel in enumerate(gfx):
        if pixel == 1:
            color = (255,255,255)
        else:
            color = (0,0,0)

        pixel_x = pixel_location % 64
        pixel_y = pixel_location // 64

        gfx_surface.set_at((pixel_x, pixel_y), color)

    # Scale the 64x32 gfx_surface to the size of the pygame window
    gfx_surface = pygame.transform.scale(gfx_surface, screen.get_size())

    # Draw gfx_surface to the screen
    screen.blit(gfx_surface, (0,0))
    pygame.display.flip()


def waitForKeypress():
    print("Awaiting Keypress")

    while True:
        keyboard = pygame.key.get_pressed()

        for KEY in KEY_BINDINGS:
          if keyboard[KEY]:
            return KEY

        for event in pygame.event.get():
          if event.type == pygame.QUIT:
              pygame.quit()
              sys.exit()
