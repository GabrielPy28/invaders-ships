import pygame
import random
import os
import time

# Window Settings
width, height = 650, 650
fps = 60
windows = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Invaders")
pygame.font.init()

# Load images
# Enemies
red_enemy = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
blue_enemy = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
green_enemy = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))

# Player
player = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))
player_gun = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Guns
red_laser = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
blue_laser = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
green_laser = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))

# Background
bg_game = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (width, height))

# Main Class
class Ship():
    cool_down = 30

    # Startup Attributes
    def __init__(self, x, y, health=100) -> None:
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.laser = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.laser:
            laser.draw(window)

    # Missed shot or Collision with the player
    def laser_collided(self, speed, obj):
        self.coolDown()

        for laser in self.laser:
            laser.laser_move(speed)
            if laser.off_screen(height):
                self.laser.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.laser.remove(laser)

    # Shooth Cool Down
    def coolDown(self):
        if self.cool_down_counter >= self.cool_down:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self): 
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.laser.append(laser)
            self.cool_down_counter = 1

    # Get object width and height attributes
    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

# Player Class
class Player(Ship):
    
    # Player Attributes
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = player
        self.laser_img = player_gun

        self.mask = pygame.mask.from_surface(self.ship_img)
        self.full_health = health

    # Drawing Currently Player Health
    def draw(self, window):
        super().draw(window)
        self.player_healthbar(window)

    def laser_collided(self, speed, objs):
        self.coolDown()

        for laser in self.laser:
            laser.laser_move(speed)
            if laser.off_screen(height):
                self.laser.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.laser:
                            self.laser.remove(laser)
    
    # Get the Player's Current Health and Lost Health
    def player_healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.full_health), 10))

# Enemy Class
class Enemy(Ship):
    """
    initializes the enemy object with a starting position x and y color and an optional health attribute.
    Set the enemy image and laser image using the enemy_map dictionary. Also creates a mask
    for the enemy object using the pygame.mask.from_surface method.
    """
    enemy_map = {
        'blue': (blue_enemy, blue_laser),
        'red': (red_enemy, red_laser),
        'green': (green_enemy, green_laser)
    }
    
    def __init__(self, x, y, color, health=100) -> None:
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.enemy_map[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    # Moves the enemy object upwards at a certain speed.
    def enemy_move(self, speed):
        self.y += speed

    # Creates a new laser object with the initial position of the enemy and adds it to the list of laser enemies. 
    # Also sets the cooldown counter to 1.
    def shoot(self): 
        if self.cool_down_counter == 0:
            laser = Laser(self.x-15, self.y, self.laser_img)
            self.laser.append(laser)
            self.cool_down_counter = 1

class Laser():
    """
    The Laser class represents a laser object that is fired by the enemy or the player. The __init__ method initializes the laser object with
    an initial xy position and a laser image. Also create a mask for the laser object using the
    pygame.mask.from_surfacemethod.
    """
    def __init__(self, x, y, laser_img) -> None:
        self.x = x
        self.y = y
        self.laser_img = laser_img
        self.mask = pygame.mask.from_surface(self.laser_img)

    # draws the laser object on the screen at its current position.
    def draw(self, window):
        window.blit(self.laser_img, (self.x, self.y))

    # The laser_move method moves the laser object upwards at a given speed.
    def laser_move(self, speed):
        self.y += speed

    # The off_screen method checks if the laser object is off screen and returns True if it is and False otherwise.
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)
    
    # Checks if the laser object has collided with another object obj by calling the collidedfunction and returns the result.
    def collision(self, obj):
        return collided(self, obj)

# Checks for collisions between two game objects.
def collided(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y

    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# Run Game
def run_game():
    run = True
    level = 0
    lives = 5
    player_speed = 5
    enemies_speed = 2
    laser_speed = 4
    game_lost = False
    game__lost_count = 0
    
    enemies = []
    speed_increase = 5


    player = Player(280, 530)
    font = pygame.font.SysFont("comicsans", 25)
    screen_lost_font = pygame.font.SysFont("comicsans", 45)
    clock = pygame.time.Clock()

    # Updating windows
    def redraw_windows():
        """
        This function is responsible for drawing all game objects on the screen, including the player's spaceship,
        enemy spaceships and any laser beams. It also shows the current level and lives on the screen.
        If the game is lost, it displays the message "You lost the game!!!" message on the screen.
        """
        lives_label = font.render(f"Lives: {lives}", 1, (255, 255, 255, 0.7))
        level_label = font.render(f"Level: {level}", 1, (255, 255, 255, 0.7))

        windows.blit(bg_game, (0, 0))
        windows.blit(lives_label, (15, 15))
        windows.blit(level_label, (width - level_label.get_width() - 15, 15))

        for enemy in enemies:
            enemy.draw(windows)

        player.draw(windows)

        if game_lost:
            label_game_lost = screen_lost_font.render("You Lost the Game!!!", 1, (255,255,255,0.7))
            windows.blit(label_game_lost, (width/2 - label_game_lost.get_width()/2, 325))
        
        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw_windows()

        if lives <= 0 or player.health <= 0:
            game_lost = True
            game__lost_count += 1

        """
        The game loop first checks if the player has lost the game. If the player has lost all their lives
        or if your health is zero, the game_lostvariable is set to True. If the game is lost, the script waits a few
        seconds before exiting the game.
        """
        if game_lost:
            if game__lost_count > fps*3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            speed_increase += 5
            for i in range(speed_increase):
                enemy = Enemy(random.randrange(50, width - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        keys = pygame.key.get_pressed()
        
        # Player Movement Keys.
        ## Left
        if keys[pygame.K_a] and player.x - player_speed > 0:
            player.x -= player_speed
        ## Right
        elif keys[pygame.K_d] and (player.x + player_speed + player.get_width()) < 650:
            player.x += player_speed
        ## Up
        elif keys[pygame.K_w] and (player.y - player_speed) > 50:
            player.y -= player_speed
        ## Down
        elif keys[pygame.K_s] and (player.y + player_speed + player.get_height()) < 650:
            player.y += player_speed

        ## Shoot
        if keys[pygame.K_SPACE]:
            player.shoot()
        
        for enemy in enemies[:]:
            enemy.enemy_move(enemies_speed)
            enemy.laser_collided(laser_speed, player)

            if random.randrange(0, 2*30) == 1: 
                enemy.shoot()

            if collided(enemy, player):
                player.health -=10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)

            
        player.laser_collided(-laser_speed, enemies)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

#  
def menu():

    """
    This function provides a simple title screen for the game that prompts the user to click on the
    mouse button to start the game. Uses Pygame's event handling mechanism to detect clicks from the
    mouse and start the game when the user clicks the mouse button.
    """
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        title_label = title_font.render("Mouse Click to Begin...", 1, (255, 255, 255, 0.6))

        windows.blit(bg_game, (0, 0))
        windows.blit(title_label, (width/2 - title_label.get_width()/2, 320))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                run_game()

    pygame.quit()

menu()