from ssl import enum_certificates
import ssl
from turtle import color, title
import pygame, os, time, random

pygame.font.init()      #Initialize font

FPS = 120
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

class Laser:
      def __init__(self, x, y, img):      #Positions and the img asset
            self.x, self.y, self.img = x, y, img
            self.mask = pygame.mask.from_surface(self.img)  #Masking for collision detection
      
      def draw(self, window):
            window.blit(self.img, (self.x, self.y))

      def move(self, vel):
            self.y += vel
      
      def off_screen(self, height):
            return not (self.y <= height and self.y >=  0)       # Returns True if laser is below screen
      
      def collision(self, obj):
            return collide(self, obj)     

class Ship:       # General class to inherit later for enemy and ownship
      COOLDOWN = FPS / 4      # Half a second per laser

      def __init__(self, x, y, health=100):
            self.x = x  #Ship position
            self.y = y
            self.health = health
            self.color = None
            self.ship_img = None
            self.laser_img = None
            self.lasers = []
            self.cool_down_counter = 0 #Laser cooldown counter

      def draw(self, window):
            #pygame.draw.rect(window, (255,0,0), (self.x, self.y, 50, 50))
            window.blit(self.ship_img, (self.x, self.y))

            for laser in self.lasers:     # Draw all the lasers
                  laser.draw(window)

      def move_lasers(self, vel, obj):
            self.cooldown()
            for laser in self.lasers:
                  laser.move(vel)
                  if laser.off_screen(HEIGHT):
                        self.lasers.remove(laser)
                  elif laser.collision(obj):          # If enemy laser hit player
                        obj.health -= 10
                        self.lasers.remove(laser)


      def cooldown(self):     # Handles counting cooldown
            if self.cool_down_counter >= self.COOLDOWN:     # If current counter is >= 120/2
                  self.cool_down_counter = 0                # Resets current counter
            elif self.cool_down_counter > 0:                
                  self.cool_down_counter += 1               # Increase counter

      def shoot(self):
            if self.cool_down_counter == 0:
                  laser = Laser(self.x, self.y, self.laser_img)
                  self.lasers.append(laser)
                  self.cool_down_counter = 1

      def get_width(self):
            return self.ship_img.get_width()

      def get_height(self):
            return self.ship_img.get_height()   
class Player(Ship):     # Inherit from Ship class
      def __init__(self, x, y, health=100):
            super().__init__(x, y, health)      # Access the methods from the object of the superclass Ship
            self.ship_img = YELLOW_SPACE_SHIP
            self.laser_img = YELLOW_LASER
            self.mask = pygame.mask.from_surface(self.ship_img)   # Masking for collision detection
            self.max_health = health

      def move_lasers(self, vel, objs):
            self.cooldown()
            for laser in self.lasers:     # Loop through each player's laser
                  laser.move(vel)
                  if laser.off_screen(HEIGHT):  # If laser is offscreen, remove it
                        self.lasers.remove(laser)
                  else: 
                        for obj in objs:  # Ojbs loop (Enemy ship)
                              if laser.collision(obj):          # If player laser hit enemy
                                    objs.remove(obj)               # Remove the obj(Enemy ship)
                                    if laser in self.lasers:
                                          self.lasers.remove(laser)

      def draw(self, window):
            super().draw(window)
            self.healthbar(window)

      def healthbar(self, window):
            pygame.draw.rect(window, (255,0,0), (self.x + self.ship_img.get_width() / 4, self.y + self.ship_img.get_height() + 7, self.ship_img.get_width() / 2, 5))
            pygame.draw.rect(window, (0,255,0), (self.x + self.ship_img.get_width() / 4, self.y + self.ship_img.get_height() + 7, self.ship_img.get_width() * (1 - (self.max_health - self.health)/self.max_health) / 2, 5))
class Enemy(Ship):
      COLOR_MAP = {
            "red": (RED_SPACE_SHIP, RED_LASER),       # Dictionary mapping key:value
            "green": (GREEN_SPACE_SHIP, GREEN_LASER),
            "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
      }

      def __init__(self, x, y, color, health=100):
            super().__init__(x, y, health)
            self.color = color
            self.ship_img, self.laser_img = self.COLOR_MAP[self.color]
            self.mask = pygame.mask.from_surface(self.ship_img)

      def shoot(self):
            if self.cool_down_counter == 0:
                  if self.color == "blue":                                 
                        laser = Laser(self.x - self.mask.get_size()[0]/2, self.y, self.laser_img)     # Different offset for blue laser
                  else:
                        laser = Laser(self.x - self.mask.get_size()[0]/4, self.y, self.laser_img)

                  self.lasers.append(laser)
                  self.cool_down_counter = 1

      def move(self, vel):
            self.y += vel

def collide(obj1, obj2):
      offset_x = obj2.x - obj1.x    #X Distance between two obj
      offset_y = obj2.y - obj1.y    #Y Distance between two obj
      return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None       # Returns (x, y) of intersection point if overlap otherwise None

def main():
      run = True
      level = 0
      lives = 5

      main_font = pygame.font.SysFont("comicsans", 30, False, False)     # (Font, Size, Bold, Italics)
      lost_font = pygame.font.SysFont("comicsans", 30, False, False)     # (Font, Size, Bold, Italics)

      enemies = []
      wave_length = 5
      enemy_vel = 1     #Downward wave

      player_vel = 5
      laser_vel = 4

      player = Player(300, 630)

      clock = pygame.time.Clock()

      lost = False
      lost_count = 0

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

            if lost:
                  lost_label = lost_font.render("You Lost!", 1, (255,255,255))
                  WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350) )  #Centering game over menu

            pygame.display.update()

      while run:
            clock.tick(FPS)

            redraw_window()   #Update the game window

            if lives <= 0 or player.health <= 0:      #Condition for losing
                  lost = True
                  lost_count += 1
            
            if lost:                
                  if lost_count > FPS * 3:       # Sec = FPS * Seconds
                        run = False              # Sets condition to exit out of while loop
                  else:
                        print(f"Game is paused at tick: {lost_count}" )
                        continue
            if len(enemies) == 0:   #Once num of enemies is 0, then increase level
                  level += 1
                  wave_length += 5
                  for i in range(wave_length):
                        enemy = Enemy( random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "green", "blue"]))
                        enemies.append(enemy)

            for event in pygame.event.get():    #Check for a user input (click or key press)
                  if event.type == pygame.QUIT: #Stop if event is QUIT
                        quit()
                        
            keys = pygame.key.get_pressed()     #Return a dict of pressed keys

            if keys[pygame.K_a] and (player.x - player_vel) > 0: # Move left
                  player.x -= player_vel
            if keys[pygame.K_d] and (player.x + player_vel + player.get_width() ) < WIDTH: # Move right
                  player.x += player_vel
            if keys[pygame.K_w] and (player.y - player_vel) > 0: # Move up
                  player.y -= player_vel
            if keys[pygame.K_s] and (player.y + player_vel + player.get_height() ) < HEIGHT - 10: # Move down
                  player.y += player_vel
            if keys[pygame.K_SPACE]:
                  player.shoot()

            for enemy in enemies[:]:      # Enemies[:] returns a list copy of all enemy's
                  enemy.move(enemy_vel)
                  enemy.move_lasers(laser_vel, player)

                  if random.randrange(0, 2*FPS) == 1:
                        enemy.shoot()

                  if collide(enemy, player):    # If enemy & player ship collide
                        player.health -= 10
                        enemies.remove(enemy)
                  elif enemy.y + enemy.get_height() > HEIGHT: # If enemy hits bottom of screen, player loses 1 life.
                        lives -= 1
                        enemies.remove(enemy)   # Remove enemy object from the enemies list copy and not original enemies

            player.move_lasers(-laser_vel, enemies)   #Neg vel so  it fires upward
      print("Game over")

def main_menu():
      title_font = pygame.font.SysFont("comicsans", 30)
      run = True
      while run:
            WIN.blit(BG, (0,0))
            title_label = title_font.render("Press the mouse to begin ...", 1, (255,255,255))
            WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
            pygame.display.update()

            for event in pygame.event.get():
                  if event.type == pygame.QUIT:
                        run = False
                  if event.type == pygame.MOUSEBUTTONDOWN:
                        main()
      pygame.quit()

main_menu()


