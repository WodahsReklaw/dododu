class Area:
    env = "town"
    floor_color = (170, 231, 105)
    doors = {
        }
    npcs = {
        }
    size = (512, 480)
    
    def get_actions(self, npc, game):
        actions = []
        events = game.events
        inv = game.inventory
        return actions

    def make_dialog(self, npc, text):
        return "DIALOG:" + npc.name + ": " + text

    def make_movement(self, npc, dist):
        return "MOVE:" + npc.name + ":" + str(dist[0]) + "," + str(dist[1])

    def make_face(self, npc, dir):
        return "FACE:" + npc.name + ": " + str(dir)

    def make_wait(self, ms):
        return "WAIT:" + str(ms)

