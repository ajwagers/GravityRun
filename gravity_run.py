import pygame
import random
import math
import numpy as np


# Initialize Pygame
pygame.init()

# Set up the game window in fullscreen mode
window_info = pygame.display.Info()
WINDOW_WIDTH = 1200 #window_info.current_w
WINDOW_HEIGHT = 800 #window_info.current_h
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) #, pygame.FULLSCREEN)
font = pygame.font.SysFont("consolas",56)
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

def update_star_layers(star_layers):
    # Draw stars
    for i, layer in enumerate(star_layers):
        for star in layer:
            star["y"] += STAR_LAYERS[i]["speed"]  # Move stars based on layer speed
            if star["y"] > WINDOW_HEIGHT + star["size"][1]:  # Wrap around if star goes off-screen
                star["y"] = -star["size"][1]
                star["x"] = random.randrange(WINDOW_WIDTH)
                star["color"] = random.choice(STAR_COLORS)
            pygame.draw.rect(window, star["color"], (star["x"], star["y"], star["size"][0], star["size"][1]))

def show_menu():
    menu_font = pygame.font.SysFont('Consolas', 48)
    title_font = pygame.font.SysFont('Consolas', 72)

    # Initialize star layers
    star_layers = init_star_layers()

    title_text = title_font.render("Gravity Run", True, (255, 255, 255))
    title_rect = title_text.get_rect(midtop=(WINDOW_WIDTH // 2, 50))

    play_text = menu_font.render("Play", True, (255, 255, 255))
    play_rect = play_text.get_rect(midtop=(WINDOW_WIDTH // 2, 200))
    
    instructions_text = menu_font.render("Instructions", True, (255, 255, 255))
    instructions_rect = instructions_text.get_rect(midtop=(WINDOW_WIDTH // 2, 300))
    
    quit_text = menu_font.render("Quit", True, (255, 255, 255))
    quit_rect = quit_text.get_rect(midtop=(WINDOW_WIDTH // 2, 400))

    #menu_items = [
    #    ("Play", play_game),
    #    ("Instructions", show_instructions),
    #    ("Quit", quit_game)
    #]

    selected_item = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(menu_items)
                #elif event.key ==pygame.K_RETURN:
                #    menu_items[selected_item][1]()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    return "play"
                elif instructions_rect.collidepoint(event.pos):
                    show_instructions()
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    return

        window.fill((0, 0, 0))
        update_star_layers(star_layers)
        window.blit(title_text, title_rect)
        window.blit(play_text, play_rect)
        window.blit(instructions_text, instructions_rect)
        window.blit(quit_text, quit_rect)

        # Draw menu items with highlighted selection
        #for i, (text, function) in enumerate(menu_items):
        #    if i == selected_item:
        #        color = (0, 255, 0)  # Highlight the selected item in green
        #    else:
        #        color = (255, 255, 255)
        #    text_surface = menu_font.render(text, True, color)
        #    text_rect = text_surface.get_rect(midtop=(WINDOW_WIDTH // 2, 200 + i * 100))
        #    window.blit(text_surface, text_rect)

        pygame.display.flip()

def show_instructions():
    instructions_font = pygame.font.Font(None, 36)
    instructions_text = instructions_font.render("Instructions go here...", True, (255, 255, 255))
    instructions_rect = instructions_text.get_rect(midtop=(WINDOW_WIDTH // 2, 50))

    init_star_layers()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        window.fill((0, 0, 0))
        window.blit(instructions_text, instructions_rect)
        pygame.display.flip()

# Generate Level 1
def generate_level_layout(num_rows, offset_range):
    layout = []
    for row in range(num_rows):
        size = random.randint(30, 80)
        x_offset = random.randint(-offset_range, offset_range)
        y_pos = -50 - (row * 200)  # Adjust the vertical spacing as needed
        layout.append({"size": size, "x": WINDOW_WIDTH // 2 + x_offset, "y": y_pos, "speed_y": 2})
    return layout

def level_1_layout():
    size_array = np.full(20,80)
    #print(size_array)
    x_array = np.tile([((WINDOW_WIDTH / 2) + (WINDOW_WIDTH * 0.15) - 40), ((WINDOW_WIDTH / 2) - (WINDOW_WIDTH * 0.15) - 40)],10)
    #print(x_array)
    y_array = np.arange(-50,-5050,-250)
    #print(y_array)
    layout = []
    for i in range(len(size_array)):
        layout.append({"size": size_array[i], "x": x_array[i], "y": y_array[i], "speed_y": 2})
    return layout


class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = WINDOW_WIDTH // 2
        self.rect.y = WINDOW_HEIGHT // 2
        self.speed_x = 0
        self.speed_y = 0
        self.acceleration = 0.25
        self.max_speed = 5
        self.mass = 50
    
    def apply_gravity(self, gravity_object):
        G = 0.1  # Gravitational constant (adjust this value to change the strength of gravity)
        dx = gravity_object.rect.x - self.rect.x
        dy = gravity_object.rect.y - self.rect.y
        distance = math.hypot(dx, dy)
        force = G * self.mass * gravity_object.mass / distance**2
        force_x = force * dx / distance
        force_y = force * dy / distance
        self.speed_x += force_x
        self.speed_y += force_y
        if (self.speed_x > 10):
            self.speed_x = 10
        if (self.speed_y > 10):
            self.speed_y = 10

    def update(self):
        # Apply gravity
        #self.speed_y += 0.3

        # Update speed with acceleration
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.speed_y = max(-self.max_speed, self.speed_y - self.acceleration)
        if keys[pygame.K_s]:
            self.speed_y = min(self.max_speed, self.speed_y + self.acceleration)

        # Update position
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Update speed (friction)
        self.speed_x = 0.999*self.speed_x
        self.speed_y = 0.999*self.speed_y

        # Wrap around the side walls
        #if self.rect.left < 0:
        #    self.rect.right = WINDOW_WIDTH
        #elif self.rect.right > WINDOW_WIDTH:
        #    self.rect.left = 0

        # Add this check to end the game if the spaceship hits the sides
        if self.rect.left < 0 or self.rect.right > WINDOW_WIDTH:
            return "game_over"

        # Keep the spaceship on the screen
        self.rect.x = max(0, min(WINDOW_WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(WINDOW_HEIGHT - self.rect.height, self.rect.y))

def display_game_over(score):
    game_over_font = pygame.font.SysFont("Consolas", 72)
    game_over_text = game_over_font.render("Game Over", True, (255, 255, 255))
    score_text = game_over_font.render(f"Score: {score}", True, (255, 255, 255))
    window.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2 - 100))
    window.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))
    pygame.display.flip()

class GravityObject(pygame.sprite.Sprite):
    def __init__(self, x, y, size, speed_y):
        super().__init__()
        #size = random.randint(50,100)
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (size,size), size)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_y = speed_y
        self.mass = size

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()
        # Collision avoidance
        #colliding_objects = pygame.sprite.spritecollide(self, self.gravity_objects, False)
        #while colliding_objects:
        #    self.rect.x = random.randint(50, WINDOW_WIDTH - 50)
        #    self.rect.y = -50
        #    colliding_objects = pygame.sprite.spritecollide(self, self.gravity_objects, False)

class BlueObject(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_y = speed_y
        self.size = 30

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

# Show the menu screen
menu_choice = show_menu()

# Start the game if 'Play' is selected
if menu_choice == "play": #def play_game():  

    # Generate the level layout
    level_layout = level_1_layout() #generate_level_layout(20, 150)  # Adjust the arguments as needed

    # Create the player and gravity objects
    player = Spaceship()
    gravity_objects = pygame.sprite.Group()
    blue_objects = pygame.sprite.Group()
    for obj in level_layout:
        gravity_object = GravityObject(obj["x"], obj["y"], obj["size"], obj["speed_y"])
        gravity_objects.add(gravity_object)
        blue_object = BlueObject((obj["x"] + (((WINDOW_WIDTH // 2) - obj["x"])/2)), obj["y"] - 100, obj["speed_y"])
        blue_objects.add(blue_object)

    # Game loop
    running = True
    clock = pygame.time.Clock()
    score = 0
    star_layers = init_star_layers()
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Spawn new gravity objects
        #if len(gravity_objects) < 5 and random.random() < 0.07:
        #    gravity_object = GravityObject()
        #    gravity_objects.add(gravity_object)

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
        update_star_layers(star_layers)

        # Check for collisions between the player and blue objects
        blue_object_hit = pygame.sprite.spritecollideany(player, blue_objects)
        if blue_object_hit:
            score += 50 #random.randint(10, 50)  # Adjust the score range as needed
            blue_object_hit.kill()
            # Display the random number at the position of the hit blue object
            font = pygame.font.SysFont("consolas",int(WINDOW_HEIGHT*0.05))
            score_text = font.render(str(score), True, (255, 255, 255))
            window.blit(score_text, blue_object_hit.rect.topleft)

        # Render the score text
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))

        # Draw the player and gravity objects
        blue_objects.draw(window)
        for gravity_object in gravity_objects:
            window.blit(gravity_object.image, gravity_object.rect)
        window.blit(player.image, player.rect)
        window.blit(score_text, (WINDOW_WIDTH*0.075, WINDOW_HEIGHT - 0.1*WINDOW_HEIGHT))

        # Check if the game is over
        if game_over == "game_over":
            display_game_over(score)
            #running = False

        # Update the display
        pygame.display.flip()

        # Limit the frame rate
        clock.tick(60)

# Quit Pygame
def quit_game():
    pygame.quit()
