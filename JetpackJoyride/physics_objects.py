from typing import Any
import pygame
from pygame.math import *
import math

class PhysicsObject:
    def __init__(self, pos=(0,0), vel=(0,0), mass=1, angle=0, avel=0, momi=math.inf):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.mass = mass
        self.angle = angle
        self.avel = avel
        self.momi = momi
        self.force = Vector2(0,0)
        self.pivot = Vector2(0,0)
        self.torque = 0


    def set(self, pos=None, angle=None):
        if pos is not None:
            self.pos = Vector2(pos)
        if angle is not None:
            self.angle = angle

    def clear_force(self):
        self.force *= 0
        self.torque *= 0

    def add_force(self, force):
        self.force += force
    
    def add_torque(self, torque):
        self.torque += torque
    
    def impulse(self, impulse, point=None):
        self.vel += Vector2(impulse) / self.mass
        if point is not None:
            self.avel += (point - (self.pos + self.pivot)).cross(impulse) / self.momi

    def update(self, dt):
        # update velocity using the current force
        self.vel += (self.force / self.mass) * dt
        # update position using the newly updated velocity
        self.pos += self.vel * dt
        # update angular
        self.avel += (self.torque / self.momi) * dt
        self.angle += self.avel * dt

class Polygon(PhysicsObject):
    def __init__(self, local_points=[], pivot=(0,0), color=(255,255,255), width=0, normals_length=1, **kwargs):
        super().__init__(**kwargs)
        self.pivot = Vector2(pivot)
        self.local_points = [Vector2(p) for p in local_points]

        self.local_normals = []
        for i in range(len(self.local_points)):
            normal = (self.local_points[i] - self.local_points[i - 1]).normalize().rotate(90)
            self.local_normals.append(normal)
        
        self.color = color
        self.width = width
        self.normals_length = normals_length
        self.contact_type = "Polygon"
        self.update()
        self.check_convex()

    def check_convex(self):
        if len(self.local_points) > 2:
            n = len(self.local_points)
            convex = True
            for i in range(n):
                d = [(self.local_points[j%n] - self.local_points[i]).dot(self.local_normals[i]) for j in range(i+1, i+n-1)]
                if max(d) <= 0:
                    pass
                elif min(d) >= 0:
                    self.local_normals[i] *= -1
                else:
                    convex = False
            if not convex:
                print("WARNING!  Non-convex polygon defined.  Collisions will be incorrect.")
                
    def update(self, dt=0):
        super().update(dt)
        self.points = [(p - self.pivot).rotate_rad(self.angle) + self.pivot + self.pos for p in self.local_points]
        self.normals = [n.rotate_rad(self.angle) for n in self.local_normals]

    def set(self, pos=None, angle=None):
        super().set(pos=pos, angle=angle)
        self.update()
    
    def draw(self, window):
        pygame.draw.polygon(window, self.color, self.points, self.width)
        if self.normals_length > 0:
            for point, normal in zip(self.points, self.normals):
                pygame.draw.line(window, self.color, point, point + normal * self.normals_length)


class Circle(PhysicsObject):
    def __init__(self, radius=10, color=(255,255,255), width=0, **kwargs): # kwargs = keyword arguments
        super().__init__(**kwargs) # calls superclass constructor
        self.radius = radius
        self.color = color
        self.width = width
        self.contact_type = "Circle"

    def draw(self, window):
        pygame.draw.circle(window, self.color, self.pos, self.radius, self.width)

    def contains_point(self, point):
        diff_point = Vector2(point)
        distance = (self.pos - Vector2(point)).length()
        return distance <=self.radius

class Wall(PhysicsObject):
    def __init__(self, point1=(0, 0), point2=(0, 0), color=(255, 255, 255), width=1):
        self.point1 = Vector2(point1)
        self.point2 = Vector2(point2)
        self.color = color
        self.width = width
        self.normal = (self.point2 - self.point1).normalize().rotate(90)
        super().__init__(pos = (self.point1 + self.point2) / 2, mass = math.inf)
        self.contact_type = "Wall"
    
    def draw(self, window):
        pygame.draw.line(window, self.color, self.point1, self.point2, self.width)

class UniformCircle(Circle):
    def __init__(self, radius = 10, density=None, **kwargs):
        # calculate mass and moment of inertia
        self.radius = radius
        self.density = density
        mass = math.pi * self.radius**2 * density
        momi = 0.5 * mass * self.radius**2
        super().__init__(mass=mass, momi=momi, **kwargs)

class UniformPolygon(Polygon):
    def __init__(self, density=None, local_points=[], pos=[0,0], angle=0, shift=True, mass=None, point_value = None, **kwargs):
        total_mass = 0
        total_momi = 0
        com_num = Vector2(0)
        self.point_value = point_value
        if mass is not None and density is not None:
            raise("Cannot specify both mass and density.")
        if mass is None and density is None:
            mass = 1 # default
        
        # calculate mass, moment of inertia, and center of mass
        for i in range(len(local_points)):
            s0 = Vector2(local_points[i])
            s1 = Vector2(local_points[(i-1)])

            # triangle mass
            triangle_mass = density * (0.5 * s0.cross(s1))

            # triangle moment of inertia
            triangle_momi = (triangle_mass / 6) * (s0.dot(s0) + s1.dot(s1) + s0.dot(s1))

            # add to total mass
            total_mass += triangle_mass
            # add to total moment of inertia
            total_momi += triangle_momi
            # add to center of mass numerator
            com_num += triangle_mass * (s0 + s1) / 3
        
        # calculate total center of mass
        total_com = com_num / total_mass

        # if mass is specified, then scale mass and momi
        if mass is not None:
            total_mass = mass
            total_momi = mass / total_mass

        # shift local_points origin to center of mass
        if shift:
            total_momi = total_momi - total_mass * total_com.magnitude()**2
          
        total_momi = abs(total_momi)
        total_mass = abs(total_mass)

        # call super().__init__() with those correct values
        super().__init__(mass=total_mass, momi=total_momi, pivot=total_com, local_points=local_points, pos=pos, angle=angle, **kwargs)