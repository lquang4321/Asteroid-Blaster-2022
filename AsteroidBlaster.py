from ssl import enum_certificates
from turtle import color
import pygame, os, time, random

pygame.font.init()      #Initialize font

WIDTH, HEIGHT = 750, 750      #Window resolution
WIN = pygame.display.set_mode( (WIDTH, HEIGHT) )
pygame.display.set_caption("Asteroid Blaster")

#Load assets .PNG
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

#Player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

#Lasers
RED_LASER = pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))

#Background image
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")) , (WIDTH, HEIGHT) ) #Load BG image, and scale to Win resolution

class Ship:       #General class to inherit later for enemy and ownship
      def __init__(self, x, y, health=100):
            self.x = x  #Ship position
            self.y = y
            self.health = health
            self.ship_img = None
            self.laser_img = None
            self.lasers = []
            self.cool_down_counter = 0 #Laser cooldown counter

      def draw(self, window):
            #pygame.draw.rect(window, (255,0,0), (self.x, self.y, 50, 50))
            window.blit(self.ship_img, (self.x, self.y))

      def get_width(self):
            return self.ship_img.get_width()

      def get_height(self):
            return self.ship_img.get_height()   
class Player(Ship):     #Inherit from Ship class
      def __init__(self, x, y, health=100):
            super().__init__(x, y, health)      #Access the methods from the object of the superclass Ship
            self.ship_img = YELLOW_SPACE_SHIP
            self.laser_img = YELLOW_LASER
            self.mask = pygame.mask.from_surface(self.ship_img)   #Masking for collision detection
            self.max_health = health
            
class Enemy(Ship):
        COLOR_MAP = {
            "red": (RED_SPACE_SHIP, RED_LASER),       #Dictionary mapping key:value
            "green": (GREEN_SPACE_SHIP, GREEN_LASER),
            "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
        }

        def __init__(self, x, y, color, health=100):
            super().__init__(x, y, health)
            self.ship_img, self.laser_img = self.COLOR_MAP[color]
            self.mask = pygame.mask.from_surface(self.ship_img)

        def move(self, vel):
            self.y += vel

def main():
      run = True
      FPS = 120
      level = 0
      lives = 5
      main_font = pygame.font.SysFont("comicsans", 20, False, False)     # (Font, Size, Bold, Italics)
      
      enemies = []
      wave_length = 5
      enemy_vel = 1     #Downward wave

      player_vel = 5

      player = Player(300, 650)

      clock = pygame.time.Clock()

      def redraw_window():
            WIN.blit(BG, (0,0))
            #Draw text
            level_label = main_font.render(f"Level: {level}", 1,(255,255,255))     
            lives_label = main_font.render(f"Lives:{lives}", 1, (255,255,255))     

            WIN.blit(lives_label, (10,10))      #Display at top left
            WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10)) #Display at top right
            
            for enemy in enemies:
                  enemy.draw(WIN)

            player.draw(WIN)

            pygame.display.update()

      while run:
            clock.tick(FPS)

            if len(enemies) == 0:   #Once num of enemies is 0, then increase level
                  level += 1
                  wave_length += 5
                  for i in range(wave_length):
                        enemy = Enemy( random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "green", "blue"]))
                        enemies.append(enemy)

            for event in pygame.event.get():    #Check for a user input (click or key press)
                  if event.type == pygame.QUIT: #Stop if event is QUIT
                        run = False
                        
            keys = pygame.key.get_pressed()     #Return a dict of pressed keys

            if keys[pygame.K_a] and (player.x - player_vel) > 0: # Move left
                  player.x -= player_vel
            if keys[pygame.K_d] and (player.x + player_vel + player.get_width() ) < WIDTH: # Move right
                  player.x += player_vel
            if keys[pygame.K_w] and (player.y - player_vel) > 0: # Move up
                  player.y -= player_vel
            if keys[pygame.K_s] and (player.y + player_vel + player.get_height() ) < HEIGHT: # Move down
                  player.y += player_vel

            for enemy in enemies:
                  enemy.move(enemy_vel)

            redraw_window()   #Update background
main()


