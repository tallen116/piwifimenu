import pygame
import logging
import os
from piwifimenu.ui import user_interface
from piwifimenu.ui import keyboard as vkeyboard

logger = logging.getLogger(__name__)
logger.info('Program started')

FPS = 30.0
screen = None
clock = pygame.time.Clock()

SELECT_KEY = None
KEYBOARD_KEY = 6

def setup_display():
    global screen

    drivers = ['x11', 'fbcon', 'directfb', 'svgalib']

    found = False
    for driver in drivers:
        # Make sure that SDL_VIDEODRIVER is set
        if not os.getenv('SDL_VIDEODRIVER'):
            os.putenv('SDL_VIDEODRIVER', driver)
        try:
            pygame.display.init()
            logger.debug("Video driver: {0}".format(driver))
        except pygame.error:
            logger.error("Driver: {0} failed.".format(driver))
            continue
        found = True
        break

    if not found:
        logger.error('No suitable video driver found!')
        raise Exception('No suitable video driver found!')

    size = (pygame.display.Info().current_w,
            pygame.display.Info().current_h)
    # Change the size here for testing
    # size = (320, 240)
    logger.debug("Framebuffer size: {0} x {1}".format(size[0], size[1]))

    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 0))
    pygame.font.init()
    pygame.display.update()


def first_setup():
    pass


def config_file():
    pass


def main():
    pygame.init()
    setup_display()

    ui = user_interface()
    keyboard = vkeyboard(screen)

    def keyboard_toggle():
        logger.debug("Keyboard toggle button pressed.")
        # Only toggle if currently on a text input widget
        if ui.is_textinput_widget():
            ui.toggle()
            keyboard.toggle()
        if not keyboard.is_enabled():
            ui.set_textinput_widget(keyboard.get_text())

    loop = True
    while loop:

        clock.tick(FPS)
        events = pygame.event.get()
        for event in events:
            logger.debug("pygame event: {}".format(event))
            if event.type == pygame.QUIT:
                loop = False
            if (event.type == pygame.KEYDOWN):
                # OSK button toggle
                if event.key == KEYBOARD_KEY:
                    keyboard_toggle()
            elif (event.type == pygame.JOYBUTTONDOWN):
                if event.button == KEYBOARD_KEY:
                    keyboard_toggle()

        ui.update(events)
        keyboard.update(events)

        if ui.exit_status():
            loop = False

        pygame.display.flip()

    logger.info('Program Finished')
