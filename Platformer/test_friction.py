import pygame
from pygame.math import Vector2
from pygame.locals import *
from physics_objects import Circle, Wall
import contact
from forces import Gravity
import itertools
import math

# initialize pygame and open window
pygame.init()
width, height = 800, 600
window = pygame.display.set_mode([width, height])
center = Vector2(width/2, height/2)
diagonal = math.sqrt(width**2 + height**2)

# set timing stuff
fps = 60
dt = 1/fps
clock = pygame.time.Clock()

# set objects
objects = [] 

circle = Circle(pos=(100,300), vel=(800,0), radius=60, mass=1, color=[0,0,255], width=0)

slope_of_floor    = 0.25
coeff_of_friction = 0.1
floor = Wall((800, 600 - 800*slope_of_floor), (0, 600), color=(0,255,0))

objects.append(circle)
gravity_objects = objects.copy()

objects.append(floor)

gravity = Gravity(acc=[0,980], objects_list=gravity_objects)

# game loop
running = True
while running:
    # update the display
    pygame.display.update()
    # delay for correct timing
    clock.tick(fps)
    # clear the screen
    window.fill([255,255,255])

    # EVENTS
    while event := pygame.event.poll():
        if event.type == pygame.QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False

    # PHYSICS
    gravity.apply()

    # update objects
    for o in objects:
        o.update(dt)

    # collisions
    for a, b in itertools.combinations(objects, 2):
        c = contact.generate(a, b, resolve=True, restitution=0.2, friction=coeff_of_friction)

    # clear force
    for o in objects:
        o.clear_force()

    # GRAPHICS
    # draw objects
    for o in objects:
        o.draw(window)

    
