import pygame
import sys
import math
import neat
import pickle

FPS= 60
WIDTH= 1200
HEIGHT= 800
CAR_X= 30
CAR_Y= 30
BORDER_COLOR = (255, 255, 255, 255)
REWARD_COLOR1 = (255, 255, 0, 255)
REWARD_COLOR2 = (255, 100, 0, 255)
REWARD_COLOR3 = (100, 255, 0, 255)
MAP = "img/1.png"
MAPS = ["img/1.png","img/2.png","img/3.png","img/4.png"]
STARTING_OPTION = [[750, 700],[600, 520],[850, 600],[750, 350]]
STARTING_POS = [750, 700]
LOAD_WINNER = False
NUMBER_OF_GENERATIONS = 0

clock = pygame.time.Clock()

#CAR-------------------------------------------------------------------------------
class Car:
    def __init__(self):
        self.img= pygame.image.load("img/car.png")
        self.img = pygame.transform.scale(self.img, (CAR_X, CAR_Y))
        self.rotated_img= self.img
        
        self.position = [STARTING_POS[0], STARTING_POS[1]]
        self.angle = 0
        self.speed = 1
        self.speed_value = 1
        self.value = 1
        self.center = [self.position[0] + CAR_X / 2, self.position[1] + CAR_Y / 2]
        self.radars = [] 

        self.check_point = [0,0,0]
        self.reward_for_check_point = 0
        self.reward_multi = 1
        self.checked = True
        self.alive = True 

    def car_speed(self):
        if self.speed > 0:
            self.speed_value -= 0.05
        self.value = (.2 * self.speed) + ((1-.2) * self.speed_value)
        if self.speed_value > 8:
            self.speed_value = 8
        self.speed = self.value


    def draw(self, window):
        window.blit(self.rotated_img, self.position)
        self.draw_radar(window)

    def check_collision(self, map):
        self.alive = True
        for point in self.corners:
            if map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False

            if map.get_at((int(point[0]), int(point[1]))) == REWARD_COLOR1:
                self.check_point[0] = 1
                self.checked = False
                
            if map.get_at((int(point[0]), int(point[1]))) == REWARD_COLOR2:
                if self.check_point[0] == 1:
                    self.check_point[1] = 1
                    self.checked = False

            if map.get_at((int(point[0]), int(point[1]))) == REWARD_COLOR3:
                if self.check_point[0] == 1 and self.check_point[1] == 1:
                    self.check_point[2] = 1
                    self.checked = False
    
    def look_points(self):
        if self.checked == False:
            if self.check_point[0] == 1:
                self.reward_for_check_point = 5 * self.reward_multi
                if self.check_point[1] == 1:
                    self.reward_for_check_point = 10 * self.reward_multi
                    if self.check_point[2] == 1:
                        self.reward_for_check_point = 15 * self.reward_multi
                        self.reward_multi += 2
                        self.check_point[0] = 0
                        self.check_point[1] = 0
        self.checked = True

    def draw_radar(self, window):
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(window, (200, 0, 100), self.center, position, 1)
            pygame.draw.circle(window, (200, 0, 100), position, 5)

    def check_radar(self, degree, map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        while not map.get_at((x, y)) == BORDER_COLOR and length < 200:
            length += 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def get_data(self):
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1])
        return_values.append(self.speed_value)
        return return_values

    def update(self, map):

        self.rotated_img = self.rotate_center(self.img, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)

        self.center = [int(self.position[0]) + CAR_X / 2, int(self.position[1]) + CAR_Y / 2]

        length = 0.5 * CAR_X
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        self.check_collision(map)
        self.radars.clear()

        for d in range(-90, 120, 45):
            self.check_radar(d, map)

    def is_alive(self):
        return self.alive
    
    def rotate_center(self, image, angle):
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image

#MAIN RUN------------------------------------------------------------------------------
def start(genomes, number):
    nets = []
    cars = []
    map = pygame.image.load(MAP).convert()

    for i, gen in genomes:
        net = neat.nn.FeedForwardNetwork.create(gen, number)
        nets.append(net)
        gen.fitness = 0
        cars.append(Car())

    counter = 0
    while True:
        clock.tick(FPS)
        window.blit(map, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                car.angle += 10
            elif choice == 1:
                car.angle -= 10
            elif choice == 2:
                car.speed_value -= .5
            else:
                car.speed_value += .2

            #Test for moving
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_UP:
            #         car.speed_value += .1

            #     if event.key == pygame.K_DOWN:
            #         car.speed_value -= .2

        for car in cars:
            if car.is_alive():
                car.car_speed()
                car.draw(window)

        still_alive = 0
        for i, car in enumerate(cars):
            if counter > 200 and car.speed <= 1:
                car.alive = False
            if car.is_alive():
                still_alive += 1
                car.update(map)


                car.look_points()
                genomes[i][1].fitness += car.speed * .5
                genomes[i][1].fitness += car.reward_for_check_point


        if still_alive == 0:
            break
        
        if LOAD_WINNER == False:
            counter += 1
            if counter == 1000:
                break

        pygame.display.flip()

#---------------OPTIONS---------------------
def options():
    global MAP
    global STARTING_POS
    global LOAD_WINNER
    global NUMBER_OF_GENERATIONS

    try:
        pickle.load(open('winner.pkl', 'rb'))
        load_is_able = True
    except:
        load_is_able = False

    a = 361
    b = 605
    slider_height = 40

    while(True):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        pygame.draw.rect(window, (255,255,255), pygame.Rect(300, 250, 600, 350))
        mouse_pos= pygame.mouse.get_pos()
        
        loop_pos_x= 320
        for i in range(len(MAPS)):
            map_img = pygame.image.load(MAPS[i])
            map_img = pygame.transform.scale(map_img, (100,100))
            map_window = window.blit(map_img, (loop_pos_x,270))
            if map_window.collidepoint(mouse_pos):
                pygame.draw.rect(window,(0,255,0), pygame.Rect(loop_pos_x,270,100,100), 5)
                if event.type== pygame.MOUSEBUTTONDOWN:
                    MAP = MAPS[i]
                    STARTING_POS = [STARTING_OPTION[i][0],STARTING_OPTION[i][1]]

                    with open(config_path, 'r') as file:
                        lines = file.readlines()
                    for i, _ in enumerate(lines):
                        if 3 == i:
                            lines[i] = 'pop_size              = {}\n'.format(ilosc_aut)
                            break
                    with open(config_path, 'w') as file:
                        file.writelines(lines)
                    return
                
            loop_pos_x+= 150

        bar = pygame.draw.rect(window, "GRAY", pygame.Rect(350, 430, 200, slider_height))
        pygame.draw.rect(window, "RED", pygame.Rect(a, 435, 10, slider_height - 10))
        if bar.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                a = pygame.mouse.get_pos()[0] - 5
                if a < 361:
                    a = 361
                if a > 529:
                    a = 529
        ilosc_aut = a - 359
        text = myfont.render(f"Ilość aut: {ilosc_aut}", 10, (255,0,0))
        window.blit(text,(400,490))


        bar = pygame.draw.rect(window, "GRAY", pygame.Rect(600, 430, 200, slider_height))
        pygame.draw.rect(window, "RED", pygame.Rect(b, 435, 10, slider_height - 10))
        if bar.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                b = pygame.mouse.get_pos()[0] - 5
                if b < 605:
                    b = 605
                if b > 775:
                    b = 775
        NUMBER_OF_GENERATIONS = b - 604
        text = myfont.render(f"Ilość Generacji: {NUMBER_OF_GENERATIONS}", 10, (255,0,0))
        window.blit(text,(650,490))

        if load_is_able:
            if LOAD_WINNER == False:
                check_box = pygame.draw.rect(window, "RED", pygame.Rect(800, 550, 30, 30))
            else:
                check_box = pygame.draw.rect(window, "GREEN", pygame.Rect(800, 550, 30, 30))
            if check_box.collidepoint(mouse_pos):
                if event.type== pygame.MOUSEBUTTONDOWN:
                    if LOAD_WINNER == True:
                        LOAD_WINNER = False
                        pygame.time.wait(100)
                    else:
                        LOAD_WINNER = True
                        pygame.time.wait(100)
            text_load = myfont.render(f"Wczytaj:", 10, (255,0,0))
            window.blit(text_load,(730,550))


        pygame.display.update()

#---------------Run-----------------------
if __name__== "__main__":
    
    pygame.init()
    myfont = pygame.font.SysFont("monospace", 14)
    window= pygame.display.set_mode((WIDTH,HEIGHT))
    config_path = "config.txt"

    options()

    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    if (LOAD_WINNER):
        genome = pickle.load(open('winner.pkl', 'rb'))
        genomes = [(1, genome)]
        start(genomes, config)
    else:
        population = neat.Population(config)

        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)
    
        winner = population.run(start, NUMBER_OF_GENERATIONS)

        with open("winner.pkl", "wb") as f:
            pickle.dump(winner, f)
