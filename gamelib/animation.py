import pygame

class Animation:
   
    def __init__(self):
        self.images = {None: []}
        self.current_name = None
        self.image = None
        self.loops = 0
        self.frame = 0
        self.delay = 0
        self.num_loops = 0
        self.angle = 0
        self.draw_offset = (0, 0)
        self.facing = 1

    def add(self, name, images):
        self.images[name] = images
        if not self.image:
            self.image = self.images[name][0]
            self.create_surf(self.images[name][0].get_size())
            #self.animate(name, 0, -1)
    
    def create_surf(self, size):
        self.dimage = pygame.Surface(size).convert_alpha()
        self.dimage.fill((0, 0, 0, 0))
        self.dimage.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
   
    def animate(self, name, delay, loops, start_frame=0, restart=False):
        if self.current_name != name or restart:
            self.current_name = name
            self.loops = loops
            self.frame = 0
            self.num_loops = 0
            self.img_frame = start_frame
        self.anim_delay = delay
   
    def draw(self, screen, rect, offset, size):
        self.frame += 1
        if self.current_name != None:
            imgs_len = len(self.images[self.current_name])
            imgs = self.images[self.current_name]
            if self.anim_delay != 0:
                if self.frame >= self.anim_delay:
                    self.frame = 0
                    self.img_frame += 1
                if self.img_frame > len(imgs)-1:
                    self.img_frame = 0
                    self.num_loops += 1
                if self.num_loops > self.loops and self.loops > 0:
                    self.img_frame = len(imgs)-1
                self.image = imgs[self.img_frame]
            else:
                self.image = imgs[0]
            if self.facing < 0:
                self.image = pygame.transform.flip(self.image, 1, 0)
        self.dimage.fill((0, 0, 0, 0))
        if size != self.dimage.get_size():
            self.create_surf(size)
        self.dimage.blit(self.image, (0, 0))
        screen.blit(self.dimage, rect.move(*offset))
        if self.num_loops < self.loops and self.loops > -1:
            if self.frame >= len(self.images[self.current_name])*self.delay - 1:
                self.num_loops += 1
                self.on_animation_end()

    def on_animation_end(self):
        pass
