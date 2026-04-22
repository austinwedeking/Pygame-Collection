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
        [-20,-20],
        [20,-20],
        [20,230],
        [-20,230],
    ]

poly = Polygon(mass=math.inf, local_points=reversed(local_points), pos=[400,300], pivot=(0,230), color=[255,0,0], avel=1, normals_length=100)
objects.append(poly)
circle = Circle(radius=60, mass=1, color=[0,0,255], width=2)

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
        # add a circle when you click at the click position
        elif event.type == pygame.MOUSEBUTTONDOWN:
            objects.append(Circle(pos=event.pos, radius=circle.radius, color=circle.color, mass=1))
    
    # set the position of the hovering circle to the mouse position
    circle.pos = Vector2(pygame.mouse.get_pos())
    
    # update objects
    for o in objects:
        o.update(dt)
    
    # collisions
    overlap = False
    contacts = []

    # show the overlap with the circle that is hovering with your mouse
    c = contact.generate(circle, poly)
    if c.overlap > 0:
        pos = circle.pos
        vel = circle.vel
        c.resolve()
        pygame.draw.circle(window, c.a.color, c.a.pos, c.a.radius, 1)
        #pygame.draw.circle(window, (0,0,0), c.point(), 5, 0)
        circle.pos = pos
        circle.vel = vel

    # check collisions among the polygon and all placed circles
    for a, b in itertools.combinations(objects, 2):
        c = contact.generate(a, b, resolve=True, restitution=1)

    # DRAW section
    # clear the screen
    window.fill([255,255,255])

    # draw objects
    for o in objects:
        o.draw(window)
    circle.draw(window)

    # remove circles that go too far off screen
    for o in objects:
        if (o.pos - center).magnitude() > diagonal + circle.radius:
            objects.remove(o)
