import pygame
import neat
import os
import time

#window frame constants
WIN_WIDTH = 560
WIN_HEIGHT = 800

#images
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))


#creating the bird class
class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5

    #initiating variables in the class (sort of like the starting identity of the bird)
    def __init__(self, x, y): #the function __init__ whenever the class is called with paremeters it brings it directly to the init paramters
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]


    #responsible for making the bird jump
    def jump(self):
        self.velocity = -10.5 #its negative as the bird is constantly wanting to fall down
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        #formula for downward acceleration
        displacement = self.velocity * self.tick_count + 1.5 * self.tick_count ** 2

        #terminal velocity 
        if displacement >= 16:
            displacement = 16

        if displacement < 0:
            displacement -= 2

        #updating the y-axis
        self.y = self.y + displacement

        #tilts the bird up, otherwise down
        if displacement < 0 or self.y < self.height + 50:  
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else: 
            if self.tilt > -90:
                self.tilt -= self.ROTATION_VELOCITY

    def draw(self, window):
        self.img_count += 1

        #animating the bird flying
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME *2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME *3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME *4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME *4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME *2

        #hitbox for the bird
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rectangle = rotated_image.get_rect(center = self.img.get_rect(x = self.x, y = self.y).center)
        window.blit(rotated_image, new_rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


def draw_window(win,bird):           #paremeters are the inputs the function requires
    win.blit(BG_IMG,(0,0))     #0,0 takes the bottom left corner of x, y            #blit is draw function requiring different paremeters, draws the bg img + location
    bird.draw(win)           #attaching the bird to window
    pygame.display.update()     #updating frames

def main(): 
    bird = Bird(200,200)
    window = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(30)   #30 frames per second
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        #bird.move()
        draw_window(window,bird)

if __name__ == "__main__":
    main()
