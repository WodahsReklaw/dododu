
from imports import *

import animation

class GameObject(rgl.gameobject.Object):
    
    def __init__(self, game, groups):
        rgl.gameobject.Object.__init__(self, groups)
        self.game = game
        self.animation = animation.Animation()
        self.offset = (0, 0)
        self.size = None
    
    def move(self, dx, dy):
        if dx != 0:
            self.move_single_axis(dx, 0)
        if dy != 0:
            self.move_single_axis(0, dy)
    
    def on_collision(self, o, dx, dy):
        pass

    def on_collision2(self, o, dx, dy, sides):
        pass

    def move_single_axis(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

        for obj in self.collision_objects:
            if self.rect.colliderect(obj.rect) and obj != self:
                if not hasattr(obj, "sides"):
                    if dx > 0:
                        self.rect.right = obj.rect.left
                    if dx < 0:
                        self.rect.left = obj.rect.right
                    if dy > 0:
                        self.rect.bottom = obj.rect.top
                    if dy < 0:
                        self.rect.top = obj.rect.bottom
                    self.on_collision(obj, dx, dy)
                else:
                    sides = [False, False, False, False]
                    if dx < 0 and obj.sides[3] and self.rect.left > obj.rect.centerx:
                        self.rect.left = obj.rect.right
                        self.on_collision(obj, dx, dy)
                    if dx > 0 and obj.sides[1] and self.rect.right < obj.rect.centerx:
                        self.rect.right = obj.rect.left
                        self.on_collision(obj, dx, dy)
                    if dy < 0 and obj.sides[2] and self.rect.top > obj.rect.centery:
                        self.rect.top = obj.rect.bottom
                        self.on_collision(obj, dx, dy)
                    if dy > 0 and obj.sides[0] and self.rect.bottom < obj.rect.centery:
                        self.rect.bottom = obj.rect.top
                        self.on_collision(obj, dx, dy)
                  
                    if dy < 0 and self.rect.top <= obj.rect.top:
                        if obj.sides[0]:
                            sides[0] = True
                            self.rect.top = obj.rect.top
                    if dy > 0 and self.rect.bottom >= obj.rect.bottom:
                        if obj.sides[2]:
                            sides[2] = True
                            self.rect.bottom = obj.rect.bottom
                    if dx < 0 and self.rect.left <= obj.rect.left:
                        if obj.sides[1]:
                            sides[1] = True
                            self.rect.left = obj.rect.left
                    if dx > 0 and self.rect.right >= obj.rect.right:
                        if obj.sides[3]:
                            sides[3] = True
                            self.rect.right = obj.rect.right
                    if True in sides:
                        self.on_collision2(obj, dx, dy, sides)

    def draw(self, surface, camera):
        if not self.size:
            self.size = self.rect.size
        r = Rect(self.rect.x - camera.x, self.rect.y - camera.y, self.rect.w, self.rect.h)
        self.animation.draw(surface, r, self.offset, self.size)

class Person(GameObject):
    
    def __init__(self, game, name, pos):
        GameObject.__init__(self, game, self.groups)
        self.rect = Rect(pos[0], pos[1], 16, 16)
        self.sheet = util.load_sheet("%s.png" % name, 16, 16)
        self.sheet.append(util.flip_images(self.sheet[2]))
        i = 0
        for n in ["down", "up", "right", "left"]:
            self.animation.add("stand-" + n, [self.sheet[i][0]])
            self.animation.add("walk-" + n, self.sheet[i][1:])
            i += 1
        self.speed = 2
        self.anim_speed = 4
        self.facing = 2
        self.walking = False
        self.dest = self.rect.topleft
        self.name = name

    def dir_to_string(self, n):
        if n == 0:
            return "up"
        if n == 1:
            return "left"
        if n == 2:
            return "down"
        if n == 3:
            return "right"

    def walk(self, dx, dy, running=False):
        if not self.walking:
            self.dest = (self.rect.x+(dx*16), self.rect.y+(dy*16))
            self.walking = True
            self.on_walk(dx, dy)
            if dx > 0:
                self.facing = 3
            if dx < 0:
                self.facing = 1
            if dy > 0:
                self.facing = 2
            if dy < 0:
                self.facing = 0

    def update(self):
        self.z = self.rect.bottom
        dir = self.dir_to_string(self.facing)
        anim = "stand"
        if self.walking:
            anim = "walk"
            if self.rect.x < self.dest[0]:
                self.move(self.speed, 0)
            if self.rect.x > self.dest[0]:
                self.move(-self.speed, 0)
            if self.rect.y < self.dest[1]:
                self.move(0, self.speed)
            if self.rect.y > self.dest[1]:
                self.move(0, -self.speed)
        if self.rect.topleft == self.dest:
            self.walking = False
        self.animation.animate(anim + "-" + dir, self.anim_speed, -1)
        
    def face(self, person):
        dx = self.rect.centerx - person.rect.centerx
        dy = self.rect.centery - person.rect.centery
        if abs(dx) >= abs(dy):
            if dx > 0:
                self.facing = 1
            else:
                self.facing = 3
        else:
            if dy > 0:
                self.facing = 0
            else:
                self.facing = 2

    def on_walk(self, dx, dy):
        pass

    def on_collision(self, o, dx, dy):
        self.walking = False
        self.dest = self.rect.topleft
    
    def on_collision2(self, o, dx, dy, sides):
        self.walking = False
        self.dest = self.rect.topleft

class Player(Person):
    
    def __init__(self, game, id):
        party = ["faldo", "shara", "igon"]
        Person.__init__(self, game, party[2-id], (128, 128))
        self.steps = []
        self.trailer = None
        if id > 0:
            self.trailer = Player(game, id-1)
        self.trail = 2
    
    def on_walk(self, dx, dy):
        if self.trailer:
            #print self.name
            self.steps.insert(0, (dx, dy))
            self.steps = self.steps[:self.trail]
            if len(self.steps) >= self.trail:
                self.trailer.walk(*self.steps[-1])
                
    def update(self):
        Person.update(self)
        x = self.rect.x / 16
        y = self.rect.y / 16
        t = self.game.map.map[y][x]
        self.size = (16, 16)
        if t:
            if t.type == "tree-middle" or t.type == "tree-top":
                self.size = (16, 12)
        
class Scenery(GameObject):
    
    def __init__(self, game, x, y, image):
        GameObject.__init__(self, game, self.groups)
        self.animation.add("normal", util.load_images("%s" % image))
        self.rect = self.animation.image.get_rect(topleft=(x, y))
        self.type = image.split(".")[0]
        self.z = -10

class Water(GameObject):
    
    def __init__(self, game, x, y):
        GameObject.__init__(self, game, self.groups)
        self.animation.add("normal", util.load_sheet("water-anim.png", 16, 16)[0])
        self.rect = self.animation.image.get_rect(topleft=(x, y))
        self.z = -10
        self.animation.animate("normal", 8, -1)

class Obstacle(GameObject):
    
    def __init__(self, game, x, y, image):
        GameObject.__init__(self, game, self.groups)
        self.animation.add("normal", util.load_images("%s" % image))
        self.rect = self.animation.image.get_rect(topleft=(x, y))
        self.z = -1

class Door(GameObject):
    
    def __init__(self, game, x, y, id):
        GameObject.__init__(self, game, self.groups)
        self.animation.add("normal", util.load_images("door.png"))
        self.rect = self.animation.image.get_rect(topleft=(x, y))
        self.z = self.rect.bottom
        self.id = id

class NPC(Person):
    
    def __init__(self, game, x, y, name):
        Person.__init__(self, game, "npc-" + name.lower().replace(".", "").replace(" ", ""), (x, y))
        self.name = name
        self.bounds = Rect(0, 0, 32, 48)
    
    def set_pos_to(self, npc):
        self.facing = npc.facing
        self.rect = Rect(npc.rect)
    
    def update(self):
        Person.update(self)
        self.bounds.center = self.rect.center

class Chest(GameObject):
    
    def __init__(self, game, x, y, id):
        GameObject.__init__(self, game, self.groups)
        self.animation.add("normal", util.load_images("chest.png"))
        self.rect = self.animation.image.get_rect(topleft=(x, y))
        self.id = id
