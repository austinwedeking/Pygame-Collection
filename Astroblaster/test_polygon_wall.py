import pygame
from pygame.locals import *
from pygame.math import Vector2
from physics_objects import Polygon, Wall, Circle
import contact 

# initialize pygame and open window
pygame.init()
width, height = 800, 600
window = pygame.display.set_mode([width, height])

# set timing stuff
fps = 60
dt = 1/fps
clock = pygame.time.Clock()

# set objects
objects = [] 

local_points = [
        [0,0],
        [200,0],
        [300,100],
        [100,300],
        [0,100]
    ]

objects.append(Wall(point1=[800,600], point2=[0,300], color=(0,0,0)))
objects.append(Wall(point1=[600,0], point2=[800,600], color=(0,0,0)))
objects.append(Wall(point1=[0,300], point2=[600,0], color=(0,0,0)))
polygon = Polygon(mass=1, local_points=[(0,-100), (75,-25), (-25,25)], color=[0,0,255], width=2)
#polygon = Circle(radius=100, mass=1, color=[0,0,255], width=2)

# game loop
running = True
while running:
    # update the display
    pygame.display.update()
    # delay for correct timing
    clock.tick(fps)

    # EVENT loop
    while event := pygame.event.poll():
        if event.type == pygame.QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
    
    # set the position of the hovering polygon to the mouse position
    polygon.set(pos=pygame.mouse.get_pos())
    
    # collisions
    overlap = False
    contacts = []

    # check for contact with any other objects
    for obj in objects:
        c = contact.generate(polygon, obj)
        if c.overlap > 0:
            overlap = True
            contacts.append(c)

    # DRAW section
    # clear the screen
    if overlap:
        window.fill([255,255,0])
    else:
        window.fill([255,255,255])

    # draw objects
    for o in objects:
        o.update(dt)
        o.draw(window)
    polygon.draw(window)

    # draw where the polygon would go after each contact is resolved
    for c in contacts:
        if c.overlap > 0:
            pos = Vector2(polygon.pos)
            vel = Vector2(polygon.vel)
            c.resolve()
            w = polygon.width
            polygon.width = 1
            polygon.draw(window)
            polygon.width = w
            pygame.draw.circle(window, (0,0,0), c.point(), 5, 0)  # draw the contact point
            polygon.set(pos=pos)
            polygon.vel = vel
