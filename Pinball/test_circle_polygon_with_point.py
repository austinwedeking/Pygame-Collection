import pygame
from pygame.constants import *
from pygame.math import Vector2
from physics_objects import Circle, Polygon
import contact
import math

''' To include point, uncomment line 82: 
    #pygame.draw.circle(window, (0,0,0), c.point, 5, 0)  # draw the contact point '''

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

offsets =[
        [0,0],
        [200,0],
        [300,100],
        [100,300],
        [0,100]
    ]

objects.append(Polygon(local_points=reversed(offsets), pos=[250,150], color=[255,0,0], 
                       avel=0.5, mass=math.inf, normals_length=100))
circle = Circle(radius=100, mass=1, color=[0,0,255], width=2)

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
    
    # set the position of the hovering circle to the mouse position
    circle.pos = Vector2(pygame.mouse.get_pos())
    
    # collisions
    overlap = False
    contacts = []

    # check for contact with any other objects
    for obj in objects:
        c = contact.generate(circle, obj)
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
    circle.draw(window)

    # draw where the circle would go after each contact is resolved
    for c in contacts:
        pos = circle.pos
        vel = circle.vel
        c.resolve()
        pygame.draw.circle(window, c.a.color, c.a.pos, c.a.radius, 1)
        pygame.draw.circle(window, (0,0,0), c.point(), 5, 0)  # draw the contact point
        circle.pos = pos
        circle.vel = vel

