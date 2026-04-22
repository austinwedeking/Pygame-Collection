import pygame
from pygame.constants import *
from pygame.math import Vector2
from physics_objects import Circle, Polygon
import contact
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

local_points =[
        [-20,-125],
        [20,-125],
        [20,125],
        [-20,125],
    ]

poly = Polygon(mass=40*250, momi=40*250/12*(40**2+250**2), local_points=local_points, pos=[400,300], color=[255,0,0])
objects.append(poly)
circle = Circle(pos=(100,200), vel=(200,0), radius=30, mass=math.pi*30**2, color=[0,0,255])
objects.append(circle)

# game loop
running = True
while running:
    # update the display
    pygame.display.update()
    # delay for correct timing
    clock.tick(fps)

    # EVENT loop
    while event := pygame.event.poll():
        if event.type == QUIT:
            running = False

    # update objects
    for o in objects:
        o.update(dt)

    # collisions
    overlap = False
    contacts = []

    # check collisions among the polygon and all placed circles
    for a, b in itertools.combinations(objects, 2):
        restitution = 0.5
        c = contact.generate(a, b, resolve=False, restitution=restitution)
        if c.overlap > 0:
            vbefore = ((c.a.vel+c.a.avel*(c.point()-c.a.pos+c.a.pivot).rotate(90)).dot(c.normal)
                        - (c.b.vel+c.b.avel*(c.point()-c.b.pos+c.b.pivot).rotate(90)).dot(c.normal))
            c.resolve()
            vafter = ((c.a.vel+c.a.avel*(c.point()-c.a.pos+c.a.pivot).rotate(90)).dot(c.normal)
                        - (c.b.vel+c.b.avel*(c.point()-c.b.pos+c.b.pivot).rotate(90)).dot(c.normal))
            print(f"before:{vbefore}, after:{vafter}, ratio:{vafter/vbefore}, retitution:{restitution}")

    # DRAW section
    # clear the screen
    window.fill([255,255,255])

    # draw objects
    for o in objects:
        o.draw(window)