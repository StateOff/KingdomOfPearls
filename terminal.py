import pygame
from pygame.locals import *
import sys

import builtins

pygame.init()

size = width, height = 320, 180
window_size = (width * 4, height * 4)

speed = [1, 1]

black = 0, 0, 0

screen = pygame.Surface(size)
window = pygame.display.set_mode(window_size)

ball = pygame.image.load("intro_ball.gif")

ballrect = ball.get_rect()


ballrect = ballrect.move(speed)

if ballrect.left < 0 or ballrect.right > width:

    speed[0] = -speed[0]

if ballrect.top < 0 or ballrect.bottom > height:

    speed[1] = -speed[1]





# SCREEN = pygame.Surface(V.Window(resizable=True))
# print(pyglet.font.add_file('NotoColorEmoji-Regular.ttf'))
# print(pyglet.font.add_file('MorePerfectDOSVGA.ttf'))
# print(pyglet.font.load("Noto Color Emoji", 12))
# print(pyglet.font.load("More Perfect DOS VGA", 12))
# LABEL = pyglet.text.Label('Hello, world 🤯',
#                           font_name='Noto Color Emoji',
#                           font_size=12,
#                           x=WINDOW.width//2, y=WINDOW.height//2,
#                           anchor_x='center', anchor_y='center')

# LABEL = pyglet.text.Label('Hello, world 🤯',
#                           font_name='More Perfect DOS VGA',
#                           font_size=12,
#                           x=WINDOW.width//2, y=WINDOW.height//2,
#                           anchor_x='center', anchor_y='center')


# @WINDOW.event
# def on_draw():
#     WINDOW.clear()
#     LABEL.draw()
#
# pyglet.app.run()

def print(*args, sep=' ', end='\n', file=None): # known special case of print
    global window_size
    screen.blit(ball, ballrect)
    window_size = window.get_size()
    factor = max(window_size[0] // width, window_size[1] // height)
    screen_in_window = pygame.transform.scale_by(screen, factor)
    window.blit(screen_in_window, (0, 0))

    pygame.display.update()
    return builtins.print(*args, sep=sep, end=end, file=file)

def input(*args, **kwargs):
    """
    If the user hits EOF (*nix: Ctrl-D, Windows: Ctrl-Z+Return), raise EOFError.
    On *nix systems, readline is used if available.
    """
    text = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYUP:
                key = pygame.key.name(event.key)
                if event.key == K_RETURN:
                    return text
                if event.key == K_BACKSPACE:
                    text = text[:-1]
                if event.key == K_SPACE:
                    text += " "
                elif event.mod == KMOD_NONE and (event.key >= K_0 and event.key <= K_9):
                    text += key
                elif (event.key >= K_a and event.key <= K_z):
                    text += key.upper() if event.mod & KMOD_SHIFT else key

                builtins.print(text)

    # return builtins.input(*args, **kwargs)

def clear():
    screen.fill(black)
    pass