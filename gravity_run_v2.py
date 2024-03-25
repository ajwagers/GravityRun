import pygame
import random
import math
import numpy as np


# Initialize Pygame
pygame.init()

# Initialize the font module
pygame.font.init()

# Set up the game window in fullscreen mode
window_info = pygame.display.Info()
WINDOW_WIDTH = 1200 #window_info.current_w
WINDOW_HEIGHT = 800 #window_info.current_h
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) #, pygame.FULLSCREEN)
wall_wrap = False
default_font = pygame.font.SysFont("consolas",56)
scorefont = pygame.font.SysFont("consolas", int(WINDOW_HEIGHT * 0.05))
#imgMeteor1 = pygame.image.load('./artwork/spaceMeteors_001.png')
pygame.display.set_caption("Gravity Run")

# Colors for stars
STAR_COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (255, 255, 255), (173, 216, 230), (0, 191, 255)]

# Star layers
STAR_LAYERS = [
    {"speed": 0, "max_size": 1, "elongation": 1, "star_count": 200},    # Stationary background layer
    {"speed": 0.1, "max_size": 1, "elongation": 1.25, "star_count": 100},
    {"speed": 0.25, "max_size": 2, "elongation": 1.25, "star_count": 30},
    {"speed": 0.5, "max_size": 3, "elongation": 1.25, "star_count": 15},
    {"speed": 1, "max_size": 4, "elongation": 1.25, "star_count": 8}
]

def load_level_high_scores():
    try:
        with open("level_high_scores.txt", "r") as file:
            level_high_scores = int(file.read())
    except (FileNotFoundError, ValueError):
        level_high_scores = [0] 

    return level_high_scores

def save_level_high_scores(level_high_scores):
    with open("level_high_scores.txt", "w") as file:
        file.write(str(score))

def load_arcade_high_score():
    try:
        with open("arcade_high_score.txt", "r") as file:
            arcade_high_score = int(file.read())
    except (FileNotFoundError, ValueError):
        arcade_high_score = 0

    return arcade_high_score

def save_arcade_high_score(score):
    with open("arcade_high_score.txt", "w") as file:
        file.write(str(score))

def main():
    star_layers = init_star_layers()

    # Set the initial state to "menu"
    game_state = "menu"
    game_mode = None

    while True:
        if game_state == "menu":
            # Handle menu events and display the menu
            game_mode = show_menu(window)
            if game_mode == "quit":
                break
        elif game_state == "game":
            if game_mode == "infinite":
                # Run the infinite game loop
                infinite_play_loop(window, star_layers)
            elif game_mode == "level":
                # Run the level game loop
                play_game_loop(window, star_layers)
            elif game_mode == "instructions":
                game_state = "instructions"
            # Add more game modes here if needed

        if game_state == "quit":
            break

    # Quit the game
    pygame.quit()

# Initialize star layers
def init_star_layers():
    star_layers = []
    for layer in STAR_LAYERS:
        stars = []
        for _ in range(layer["star_count"]):  # Adjust the number of stars per layer
            x = random.randrange(WINDOW_WIDTH)
            y = random.randrange(WINDOW_HEIGHT)
            size = random.randint(1, layer["max_size"])
            elongated_size = (size, int(size * layer["elongation"]))
            base_color = random.choice(STAR_COLORS)
            color_factor = (255 - layer["star_count"])/255
            color = (int(base_color[0] * color_factor), int(base_color[1] * color_factor), int(base_color[2] * color_factor))
            stars.append({"x": x, "y": y, "size": elongated_size, "color": color})
        star_layers.append(stars)
    return(star_layers)

def update_star_layers(star_layers,window,large_mass_object=None,large_mass_stopped=False):
    # Draw stars
    for i, layer in enumerate(star_layers):
        for star in layer:
            # Apply circular motion if the star is within a certain range
            if large_mass_object and large_mass_stopped:
                distance_to_mass = large_mass_object.get_distance_to_star(star)
                if distance_to_mass <= 800:  # Adjust this value to change the range
                    angle = math.atan2(star["y"] - large_mass_object.rect.centery, star["x"] - large_mass_object.rect.centerx)
                    orbital_speed = 1  # Adjust this value to change the orbital speed
                    star["x"] += orbital_speed * math.sin(angle)
                    star["y"] += orbital_speed * math.cos(angle) * (-1)
                elif distance_to_mass > 400:
                    star["x"] = star["x"]
                    star["y"] = star["y"]
            else:
                star["y"] += STAR_LAYERS[i]["speed"]  # Move stars based on layer speed

                if star["y"] > WINDOW_HEIGHT + star["size"][1]:  # respawn if star goes off-screen
                    star["y"] = -star["size"][1]
                    star["x"] = random.randrange(WINDOW_WIDTH)
                    star["color"] = random.choice(STAR_COLORS)
        
            pygame.draw.rect(window, star["color"], (star["x"], star["y"], star["size"][0], star["size"][1]))

def generate_random_layout(num_rows, offset_range):
    layout = []
    for row in range(num_rows):
        size = int(random.uniform(30, 60))
        x_offset = random.uniform(-offset_range, offset_range)
        y_pos = -size - 30 - (row * 200)  # Adjust the vertical spacing as needed
        speed_rand = random.gauss(0.5,1.2)
        layout.append({"size": size, "x": int(WINDOW_WIDTH // 2 + x_offset - size), "y": y_pos, "speed_y": speed_rand})
    return layout

class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 60))
        image_file = "./artwork/spaceRockets_002.png"
        image = pygame.image.load(image_file).convert_alpha()
        image = pygame.transform.scale(image, (30, 60))
        self.image_width, self.image_height = self.image.get_size()
        #self.image.fill((255, 255, 255))
        self.image.blit(image, (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = WINDOW_WIDTH // 2
        self.rect.y = WINDOW_HEIGHT // 2
        self.speed_x = 0
        self.speed_y = 0
        self.acceleration = 0.02
        self.max_speed = 2
        self.mass = 30
    
    #def check_collisions(self, gravity_objects):
    #    collision_list = pygame.sprite.spritecollide(self, gravity_objects, False)
    #    if collision_list:
    #        for gravity_object in collision_list:
    #            # Adjust the spaceship's position to avoid collision
    #            while pygame.sprite.collide_rect(self, gravity_object):
    #                self.rect.x += 1
    #                self.rect.y += 1

    def apply_gravity(self, gravity_object):
        G = 0.04  # Gravitational constant (adjust this value to change the strength of gravity)
        dx = (gravity_object.rect.x + int(gravity_object.image.get_size()[0])/2) - (self.rect.x + self.image_width/2)
        dy = (gravity_object.rect.y + int(gravity_object.image.get_size()[1])/2) - (self.rect.y + self.image_height/2)
        distance = math.hypot(dx, dy)
        force = G * self.mass * gravity_object.mass / distance**2
        force_x = force * dx / distance
        force_y = force * dy / distance
        self.speed_x += min(force_x,0.15) 
        self.speed_y += min(force_y,0.15) 
        if (self.speed_x > 2):
            self.speed_x = 2
        if (self.speed_y > 2):
            self.speed_y = 2
    
    def blackhole_gravity(self, large_mass_object):
        G = 0.05  # Gravitational constant (adjust this value to change the strength of gravity)
        dx = large_mass_object.rect.x - (self.rect.x + self.image_width/2)
        dy = large_mass_object.rect.y - (self.rect.y + self.image_height/2)
        distance = math.hypot(dx, dy)
        force = G * self.mass * large_mass_object.mass / distance**2
        force_x = force * dx / distance
        force_y = force * dy / distance
        self.speed_x += min(force_x,0.15) 
        self.speed_y += min(force_y,0.15) 
        if (self.speed_x > 2):
            self.speed_x = 2
        if (self.speed_y > 2):
            self.speed_y = 2

    def update(self):
        # Update speed with acceleration
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.speed_y = max(-self.max_speed, self.speed_y - self.acceleration)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.speed_y = min(self.max_speed, self.speed_y + self.acceleration)

        #self.check_collisions(gravity_objects)

        # Update position
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Update speed (friction)
        self.speed_x = 0.999*self.speed_x
        self.speed_y = 0.999*self.speed_y

        # Wrap around the side walls
        if wall_wrap == True:
            if self.rect.left < 0:
                self.rect.right = WINDOW_WIDTH
            elif self.rect.right > WINDOW_WIDTH:
                self.rect.left = 0

        # The Spaceship dies if it touches the walls if wall-wrap is turned off
        if wall_wrap == False:
            if self.rect.left < 0 or self.rect.right > WINDOW_WIDTH:
                return "game_over"

        # Keep the spaceship on the screen
        self.rect.x = max(0, min(WINDOW_WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(WINDOW_HEIGHT - self.rect.height, self.rect.y))

class GravityObject(pygame.sprite.Sprite):
    def __init__(self, x, y, size, speed_y):
        super().__init__()
        #size = random.randint(50,100)
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        #pygame.draw.circle(self.image, (255, 0, 0), (size,size), size)
        
        image_file_1 = "./artwork/spaceMeteors_001.png"
        image_file_2 = "./artwork/spaceMeteors_002.png"
        image_file_3 = "./artwork/spaceMeteors_003.png"
        image_file_4 = "./artwork/spaceMeteors_004.png"
        image1 = pygame.image.load(image_file_1).convert_alpha()
        image2 = pygame.image.load(image_file_2).convert_alpha()
        image3 = pygame.image.load(image_file_3).convert_alpha()
        image4 = pygame.image.load(image_file_4).convert_alpha()

        image1 = pygame.transform.scale(image1, (size * 2, size * 2))
        image2 = pygame.transform.scale(image2, (size * 2, size * 2))
        image3 = pygame.transform.scale(image3, (size * 2, size * 2))
        image4 = pygame.transform.scale(image4, (size * 2, size * 2))
        
        pic_choose = random.randint(1,4)
        if pic_choose == 1:
            self.image.blit(image1, (0,0))
        if pic_choose == 2:
            self.image.blit(image2, (0,0))
        if pic_choose == 3:
            self.image.blit(image3, (0,0))
        if pic_choose == 4:
            self.image.blit(image4, (0,0))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_y = speed_y
        self.mass = size

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class BlueObject(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y):
        super().__init__()
        self.image = pygame.Surface((60, 30))
        #self.image.fill((0, 0, 255))

        image_file_1 = "./artwork/spaceStation_018.png"
        image_file_2 = "./artwork/spaceStation_022.png"
        image_file_3 = "./artwork/spaceBuilding_015.png"
        image_file_4 = "./artwork/spaceBuilding_024.png"
        image1 = pygame.image.load(image_file_1).convert_alpha()
        image2 = pygame.image.load(image_file_2).convert_alpha()
        image3 = pygame.image.load(image_file_3).convert_alpha()
        image4 = pygame.image.load(image_file_4).convert_alpha()

        image1 = pygame.transform.scale(image1, (60, 30))
        image2 = pygame.transform.scale(image2, (60, 30))
        image3 = pygame.transform.scale(image3, (60, 30))
        image4 = pygame.transform.scale(image4, (60, 30))
        
        pic_choose = random.randint(1,4)
        if pic_choose == 1:
            self.image.blit(image1, (0,0))
        if pic_choose == 2:
            self.image.blit(image2, (0,0))
        if pic_choose == 3:
            self.image.blit(image3, (0,0))
        if pic_choose == 4:
            self.image.blit(image4, (0,0))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_y = speed_y
        self.size = 30

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class LargeMassObject(pygame.sprite.Sprite):
    def __init__(self, x, y, size, speed_y):
        super().__init__()
        self.original_image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_y = speed_y
        self.mass = size * 4
        self.stopped_time = 0
        self.stopped = False
        self.pause_over = False

        # Create the solid color circle as the bottom layer
        layer0 = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(layer0, (10, 10, 10), (size, size), size)

        # Load the individual image layers
        layer1 = pygame.image.load("./artwork/twirl_01.png").convert_alpha()
        layer2 = pygame.image.load("./artwork/twirl_03.png").convert_alpha()

        # Set initial rotation angles (adjust as needed)
        self.angle1 = 0
        self.angle2 = 90

        # Scale the layers to the desired size
        layer0 = pygame.transform.scale(layer0, (size * 2, size * 2))
        layer1 = pygame.transform.scale(layer1, (size * 2, size * 2))
        layer2 = pygame.transform.scale(layer2, (size * 2, size * 2))

        self.layers = [layer0, layer1, layer2]

    def update(self):
        warning_font = pygame.font.SysFont("Consolas", 72)

        # Update rotation angles (adjust the increment values as needed)
        self.angle1 += 0.5
        self.angle2 += 1.2

        # Clear the original image surface
        self.original_image.fill((0, 0, 0, 0))

        # Get the center of the layers for rotation
        layer_center = (self.layers[1].get_width() // 2, self.layers[1].get_height() // 2)

        # Draw each layer with the corresponding rotation angle
        rotated_layer1 = pygame.transform.rotate(self.layers[1], self.angle1)
        rotated_layer2 = pygame.transform.rotate(self.layers[2], self.angle2)

        # Calculate the offset for blitting the rotated layers
        rotated_layer1_rect = rotated_layer1.get_rect()
        rotated_layer1_rect.center = layer_center
        rotated_layer2_rect = rotated_layer2.get_rect()
        rotated_layer2_rect.center = layer_center

        # Blit the rotated layers onto the original image surface
        self.original_image.blit(self.layers[0], (0, 0))  # Draw the solid color circle first
        self.original_image.blit(rotated_layer1, rotated_layer1_rect)
        self.original_image.blit(rotated_layer2, rotated_layer2_rect)

        # Update the sprite image
        self.image = self.original_image.copy()

        if not self.stopped:
            self.rect.y += self.speed_y
            if self.rect.centery >= ((WINDOW_HEIGHT / 2) ): #+ layer_center[1])
                self.rect.centery = ((WINDOW_HEIGHT / 2) ) #+ layer_center[1]
                self.stopped = True
                self.stopped_time = pygame.time.get_ticks()
                time_text = warning_font.render(str(self.stopped_time), True, (255, 100, 100))
                window.blit(time_text, (int(WINDOW_WIDTH // 2 - time_text.get_width() // 2), int(3 * WINDOW_HEIGHT // 4)))

        if self.rect.y >= -500 and self.rect.y <= 0:
            warning_text = warning_font.render("INCOMING BLACK HOLE!", True, (255, 100, 100))
            window.blit(warning_text, (WINDOW_WIDTH // 2 - warning_text.get_width() // 2, WINDOW_HEIGHT // 4))

        if self.stopped:
            current_time = pygame.time.get_ticks()
            
            # Draw each layer with the corresponding rotation angle
            rotated_layer1 = pygame.transform.rotate(self.layers[1], self.angle1)
            rotated_layer2 = pygame.transform.rotate(self.layers[2], self.angle2)

            # Calculate the offset for blitting the rotated layers
            rotated_layer1_rect = rotated_layer1.get_rect()
            rotated_layer1_rect.center = layer_center
            rotated_layer2_rect = rotated_layer2.get_rect()
            rotated_layer2_rect.center = layer_center

            # Blit the rotated layers onto the original image surface
            self.original_image.blit(self.layers[0], (0, 0))  # Draw the solid color circle first
            self.original_image.blit(rotated_layer1, rotated_layer1_rect)
            self.original_image.blit(rotated_layer2, rotated_layer2_rect)

            # Update the sprite image
            self.image = self.original_image.copy()
            
            if current_time - self.stopped_time >= 3000:  # 30 seconds
                self.stopped = False
                self.pause_over = True

        if self.pause_over:
            self.rect.y += self.speed_y

    def get_distance_to_star(self, star):
        dx = star["x"] - self.rect.centerx
        dy = star["y"] - self.rect.centery
        return math.sqrt(dx**2 + dy**2)

def display_game_over(window,score,high_score):
    pygame.font.init()
    game_over_font = pygame.font.SysFont("Consolas", 72)
    game_over_text = game_over_font.render("Game Over", True, (255, 255, 255))
    score_text = game_over_font.render(f"Score: {score}", True, (255, 255, 255))
    high_score_text = game_over_font.render(f"High Score: {high_score}", True, (255, 255, 255))
    window.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2 - 100))
    window.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))
    window.blit(high_score_text, (WINDOW_WIDTH // 2 - high_score_text.get_width() // 2, WINDOW_HEIGHT // 2 + 120))
    pygame.display.flip()


def play_game_loop(window, star_layers):
    #print("play")
    level_high_scores = load_level_high_scores()
    level_layout = level_1_layout()

    # Create the player and gravity objects
    player = Spaceship()
    gravity_objects = pygame.sprite.Group()
    blue_objects = pygame.sprite.Group()
    for obj in level_layout:
        gravity_object = GravityObject(obj["x"], obj["y"], obj["size"], obj["speed_y"])
        gravity_objects.add(gravity_object)
        blue_object = BlueObject(obj["x"] + random.uniform(-50,50), obj["y"] - random.uniform(30,130), obj["speed_y"])
        blue_objects.add(blue_object)

    # Create the large mass object
    large_mass_object = LargeMassObject(int(WINDOW_WIDTH // 2 - 200), -6000, 200, 1)
    running = True
    clock = pygame.time.Clock()
    score = 0
    score_texts = []
    # Clear the window and show the game loop
    window.fill((0, 0, 0))
    pygame.display.flip()
    star_layers = init_star_layers()
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Clear the window
        window.fill((0, 0, 0))

        # Update the player and gravity objects
        if not large_mass_object.stopped:
            # Draw stars
            large_mass_stopped = False
            update_star_layers(star_layers,window)
            for gravity_object in gravity_objects:
                #gravity_object.update(gravity_objects)
                player.apply_gravity(gravity_object)
            player.update()
            game_over = player.update()
            gravity_objects.update()
            blue_objects.update()
            large_mass_object.update()
        elif large_mass_object.stopped:
            large_mass_stopped = True
            update_star_layers(star_layers,window,large_mass_object,large_mass_stopped)
            player.blackhole_gravity(large_mass_object)
            player.update()
            game_over = player.update()

        # Check for collisions between the player and blue objects
        blue_object_hit = pygame.sprite.spritecollideany(player, blue_objects)
        if blue_object_hit:
            score += 50 #random.randint(10, 50)  # Adjust the score range as needed
            blue_object_hit.kill()
            score_text = scorefont.render(str(50), True, (0, 0, 255))
            score_texts.append({"text": score_text, "pos": blue_object_hit.rect.topleft, "time": pygame.time.get_ticks()})
            
            for score_text_info in score_texts[:]:
                elapsed_time = pygame.time.get_ticks() - score_text_info["time"]
                if elapsed_time < 1000:  # Keep the text on the screen for 1 second
                    window.blit(score_text_info["text"], score_text_info["pos"])
                else:
                    score_texts.remove(score_text_info)

        # Render the score text
        high_score_text = scorefont.render(f"Level High Score: {level_high_scores}", True, (255, 255, 255))
        score_counter = scorefont.render(f"Score: {score}", True, (255, 255, 255))

        # Draw the player and gravity objects
        window.blit(player.image, player.rect)
        blue_objects.draw(window)
        for gravity_object in gravity_objects:
            window.blit(gravity_object.image, gravity_object.rect)
        window.blit(player.image, player.rect)
        #if large_mass_object.alive():  # Check if the large mass object is still alive
        window.blit(large_mass_object.image, large_mass_object.rect)
        window.blit(score_counter, (10, WINDOW_HEIGHT - 100))
        window.blit(high_score_text, (10, WINDOW_HEIGHT - 50))

        # Check if the game is over
        if game_over == "game_over":
            if score > level_high_scores:
                level_high_scores = score
                save_level_high_scores(level_high_scores)

            display_game_over(window,score,level_high_scores)
            #running = False

        # Update the display
        pygame.display.flip()

        clock.tick(60)


def show_instructions(window):
    #print("instructions")
    # Load the instruction image
    instruction_image = pygame.image.load("./artwork/instructions_b.png")

    # Get the dimensions of the display
    screen_width, screen_height = pygame.display.get_surface().get_size()

    # Scale the image to fit the display
    scaled_image = pygame.transform.scale(instruction_image, (screen_width, screen_height))

    # Create a new surface with the scaled image
    image_surface = pygame.Surface((screen_width, screen_height))
    image_surface.blit(scaled_image, (0, 0))

    # Display the image surface
    pygame.display.get_surface().blit(image_surface, (0, 0))
    pygame.display.flip()

    # Wait for the user to close the instructions
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    return


    # Game loop
def infinite_play_loop(window, star_layers):
    #print("infinity!")
    arcade_high_score = load_arcade_high_score()

    # Generate the level layout
    level_layout = generate_random_layout(20, 150)  # Adjust the arguments as needed

    # Create the player and gravity objects
    player = Spaceship()
    gravity_objects = pygame.sprite.Group()
    blue_objects = pygame.sprite.Group()
    for obj in level_layout:
        gravity_object = GravityObject(obj["x"], obj["y"], obj["size"], obj["speed_y"])
        gravity_objects.add(gravity_object)
        blue_object = BlueObject(obj["x"] + random.uniform(-50,50), obj["y"] - random.uniform(30,130), obj["speed_y"])
        blue_objects.add(blue_object)

    running = True
    clock = pygame.time.Clock()
    score = 0
    score_texts = []

    # Clear the window and show the game loop
    window.fill((0, 0, 0))
    pygame.display.flip()
    star_layers = init_star_layers()
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Remove gravity objects that have moved off the screen and spawn new gravity objects
        #for obj in gravity_objects:
        #print(gravity_objects.sprites())

        if len(gravity_objects) < 20 and random.random() < 0.75:
            gravity_object = GravityObject(int(WINDOW_WIDTH //2 + random.uniform(-250, 250)), int(-30 - random.uniform(10,30)), int(random.uniform(30, 80)), 
                                           random.uniform(0.5,1))
            gravity_objects.add(gravity_object)
            blue_object = BlueObject(obj["x"] + random.uniform(-50,50), obj["y"] - random.uniform(30,130), obj["speed_y"])
            blue_objects.add(blue_object)

        # Update the player and gravity objects
        for gravity_object in gravity_objects:
            #gravity_object.update(gravity_objects)
            player.apply_gravity(gravity_object)
        player.update()
        game_over = player.update()
        gravity_objects.update()
        blue_objects.update()

        # Clear the window
        window.fill((0, 0, 0))

        # Draw stars
        update_star_layers(star_layers,window)

        # Check for collisions between the player and blue objects
        blue_object_hit = pygame.sprite.spritecollideany(player, blue_objects)
        if blue_object_hit:
            score += 50 #random.randint(10, 50)  # Adjust the score range as needed
            blue_object_hit.kill()
            score_text = scorefont.render(str(50), True, (0, 0, 255))
            score_texts.append({"text": score_text, "pos": blue_object_hit.rect.topleft, "time": pygame.time.get_ticks()})
            
            for score_text_info in score_texts[:]:
                elapsed_time = pygame.time.get_ticks() - score_text_info["time"]
                if elapsed_time < 1000:  # Keep the text on the screen for 1 second
                    window.blit(score_text_info["text"], score_text_info["pos"])
                else:
                    score_texts.remove(score_text_info)

        # Render the score text
        arcade_high_score_text = scorefont.render(f"Arcade High Score: {arcade_high_score}", True, (255, 255, 255))
        score_counter = scorefont.render(f"Score: {score}", True, (255, 255, 255))

        # Draw the player and gravity objects
        window.blit(player.image, player.rect)
        blue_objects.draw(window)
        for gravity_object in gravity_objects:
            window.blit(gravity_object.image, gravity_object.rect)
        window.blit(player.image, player.rect)
        window.blit(score_counter, (10, WINDOW_HEIGHT - 100))
        window.blit(arcade_high_score_text, (10, WINDOW_HEIGHT - 50))

        # Check if the game is over
        if game_over == "game_over":
            if score > arcade_high_score:
                arcade_high_score = score
                save_arcade_high_score(arcade_high_score)
            display_game_over(window,score,arcade_high_score)
            #running = False

        # Update the display
        pygame.display.flip()

        clock.tick(60)

def level_1_layout():
    size_array = np.full(20,80)
    #print(size_array)
    x_array = np.tile([((WINDOW_WIDTH / 2) + (WINDOW_WIDTH * 0.15) - 80), ((WINDOW_WIDTH / 2) - (WINDOW_WIDTH * 0.15) - 80)],10)
    #print(x_array)
    y_array = np.arange(-50,-5050,-250)
    #print(y_array)
    layout = []
    for i in range(len(size_array)):
        layout.append({"size": size_array[i], "x": x_array[i], "y": y_array[i], "speed_y": 1})
    return layout


def quit_game():
    pygame.quit()
    return

def show_menu(window):
    menu_font = pygame.font.SysFont('Consolas', 48)
    title_font = pygame.font.SysFont('Consolas', 72)
    text_font = pygame.font.SysFont('Consolas', 12)

    # Initialize star layers
    star_layers = init_star_layers()

    title_text = title_font.render("Gravity Run", True, (255, 255, 255))
    title_rect = title_text.get_rect(midtop=(WINDOW_WIDTH // 2, 50))

    play_text = menu_font.render("Play Game", True, (255, 255, 0))
    play_rect = play_text.get_rect(midtop=(WINDOW_WIDTH // 2, 200))

    arcade_text = menu_font.render("Arcade Play", True, (255, 255, 255))
    arcade_rect = arcade_text.get_rect(midtop=(WINDOW_WIDTH // 2, 300))
    
    instructions_text = menu_font.render("Instructions", True, (255, 255, 255))
    instructions_rect = instructions_text.get_rect(midtop=(WINDOW_WIDTH // 2, 400))
    
    quit_text = menu_font.render("Quit", True, (255, 255, 255))
    quit_rect = quit_text.get_rect(midtop=(WINDOW_WIDTH // 2, 500))

    atrib_text = text_font.render("Artwork from OpenGameArt.org and www.kenney.nl.",True,(255,255,255))
    #atrib_rect = atrib_text.get_rect(10,WINDOW_HEIGHT -25)

    menu_items = [
        ("Play Game", "level"),
        ("Arcade Play", "infinite"),
        ("Instructions", "instructions"),
        ("Quit", "quit")
    ]

    selected_item = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:               
                if (event.key == pygame.K_UP) or (event.key == pygame.K_w):
                    selected_item -= 1
                    selected_item = selected_item % len(menu_items)
                    #print(selected_item)
                elif (event.key == pygame.K_DOWN) or (event.key == pygame.K_s):
                    selected_item += 1
                    selected_item = selected_item % len(menu_items)
                    #print(selected_item)
                
                if selected_item == 0:
                    play_text = menu_font.render("Play Game", True, (255, 255, 0))
                    arcade_text = menu_font.render("Arcade Play", True, (255, 255, 255))
                    instructions_text = menu_font.render("Instructions", True, (255, 255, 255))
                    quit_text = menu_font.render("Quit", True, (255, 255, 255))
                elif selected_item == 1:
                    play_text = menu_font.render("Play Game", True, (255, 255, 255))
                    arcade_text = menu_font.render("Arcade Play", True, (255, 255, 0))
                    instructions_text = menu_font.render("Instructions", True, (255, 255, 255))
                    quit_text = menu_font.render("Quit", True, (255, 255, 255))
                elif selected_item == 2:
                    play_text = menu_font.render("Play Game", True, (255, 255, 255))
                    arcade_text = menu_font.render("Arcade Play", True, (255, 255, 255))
                    instructions_text = menu_font.render("Instructions", True, (255, 255, 0))
                    quit_text = menu_font.render("Quit", True, (255, 255, 255))
                elif selected_item == 3:
                    play_text = menu_font.render("Play Game", True, (255, 255, 255))
                    arcade_text = menu_font.render("Arcade Play", True, (255, 255, 255))
                    instructions_text = menu_font.render("Instructions", True, (255, 255, 255))
                    quit_text = menu_font.render("Quit", True, (255, 255, 0))
                
                if event.key == pygame.K_RETURN:
                    #menu_items[selected_item][1]()
                    #print(selected_item, menu_items[selected_item][0])
                    if selected_item == 0:
                        #print("Go to level")
                        play_game_loop(window, star_layers)
                    elif selected_item == 1:
                        # Call infinite_play function and then run the game loop
                        infinite_play_loop(window, star_layers)
                    elif selected_item == 2:
                       #print("Go to Instructions Page")
                        show_instructions(window)
                    elif selected_item ==3:
                        #print("Quit")
                        pygame.quit()
                        return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    play_text = menu_font.render("Play Game", True, (255, 255, 0))
                    arcade_text = menu_font.render("Arcade Play", True, (255, 255, 255))
                    instructions_text = menu_font.render("Instructions", True, (255, 255, 255))
                    quit_text = menu_font.render("Quit", True, (255, 255, 255))
                    #print("Go to Level.") #play_game()
                    play_game_loop(window, star_layers)
                elif arcade_rect.collidepoint(event.pos):
                    play_text = menu_font.render("Play Game", True, (255, 255, 255))
                    arcade_text = menu_font.render("Arcade Play", True, (255, 255, 0))
                    instructions_text = menu_font.render("Instructions", True, (255, 255, 255))
                    quit_text = menu_font.render("Quit", True, (255, 255, 255))
                    # Call infinite_play function and then run the game loop
                    infinite_play_loop(window, star_layers)
                elif instructions_rect.collidepoint(event.pos):
                    play_text = menu_font.render("Play Game", True, (255, 255, 255))
                    arcade_text = menu_font.render("Arcade Play", True, (255, 255, 255))
                    instructions_text = menu_font.render("Instructions", True, (255, 255, 0))
                    quit_text = menu_font.render("Quit", True, (255, 255, 255))
                    #print("Go to Instructions Page") #show_instructions()
                elif quit_rect.collidepoint(event.pos):
                    play_text = menu_font.render("Play Game", True, (255, 255, 255))
                    arcade_text = menu_font.render("Arcade Play", True, (255, 255, 255))
                    instructions_text = menu_font.render("Instructions", True, (255, 255, 255))
                    quit_text = menu_font.render("Quit", True, (255, 255, 0))
                    #print("Quit")
                    pygame.quit()
                    return
                return menu_items[selected_item][1]

        window.fill((0, 0, 0))
        update_star_layers(star_layers,window)
        window.blit(title_text, title_rect)
        window.blit(play_text, play_rect)
        window.blit(arcade_text, arcade_rect)
        window.blit(instructions_text, instructions_rect)
        window.blit(quit_text, quit_rect)
        window.blit(atrib_text, (10,WINDOW_HEIGHT -25))

        pygame.display.flip()

# Show the menu screen
#show_menu()

if __name__ == "__main__":
    main()
