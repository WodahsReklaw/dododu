
from imports import *

import root, game

def main():
    
    rgl.display.init(4.0, "RPG Project", GBRES)
    game_root = root.Root()
    game_root.start(game.Game)
    
    while True:
        
        rgl.clock.tick()
        rgl.button.handle_input()
        
        surface = rgl.display.get_surface()
        game_root.update(surface)
        rgl.display.update()
