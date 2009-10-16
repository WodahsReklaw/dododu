
import objects, os

class MapLoader(object):
    
    def __init__(self, game, w=32, h=30, tw=16, th=16):
        self.game = game
        self.tile_width = tw
        self.tile_height = th
        self.width = w
        self.height = h

    def parse(self, file_name):
        self.file_name = file_name
        data = open(file_name, "rU").read()
        data = data.replace("\r", "")
        script = self.get_script()
        exec script
        self.info = Area()
        self.width = self.info.size[0] / self.tile_width
        self.height = self.info.size[1] / self.tile_height
        self.map = []
        for y in range(self.height):
            n = []
            for x in range(self.width):
                n.append(None)
            self.map.append(n)
        x = y = 0
        layer = 0
        for row in data.split("\n"):
            if row.startswith("layer"):
                layer = int(row[-1:])
                x = y = 0
                continue
            for char in row.split(" "):
                self.on_char(char, x, y, layer)
                x += 1
            y += 1
            x = 0

    def on_char(self, char, x, y):
        pass

    def set_tile(self, object):
        x = int(object.rect.x / self.tile_width)
        y = int(object.rect.y / self.tile_height)
        self.map[y][x] = object
        
    def get_script(self):
        fn = self.file_name.replace(".map", ".py")
        script = open(fn, "rU").read()
        return script

class GameMap(MapLoader):
    
    def on_char(self, char, x, y, layer):
        gx, gy = x, y
        x = x*self.tile_width
        y = y*self.tile_height
        if char == "GRS":
            objects.Scenery(self.game, x, y, "grass.png")
        if char == "WTR":
            objects.Scenery(self.game, x, y, "water.png")
        if char == "SND":
            objects.Scenery(self.game, x, y, "sand.png")
        if char == "TRT":
            self.set_tile(objects.Scenery(self.game, x, y, "tree-top.png"))
        if char == "TRM":
            self.set_tile(objects.Scenery(self.game, x, y, "tree-middle.png"))
        if char == "TRB":
            self.set_tile(objects.Scenery(self.game, x, y, "tree-bottom.png"))
        if char == "HLL":
            objects.Scenery(self.game, x, y, "hill.png")
        if char == "BRV":
            objects.Obstacle(self.game, x, y, "bridge-vertical.png").sides = [False, True, False, True]
        if char == "BRH":
            objects.Obstacle(self.game, x, y, "bridge-horizontal.png").sides = [True, False, True, False]
        if char == "CSL":
            objects.Obstacle(self.game, x, y, "castle.png")
        if char == "MTN":
            objects.Obstacle(self.game, x, y, "mountain-center.png")
        if char == "MNT":
            objects.Obstacle(self.game, x, y, "mountain-top.png")
        if char == "MNB":
            objects.Obstacle(self.game, x, y, "mountain-bottom.png")
        if char == "MNL":
            objects.Obstacle(self.game, x, y, "mountain-left.png")
        if char == "MNR":
            objects.Obstacle(self.game, x, y, "mountain-right.png")
        if char == "MTL":
            objects.Obstacle(self.game, x, y, "mountain-topleft.png")
        if char == "MTR":
            objects.Obstacle(self.game, x, y, "mountain-topright.png")
        if char == "MBL":
            objects.Obstacle(self.game, x, y, "mountain-bottomleft.png")
        if char == "MBR":
            objects.Obstacle(self.game, x, y, "mountain-bottomright.png")
        if char == "SHT":
            objects.Obstacle(self.game, x, y, "shore-top.png")
        if char == "SHB":
            objects.Obstacle(self.game, x, y, "shore-bottom.png")
        if char == "SHL":
            objects.Obstacle(self.game, x, y, "shore-left.png")
        if char == "SHR":
            objects.Obstacle(self.game, x, y, "shore-right.png")
        if char == "STL":
            objects.Obstacle(self.game, x, y, "shore-topleft.png")
        if char == "STR":
            objects.Obstacle(self.game, x, y, "shore-topright.png")
        if char == "SBL":
            objects.Obstacle(self.game, x, y, "shore-bottomleft.png")
        if char == "SBR":
            objects.Obstacle(self.game, x, y, "shore-bottomright.png")
        if char == "CLB":
            objects.Obstacle(self.game, x, y, "cliff-bottom.png")
        if char == "CLL":
            objects.Obstacle(self.game, x, y, "cliff-left.png").sides = [False, True, False, False]
        if char == "CLR":
            objects.Obstacle(self.game, x, y, "cliff-right.png").sides = [False, False, False, True]
        if char == "CTL":
            objects.Obstacle(self.game, x, y, "cliff-topleft.png").sides = [True, True, False, False]
        if char == "CTR":
            objects.Obstacle(self.game, x, y, "cliff-topright.png").sides = [True, False, False, True]
        if char == "CLT":
            objects.Obstacle(self.game, x, y, "cliff-top.png").sides = [True, False, False, False]
        if char.startswith("CH"):
            id = int(char[-1:])
            objects.Chest(self.game, x, y, id)
        if char.startswith("NP"):
            id = int(char[-1:])
            name = self.info.npcs[id][0]
            npc = objects.NPC(self.game, x, y, name)
            if npc.name in self.game.npc_cache:
                npc.set_pos_to(self.game.npc_cache[npc.name])
                self.game.npc_cache[npc.name] = npc
            else:
                self.game.npc_cache[npc.name] = npc
        if char.startswith("IT"):
            id = int(char[-1:])
            name, id = self.info.items[id]
            if name in self.game.inventory:
                if self.game.inventory[name][0] == id:
                    return
            objects.Item(self.game, x, y, name, id)
