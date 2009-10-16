#! /usr/bin/env python

import os, math, glob

import pygame
from pygame.locals import *

from retrogamelib import gameobject
import ConfigParser

def load_image(filename):
    return pygame.image.load(os.path.join("data", "images", filename)).convert_alpha()

def make_arrow():
    img = pygame.Surface((24, 12))
    img.set_colorkey((0, 0, 0), RLEACCEL)
    pygame.draw.polygon(img, (255, 255, 255), ((12, 0), (0, 12), (24, 12)))
    return img

def make_image(filename):
    d = open(filename, "rU").read()
    w = len(d.split("\n")[0].split(" "))
    h = len(d.split("\n"))
    i = pygame.Surface((w, h))
    i.fill((0, 255, 0))
    i.set_colorkey((0, 255, 0))
    i.fill((255, 255, 255))
    x = y = 0
    for row in d.split("\n"):
        for char in row.split(" "):
            if char != "---":
                i.set_at((x, y), (0, 0, 0))
            x += 1
        y += 1
        x = 0
    return i

def round_to_nearest_pow(num, pow=2):
    last = pow
    next = pow * pow
    if num <= pow:
        return pow

    while next < num:
        last = next
        next *= pow

    if abs(num-last) <= abs(num-next):
        return last
    return next

def nearest_multiple(num, div=2):
    if num == 0:
        return div
    if div == 0:
        return 0

    x = num % div

    min = num - x
    max = min + div

    if abs(num-min) < abs(num-max):
        return min
    return max

class Template(gameobject.Object):
    
    def __init__(self, editor, name, image, i, doffset, roffset):
        gameobject.Object.__init__(self, self.groups)
        self.editor = editor
        self.image = load_image(image)
        iw = float(self.image.get_width())
        ih = float(self.image.get_height())
        
        self.offset = doffset
        self.roffset = roffset
        self.name = name
        w = iw
        h = ih
        if iw > ih:
            r = float(h)/w
            w = 32
            h = 32 * r
        if ih > iw:
            r = float(w)/h
            h = 32
            w = 32 * r
        if ih == iw:
            w = 32
            h = 32
        
        self.icon = pygame.transform.scale(self.image, (int(w), int(h)))
        self.id = image.split(".")[0]
        self.i = i
        self.rect = self.image.get_rect(topleft=(0, self.i*34))

class Tile(gameobject.Object):
    
    def __init__(self, template, pos, groups):
        gameobject.Object.__init__(self, groups)
        self.groups = groups
        self.template = template
        self.pos = pos
        self.rect = self.template.image.get_rect(topleft = pos)
        self.offset = self.template.offset
        self.rect.y += self.template.roffset
        self.rect.h = nearest_multiple(self.rect.h, self.template.editor.th)
        self.name = self.template.name

class Editor(object):
    
    def __init__(self, screen_size, tile_size):
        
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        
        pygame.display.set_caption("Level Editor")
        self.screen = pygame.display.set_mode((screen_size[0]+48, screen_size[1]))
    
        self.screen_size = screen_size
        self.tile_size = tile_size
        self.font = pygame.font.Font(None, 24)
        self.running = True
        self.maphud = MapHud(self)
        self.curr = self.maphud
    
    def handle_input(self):
        events = pygame.event.get()
        for e in events:
            if e.type == QUIT:
                self.running = False
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    self.running = False
        return events
    
    def update(self):
        events = self.handle_input()
        self.curr.update()
        self.curr.handle_input(events)
        self.curr.draw(self.screen)

    def loop(self):
        while self.running:
            self.update()
            
    def request_input(self, prompt, limit=None, allowed_chars=None):
        text = ""
        while self.running:
            events = self.handle_input()
            for e in events:
                if e.type == KEYDOWN:
                    if e.key == K_RETURN:
                        return text
                    elif e.key == K_BACKSPACE:
                        if len(text) > 0:
                            text = text[:-1]
                    elif e.key == K_ESCAPE:
                        break
                    else:
                        c = e.unicode
                        if allowed_chars:
                            if e.unicode not in allowed_chars:
                                c = ""
                        text += c
                        if limit:
                            if len(text) > limit:
                                text = text[:-1]
            self.screen.fill((255, 255, 255))
            ren = self.font.render(prompt, 1, (0, 0, 0))
            self.screen.blit(ren, (self.screen_size[0]/2 - ren.get_width()/2, 
                self.screen_size[1]/2 - 32 - ren.get_height()/2))
            ren = self.font.render(text + "_", 1, (0, 0, 0))
            self.screen.blit(ren, (self.screen_size[0]/2 - ren.get_width()/2, 
                self.screen_size[1]/2 - ren.get_height()/2))
            pygame.display.flip()

class MapHud(object):
    
    def __init__(self, editor):
        self.editor = editor
        self.w = self.editor.screen_size[0]+48
        self.h = self.editor.screen_size[1]
        self.tw = self.th = 24
        self.map_list = ["Create New Map"]
        for name in glob.glob("data/maps/*.map"):
            self.map_list.append(name.split("/")[2][:-4])
        self.clicked = False
        
    def draw(self, screen):
        screen.fill((255, 255, 255))
        y = 16
        if pygame.mouse.get_pressed()[0]:
            self.clicked = True
        for i in self.map_list:
            ren = self.editor.font.render(i, 1, (0, 0, 0))
            rect = ren.get_rect(topleft=(16, y))
            screen.blit(ren, rect)
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, (255, 0, 0), (rect.x - 2, rect.y - 2, rect.w + 4, rect.h + 4), 1)
                if self.clicked:
                    pygame.draw.rect(screen, (0, 255, 0), (rect.x - 2, rect.y - 2, rect.w + 4, rect.h + 4), 1)
                if not pygame.mouse.get_pressed()[0] and self.clicked:
                    if y == 16:
                        name = self.editor.request_input("Name the map:")
                        self.map_list.append(name)
                    else:
                        self.editor.curr = LevelEditor(self.editor, "data/maps/%s.map" % i)
            y += self.editor.font.get_height()
        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False
        pygame.display.flip()
        
    def handle_input(self, events):
        pass
    
    def update(self):
        pass

class Layer:
    
    def __init__(self, editor):
        self.tiles = {}
        self.group = gameobject.Group()
        self.background = pygame.Surface(editor.editor.screen_size).convert_alpha()
        self.background.fill((0, 0, 0, 0))
        self.background.set_colorkey((0, 0, 0, 0), RLEACCEL)
    
    def draw_tile(self, t):
        self.background.fill((0, 0, 0, 0), t.rect)
        self.background.blit(t.template.image, t.rect)

    def erase_tile(self, t):
        self.background.fill((0, 0, 0, 0), t.rect)

    def erase_bg(self):
        self.background = pygame.Surface(self.background.get_size()).convert_alpha()
        self.background.fill((0, 0, 0, 0))
        self.background.set_colorkey((0, 0, 0, 0), RLEACCEL)

class LevelEditor(object):
    
    def __init__(self, editor, level_file):
        self.editor = editor
        self.layers = [Layer(self), Layer(self), Layer(self), Layer(self)]
        self.layer = 0
        self.templates = gameobject.Group()
        self.screen = editor.screen
        
        Template.groups = [self.templates]
        self.hud_h = 34
        
        config = open("editor.cfg", "rU").read()
        i = 1
        for item in config.split("\n"):
            key = item.split(": ")
            if len(key) == 2:
                t = Template(self, key[0], key[1], i, 0, 0)
                self.hud_h += 34
                i += 1
        
        self.tool = self.templates[0]
        self.tw, self.th = editor.tile_size
        self.gx, self.gy = 0, 0
        self.mw, self.mh = editor.screen_size
        self.grid_color = (200, 200, 200)
        self.hud_color = (150, 150, 150)
        self.hud_rect = Rect(self.mw, 0, self.screen.get_width()-self.mw, self.screen.get_height())
        self.mb = pygame.mouse.get_pressed()
        self.clock = pygame.time.Clock()
        self.hud_y = 0
        self.u_arrow = make_arrow()
        self.d_arrow = pygame.transform.flip(self.u_arrow, 0, 1)
        self.level_file = level_file
        self.can_add = True
        
        script = self.get_script()
        exec script
        self.info = Area()
        self.mw, self.mh = self.info.size
        
        try:
            self.load()
        except:
            pass

    def save(self):
        data = ""
        olayer = self.layer
        self.layer = 0
        for layer in self.layers:
            data += "layer" + str(self.layer) + "\n"
            for y in range(self.mh/self.th):
                for x in range(self.mw/self.tw):
                    added = False
                    if (x*self.tw, y*self.th) in self.layers[self.layer].tiles:
                        o = self.layers[self.layer].tiles[(x*self.tw, y*self.th)]
                        if o.pos == (x*self.tw, y*self.th):
                            data += o.name + " "
                            added = True
                    if not added:
                        data += "--- "
                data += "\n"
            self.layer += 1
        open(self.level_file, "wr").write(data)
        print "Saved level to:", self.level_file
        self.layer = olayer
        
    def load(self):
        for layer in self.layers:
            for o in layer.group:
                o.kill()
            layer.tiles = {}
        data = open(self.level_file, "rb").read()
        olayer = self.layer
        x = y = 0
        for row in data.split("\n"):
            if row.startswith("layer"):
                self.layer = int(row[-1:])
                x = y = 0
                continue
            for name in row.split(" "):
                if len(name) > 1:
                    for t in self.templates:
                        tn = t.name
                        create = False
                        if tn.endswith("%"):
                            if tn[:-1] == name[:-1]:
                                create = True
                        if t.name == name:
                            create = True
                        if create:
                            self.layers[self.layer].tiles[(x, y)] = Tile(t, (x, y), [self.layers[self.layer].group])
                            self.layers[self.layer].tiles[(x, y)].name = name
                            self.layers[self.layer].draw_tile(self.layers[self.layer].tiles[(x, y)])
                x += self.tw
            y += self.th
            x = 0
        print "Loaded level from:", self.level_file
        self.layer = olayer

    def get_script(self):
        fn = self.level_file.replace(".map", ".py")
        if os.path.exists(fn):
            script = open(fn, "rU").read()
            return script
        else:
            s = open("data/maps/template.py", "rU").read()
            open(fn, "w").write(s)
            return self.get_script()

    def handle_input(self, events):
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_s:
                    self.save()
                if e.key == K_l:
                    self.load()
                if e.key == K_b:
                    self.editor.curr = self.editor.maphud
                if e.key in [K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0]:
                    self.layer = int(e.unicode)-1
                if e.key == K_c:
                    for layer in self.layers:
                        for o in layer.group:
                            o.kill()
                        layer.tiles = {}
                        layer.erase_bg()
                i = 0
                for k in [K_UP, K_LEFT, K_DOWN, K_RIGHT]:
                    if e.key == k:
                        dx = dy = 0
                        if i == 0:
                            dy = -1
                        if i == 1:
                            dx = -1
                        if i == 2:
                            dy = 1
                        if i == 3:
                            dx = 1
                        self.layers[self.layer].tiles = {}
                        for t in self.layers[self.layer].group:
                            t.rect.x += self.tw*dx
                            t.rect.y += self.th*dy
                            t.pos = t.rect.topleft
                            self.layers[self.layer].tiles[t.rect.topleft] = t
                    i += 1
        
        self.mb = pygame.mouse.get_pressed()
        add = True
        mp = pygame.mouse.get_pos()
        if mp[0] > self.mw or mp[1] > self.mh:
            self.can_add = False
        if self.mb[0] and self.gx < self.mw and self.can_add:
            t = Tile(self.tool, (self.gx, self.gy), [self.layers[self.layer].group])
            if "%" in t.template.name:
                n = self.editor.request_input("Enter a number ID for the tile:", 1, "0123456789")
                t.name = t.name[:-1]
                t.name += n
                print t.name
            if (self.gx, self.gy) in self.layers[self.layer].tiles:
                t2 = self.layers[self.layer].tiles[(self.gx, self.gy)]
                if t.template.id != t2.template.id:
                    t2.kill()
            if (self.gx, self.gy) in self.layers[self.layer].tiles:
                if self.layers[self.layer].tiles[(self.gx, self.gy)].template.id == t.template.id:
                    t.kill()
                    self.layers[self.layer].background.fill((0, 0, 0, 0), t.rect)
                    self.layers[self.layer].draw_tile(t)
                    add = False
            if add:
                self.layers[self.layer].tiles[(self.gx, self.gy)] = t
                self.layers[self.layer].draw_tile(t)
                
        if self.mb[2] and self.gx < self.mw:
            for t in self.layers[self.layer].group:
                if t.rect.collidepoint(pygame.mouse.get_pos()):
                    t.kill()
                    if (t.rect.x, t.rect.y) in self.layers[self.layer].tiles:
                        self.layers[self.layer].erase_tile(t)
                        del self.layers[self.layer].tiles[(t.rect.x, t.rect.y)]

    def update(self):
        dt = self.clock.tick(60) / 1000.0
        mp = pygame.mouse.get_pos()
        self.gx = (mp[0]/self.tw) * self.tw
        self.gy = (mp[1]/self.th) * self.th
        
        if self.hud_rect.collidepoint(pygame.mouse.get_pos()):
            y = pygame.mouse.get_pos()[1]
            if y < 32 and self.hud_y < 0:
                self.hud_y += 600.0*dt
            if y > self.editor.screen_size[1]-32 and self.hud_y+self.hud_h > self.editor.screen_size[1]-34:
                self.hud_y -= 600.0*dt

    def draw(self, screen):
        self.screen.fill(self.info.floor_color)
        for x in range(self.mw/self.tw + 1):
            pygame.draw.line(self.screen, self.grid_color, (x*self.tw, 0), (x*self.tw, self.mh))
        for y in range(self.mh/self.th + 1):
            pygame.draw.line(self.screen, self.grid_color, (0, y*self.th), (self.mw, y*self.th))
        
        tr = Rect(self.gx, self.gy, self.tool.rect.w, self.tool.rect.h)
        tr.y += self.tool.offset
        
        mp = pygame.mouse.get_pos()
        self.can_add = True
        for layer in self.layers:
            '''for t in layer.group:
                dr = Rect(t.rect)
                dr.y += t.offset
                dr.w = t.template.image.get_width()
                dr.h = t.template.image.get_height()
                #self.screen.blit(t.template.image, dr)
                if pygame.key.get_pressed()[K_SPACE] and tr.colliderect(t.rect):
                    pygame.draw.rect(self.screen, (255, 0, 0), dr, 3)
                    self.can_add = False'''
            self.screen.blit(layer.background, (0, 0))
        
        self.screen.blit(self.tool.image, tr)
        pygame.draw.rect(self.screen, (255, 0, 0), tr, 1)
        
        self.screen.fill(self.hud_color, self.hud_rect)
        for t in self.templates:
            r = Rect(0, 0, 32, 32)
            hx = self.editor.screen_size[0]
            r.x = hx+8
            r.y = t.rect.y+8+self.hud_y
            dr = t.icon.get_rect(center = r.center)
            self.screen.blit(t.icon, dr)
            if t == self.tool:
                pygame.draw.rect(self.screen, (255, 255, 0), r, 1)
            if r.collidepoint(mp):
                pygame.draw.rect(self.screen, (255, 255, 255), r, 1)
                if self.mb[0]:
                    self.tool = t
        tr = Rect(self.hud_rect[0], 0, 48, 32)
        br = Rect(self.hud_rect[0], self.hud_rect.h-32, 48, 32)
        tc = (0, 0, 0)
        bc = (0, 0, 0)
        if tr.collidepoint(pygame.mouse.get_pos()):
            tc = (100, 100, 100)
        if br.collidepoint(pygame.mouse.get_pos()):
            bc = (100, 100, 100) 
        pygame.draw.rect(self.screen, tc, tr)
        pygame.draw.rect(self.screen, bc, br)
        self.screen.blit(self.u_arrow, (self.hud_rect[0]+12, 8))
        self.screen.blit(self.d_arrow, (self.hud_rect[0]+12, self.hud_rect.h-20))
        pygame.draw.rect(self.screen, (0, 0, 0), self.hud_rect, 1)
        ren = self.editor.font.render("Layer: " + str(self.layer+1), 1, (0, 0, 0), (255,255,255))
        self.screen.blit(ren, (0, self.editor.screen_size[1]-self.editor.font.get_height()))
        
        pygame.display.flip()

    def loop(self):
        self.running = True
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            
def main():
    editor = Editor((768, 720), (16, 16))
    editor.loop()

if __name__ == "__main__":
    main()
