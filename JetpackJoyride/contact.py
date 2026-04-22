from pygame.math import Vector2
from physics_objects import PhysicsObject, Circle, Wall, Polygon
import math
import random

# Returns a new contact object of the correct subtype
def generate(a, b, **kwargs):
    # Check if a's type comes later than b's alphabetically.
    if b.contact_type < a.contact_type:
        a, b = b, a
    # This calls the class of the appropriate name based on the two contact types.
    return globals()[f"{a.contact_type}_{b.contact_type}"](a, b, **kwargs)
    

# Generic contact class, to be overridden by specific scenarios
class Contact():
    def __init__(self, a:PhysicsObject, b:PhysicsObject, resolve=False, **kwargs):
        self.a = a
        self.b = b
        self.kwargs = kwargs
        self.update()
        if resolve:
            self.resolve(update=False)

    def update(self):
        self.overlap = 0
        self.normal = Vector2(1, 0)

    def point(self):
        return Vector2(0, 0)

    def resolve(self, update=True, **kwargs):
        if update:
            self.update()
        
        # This pattern first checks keywords to resolve, then keywords given to contact.
        restitution = kwargs.get("restitution", self.kwargs.get("restitution", 0)) # 0 is default
        rebound = kwargs.get("rebound", self.kwargs.get("rebound", 0)) # 0 is default
        friction = kwargs.get("friction", self.kwargs.get("friction", 0)) # 0 is default
        
        # RESOLVE OVERLAP
        if self.overlap > 0:
            m = 1 / (1/self.a.mass + 1/self.b.mass)
            self.a.set(pos = self.a.pos + m/self.a.mass * self.overlap * self.normal)
            self.b.set(pos = self.b.pos - m/self.b.mass * self.overlap * self.normal)

            # RESOLVE VELOCITY
            point = self.point() # contact point
            sa = point - (self.a.pos - self.a.pivot)
            vapoint = self.a.vel + self.a.avel * sa.rotate(90)
            sb = point - (self.b.pos - self.b.pivot)
            vbpoint = self.b.vel + self.b.avel * sb.rotate(90)
            relative_vel = vapoint - vbpoint
            vdotn = relative_vel.dot(self.normal)
            
            reduced_m = 1 / (1/self.a.mass + 1/self.b.mass + sa.cross(self.normal)**2/self.a.momi + sb.cross(self.normal)**2/self.b.momi)
            if vdotn < 0:
                Jn = -(1 + restitution) * reduced_m * vdotn + reduced_m * rebound
                tangent = self.normal.rotate(90)
                vdott = relative_vel.dot(tangent)
                Jt = -reduced_m * vdott   # for static friction

                if abs(Jt) <= friction*Jn:
                    #static friction
                    shift = self.overlap * vdott/vdotn
                    self.a.pos += reduced_m/self.a.mass * shift * tangent
                    self.b.pos -= reduced_m/self.b.mass * shift * tangent
                else:
                    #kinetic friction
                    Jt = friction * Jn * math.copysign(1, -vdott)
                
                impulse = Jn * self.normal + Jt * tangent
                self.a.impulse(impulse, point)
                self.b.impulse(-impulse, point)


# Contact class for two circles
class Circle_Circle(Contact):
    def update(self):
        self.a:Circle
        self.b:Circle
        self.overlap, self.normal = circle_circle(self.a, self.b.pos, self.b.radius)

    def point(self):
        return self.a.pos + self.a.radius * (-self.normal)
    
def circle_circle(circle:Circle, pos, radius):
    r = circle.pos - pos
    overlap = circle.radius + radius - r.magnitude()
    if r:
        normal = r.normalize()
    else:
        normal = Vector2(1, 0).rotate(random.uniform(0, 360))
    return overlap, normal



# Contact class for Circle and a Wall
# Circle is before Wall because it comes before it in the alphabet
class Circle_Wall(Contact):
    def update(self):  # compute the appropriate values
        self.a:Circle
        self.b:Wall
        self.overlap, self.normal = circle_wall(self.a, self.b.pos, self.b.normal)

    def point(self):
        return self.a.pos + self.a.radius * (-self.normal)
    
def circle_wall(circle:Circle, pos:Vector2, normal:Vector2):
    overlap = (pos - circle.pos).dot(normal) + circle.radius
    return overlap, normal

# Empty class for Wall - Wall collisions
# The intersection of two infinite walls is not interesting, so skip them
class Wall_Wall(Contact):
    pass

class Circle_Polygon(Contact):
    def update(self):  # compute the appropriate values
        circle:Circle = self.a
        polygon:Polygon = self.b

        self.overlap = math.inf
        # Loop over all "walls"
        for i, (point, normal) in enumerate(zip(polygon.points, polygon.normals)):
            # Find the overlap of each "wall"
            wall_overlap, wall_normal = circle_wall(circle, point, normal)
            # Keep the minimum overlap
            if wall_overlap < self.overlap:
                self.overlap = wall_overlap
                self.normal = wall_normal
                min_i = i
                if self.overlap < 0:
                    break

        # Check corners
        if 0 < self.overlap < circle.radius:
            point1 = polygon.points[min_i]
            point2 = polygon.points[min_i - 1]
            # Check if nearest point1
            if (point1 - point2).dot(circle.pos - point1) > 0:
                self.overlap, self.normal = circle_circle(circle, point1, 0)
            # Check if nearest point2
            if (point2 - point1).dot(circle.pos - point2) > 0:
                self.overlap, self.normal = circle_circle(circle, point2, 0)
    
    def point(self):
        return self.a.pos + self.a.radius * (-self.normal)
    
class Polygon_Wall(Contact):
    def update(self):
        wall:Wall = self.b
        self.overlap, self.normal, self.index = polygon_wall(self.a, wall.point1, wall.normal)

    def point(self):
        return self.a.points[self.index]
    
def polygon_wall(polygon, wall_point, wall_normal):
    max_overlap = -math.inf
    for i, point in enumerate(polygon.points):
        overlap = (wall_point - point).dot(wall_normal) # circle-wall
        if overlap > max_overlap:
            max_overlap = overlap
            index = i
    return max_overlap, wall_normal, index

class Polygon_Polygon(Contact):
    def update(self):
        self.overlap = math.inf
        # check polygon a's points against polygon b's walls
        self.polygon_polygon(self.a, self.b)
        # check polygon b's points against polygon a's walls
        # if the min overlap belongs to the second case, reverse self.normal
        if self.polygon_polygon(self.b, self.a):
            self.normal = -self.normal

    def polygon_polygon(self, point_poly:Polygon, wall_poly:Polygon):
        '''sets self.overlap, self.normal, self.index, self.point_poly
            returns True if a new overlap is found
            returns False if no new overlap is found (or if a negative overlap is found)'''
        found_new_overlap = False
        # Loop over all wall_poly's walls
        for i, (point, normal) in enumerate(zip(wall_poly.points, wall_poly.normals)):
            # Find the the overlap between point_poly and this wall (use polygon_wall)
            overlap, new_normal, index = polygon_wall(point_poly, point, normal)
            # If overlap is less than self.overlap (found_new_overlap = True), 
            # keep it and set self.overlap, self.normal, self.index, self.point_poly    
            if overlap < self.overlap:
                found_new_overlap = True
                self.overlap = overlap
                self.normal = new_normal
                self.index = index
                self.point_poly = point_poly
            # Optional: if self.overlap < 0, return False
        return found_new_overlap
    
    def point(self):
        # return the point at the saved index and polygon
        return self.point_poly.points[self.index]