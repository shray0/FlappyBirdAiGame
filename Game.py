import pygame
import neat
import os
import time
import random
pygame.font.init()

#window frame constants
WIN_WIDTH = 560
WIN_HEIGHT = 800

#images
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
GEN = 0
STAT_FONT = pygame.font.SysFont("arial",50)

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

class Pipe:
    GAP = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, window):
        # draw top and bottom
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    #returns true or false based on whether a collisions is detected
    def collide(self, bird, window):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        top_point = bird_mask.overlap(top_mask,top_offset)
        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)

        if top_point or bottom_point:
            return True

        return False

class Base:
    VELOCITY = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG
    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY
        if self.x1 + self.WIDTH<0:
            self.x1 = self.x2 + self.WIDTH 
        if self.x2 + self.WIDTH<0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1,self.y))
        win.blit(self.IMG, (self.x2,self.y))

    


def draw_window(win,birds,pipes,base,score,gen):           #paremeters are the inputs the function requires
    win.blit(BG_IMG,(0,0))     #0,0 takes the bottom left corner of x, y            #blit is draw function requiring different paremeters, draws the bg img + location
    for bird in birds:
        bird.draw(win)           #attaching the bird to window
    for pipe in pipes:
        pipe.draw(win)
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(),10))
    text = STAT_FONT.render("Gen: " + str(gen), 1, (255,255,255))
    win.blit(text, (10,10))
    base.draw(win)
    
    pygame.display.update()     #updating frames

def main(genomes,config): 
    global GEN 
    GEN += 1
    networks = []
    genomes = []
    score = 0
    birds = []
    pipes = [Pipe(600)]
    base = Base(730)
    window = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock = pygame.time.Clock()
    run = True
    for _,g in genomes:
        network = neat.nn.FeedForwardNetwork.create(g,config)
        networks.append(network)
        birds.append(Bird(230,350))
        g.fitness = 0
        genomes.append(g)
    while run:
        clock.tick(30)   #30 frames per second
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_index = 1 #might be += 1
        else: 
            run = False #shuts down code
            break #stops loop from running
        for x,bird in enumerate(birds): #enumarate has one variable, in this case x keeping track of index, and bird keeping of value
            bird.move()
            genomes[x].fitness += 0.1  #for every frame it survives, it has higher fitness
            output = networks[x].activate((bird.y,abs(bird.y - pipes[pipe_index].height),abs(bird.y - pipes[pipe_index].bottom))) #the movement output is the decision based on the neural network
            if output[0] > 0.5: #comeback to absolute value part
                bird.jump()

        remove = []
        add_pipe = False
        for pipe in pipes:
            for x,bird in enumerate(birds): 
                if pipe.collide(bird,window):
                    genomes[x].fitness -= 1 #makes the model of the bird that collides less fit to the ideal model
                    birds.pop(x) #removes the collided bird from index
                    networks.pop(x) #removes from network
                    genomes.pop(x) #removes from generation of birds
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width()<0:
                remove.append(pipe)
            
            pipe.move()
        if add_pipe:
            score += 1
            for genome in genomes:
                genome.fitness += 5
            pipes.append(Pipe(600))
        for r in remove:
            pipes.remove(r)
        for x,bird in enumerate(birds):
            if bird.y + bird.img.get_height()>= 730 or bird.y < 0: #if it goes too high it is a bad model
                birds.pop(x)
                networks.pop(x)
                genomes.pop(x)
                
        base.move()
        draw_window(window,birds,pipes,base,score,GEN)
    

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,neat.DefaultSpeciesSet, neat.DefaultStagnation,config_path)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(main, 50)     

if __name__ == "__main__":
    #main(,50)
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config_feedforward.txt') #data for neural network
    run(config_path)

