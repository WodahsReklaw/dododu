
from imports import *

import state, objects, maploader

class ActionHandler(object):
    
    def __init__(self, game):
        self.game = game
        self.pos = 0
        self.dialog = rgl.dialog.DialogBox((240, 51), (0, 0, 0), (255, 255, 255), self.game.font)
        self.dialog.close()
        self.seq = []
        self.set_d = ""
        self.acting = False
        self.npc_start = None
        self.wait_timer = None
    
    def update(self):
        self.acting = False
        if self.pos < len(self.seq):
            self.acting = True
            self.cur = self.seq[self.pos]
            if self.cur.startswith("DIALOG:"):
                d = self.cur.replace("DIALOG:", "")
                if self.set_d != d:
                    self.dialog.set_dialog([self.cur.replace("DIALOG:", "")])
                    while self.dialog.curr_dialog[self.dialog.text_pos] != ":":
                        self.dialog.text_pos += 1
                    self.set_d = d
                if self.dialog.over():
                    self.pos += 1
            if self.cur.startswith("MOVE:"):
                d = self.cur.split(":")
                name = d[1]
                for n in self.game.npcs:
                    if n.name == name:
                        self.npc = n
                p = d[2].split(",")
                if not self.npc_start:
                    self.npc_start = self.npc.rect.topleft
                pos = (int(p[0])+self.npc_start[0], int(p[1])+self.npc_start[1])
                if self.npc.rect.x != pos[0] or self.npc.rect.y != pos[1]:
                    if self.npc.rect.x > pos[0]:
                        self.npc.walk(-1, 0)
                    if self.npc.rect.x < pos[0]:
                        self.npc.walk(1, 0)
                    if self.npc.rect.y > pos[1]:
                        self.npc.walk(0, -1)
                    if self.npc.rect.y < pos[1]:
                        self.npc.walk(0, 1)
                else:
                    self.npc_start = None
                    self.pos += 1
            if self.cur.startswith("FACE:"):
                d = self.cur.split(":")
                name = d[1]
                for n in self.game.npcs:
                    if n.name == name:
                        self.npc = n
                dir = int(d[2])
                if dir == 4:
                    self.npc.face(self.game.player)
                else:
                    self.npc.facing = dir
                self.pos += 1
            if self.cur.startswith("WAIT:"):
                d = self.cur.split(":")
                ms = int(d[1])
                if not self.wait_timer:
                    self.wait_timer = ms
                self.wait_timer -= 1
                if self.wait_timer <= 0:
                    self.wait_timer = None
                    self.pos += 1
        
    def read_actions(self, sequence):
        self.seq = sequence
        self.pos = 0
        self.set_d = ""
    
    def running(self):
        return self.acting

class Game(state.State):
    
    def __init__(self, root):
        state.State.__init__(self, root)
        self.objects = rgl.gameobject.Group()
        self.scenery = rgl.gameobject.Group()
        self.collidables = rgl.gameobject.Group()
        self.doors = rgl.gameobject.Group()
        self.npcs = rgl.gameobject.Group()
        self.items = rgl.gameobject.Group()
        self.players = rgl.gameobject.Group()
        
        objects.GameObject.collision_objects = self.collidables
        objects.Player.groups = [self.objects, self.players]
        objects.Scenery.groups = [self.scenery]
        objects.Obstacle.groups = [self.objects, self.collidables]
        objects.Door.groups = [self.objects, self.doors]
        objects.NPC.groups = [self.objects, self.npcs, self.collidables]
        objects.Chest.groups = [self.objects, self.items]
        objects.Water.groups = [self.objects]
        
        self.events = {
            "gun_quest": 0,
        }
        self.inventory = {
        }
        self.npc_cache = {}
        
        self.camera = Rect(0, 0, 160, 144)
        self.camera_xbounds = 16
        self.camera_ybounds = 16
        self.player = objects.Player(self, 2)
        self.map = maploader.GameMap(self)
        self.map.parse("data/maps/world-map.map")
        self.world_rect = Rect(0, 0, self.map.info.size[0], self.map.info.size[1])
        self.make_background()
        self.font = rgl.font.Font(NES_FONT)
        self.action_handler = ActionHandler(self)
    
    def make_background(self):
        self.camera.topleft = (0, 0)
        self.background = pygame.Surface(self.world_rect.size)
        self.background.fill(self.map.info.floor_color)
        for o in self.scenery:
            o.draw(self.background, self.camera)
    
    def enter_area(self, name, player_dest):
        for o in self.objects:
            if not isinstance(o, objects.Player):
                o.kill()
        for o in self.scenery:
            o.kill()
        self.map.parse("data/maps/" + name + ".map")
        self.world_rect.size = self.map.info.size
        for p in self.players:
            p.rect.topleft = player_dest
            p.steps = []
        self.make_background()
        
    def enter_door(self, door):
        dest_name = self.map.info.doors[door.id][0]
        dr = self.map.info.doors[door.id]
        print dr
        self.enter_area(dest_name, (0, 0))
        for d in self.doors:
            if d.id == dr[1]:
                side = dr[2]
                if side == "top":
                    self.player.rect.bottomleft = d.rect.topleft
                if side == "bottom":
                    self.player.rect.topleft = d.rect.bottomleft
                if side == "left":
                    self.player.rect.topright = d.rect.topleft
                if side == "right":
                    self.player.rect.topleft = d.rect.topright
        for p in self.players:
            p.rect.topleft = self.player.rect.topleft
            p.steps = []
            
    def handle_input(self):
        if not self.action_handler.running() and self.action_handler.dialog.over():
            running = False
            if rgl.button.is_held(B_BUTTON):
                running = True
            if rgl.button.is_held(UP):
                self.player.walk(0, -1, running)
            elif rgl.button.is_held(DOWN):
                self.player.walk(0, 1, running)
            elif rgl.button.is_held(LEFT):
                self.player.walk(-1, 0, running)
            elif rgl.button.is_held(RIGHT):
                self.player.walk(1, 0, running)
        if not self.action_handler.dialog.over():
            if rgl.button.is_pressed(A_BUTTON):
                self.action_handler.dialog.progress()
                rgl.button.handle_input()

    def update(self, surface):
        
        self.handle_input()
        self.action_handler.update()
        for o in self.objects:
            o.update()
        
        if not self.action_handler.running() and self.action_handler.dialog.over():
            for d in self.doors:
                if self.player.rect.colliderect(d.rect):
                    self.enter_door(d)
            for n in self.npcs:
                if self.player.rect.colliderect(n.bounds):
                    if rgl.button.is_pressed(A_BUTTON):
                        self.action_handler.read_actions(self.map.info.get_actions(n, self))
                        self.player.face(n)
            for i in self.items:
                if self.player.rect.colliderect(i.rect):
                    if rgl.button.is_pressed(A_BUTTON):
                        self.inventory[i.name] = [i.id, 1]
                        i.kill()
                        self.action_handler.dialog.set_dialog(["You found a " + i.name + "!"])
        
        if self.player.rect.centerx < self.camera.centerx-self.camera_xbounds:
            self.camera.centerx = self.player.rect.centerx+self.camera_xbounds
        if self.player.rect.centerx > self.camera.centerx+self.camera_xbounds:
            self.camera.centerx = self.player.rect.centerx-self.camera_xbounds
        if self.player.rect.centery < self.camera.centery-self.camera_ybounds:
            self.camera.centery = self.player.rect.centery+self.camera_ybounds
        if self.player.rect.centery > self.camera.centery+self.camera_ybounds:
            self.camera.centery = self.player.rect.centery-self.camera_ybounds
        self.camera.clamp_ip(self.world_rect)
        self.player.rect.clamp_ip(self.world_rect)
        
        surface.blit(self.background, (-self.camera.x, -self.camera.y))
        for o in self.objects:
            o.draw(surface, self.camera)
        self.action_handler.dialog.draw(surface, (8, 8))
