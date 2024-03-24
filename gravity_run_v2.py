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
wall_wrap = False
default_font = pygame.font.SysFont("consolas",56)
scorefont = pygame.font.SysFont("consolas", int(WINDOW_HEIGHT * 0.05))
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
                gravity_objects, blue_objects, player = infinite_play()
                game_state = infinite_play_loop(window, star_layers, gravity_objects, blue_objects, player)
            elif game_mode == "level":
                # Run the level game loop
                gravity_objects, blue_objects, player, large_mass_object = play_game()
                game_state = play_game_loop(window, star_layers, gravity_objects, blue_objects, player, large_mass_object)
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

def update_star_layers(star_layers,window):
    # Draw stars
    for i, layer in enumerate(star_layers):
        for star in layer:
            star["y"] += STAR_LAYERS[i]["speed"]  # Move stars based on layer speed
            if star["y"] > WINDOW_HEIGHT + star["size"][1]:  # Wrap around if star goes off-screen
                star["y"] = -star["size"][1]
                star["x"] = random.randrange(WINDOW_WIDTH)
                star["color"] = random.choice(STAR_COLORS)
            pygame.draw.rect(window, star["color"], (star["x"], star["y"], star["size"][0], star["size"][1]))

def generate_random_layout(num_rows, offset_range):
    layout = []
    for row in range(num_rows):
        size = int(random.uniform(30, 60))
        x_offset = random.uniform(-offset_range, offset_range)
        y_pos = -50 - (row * 200)  # Adjust the vertical spacing as needed
        speed_rand = random.gauss(0.5,1)
        layout.append({"size": size, "x": int(WINDOW_WIDTH // 2 + x_offset), "y": y_pos, "speed_y": speed_rand})
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
        self.acceleration = 0.01
        self.max_speed = 2
        self.mass = 40
    
    def apply_gravity(self, gravity_object):
        G = 0.05  # Gravitational constant (adjust this value to change the strength of gravity)
        dx = gravity_object.rect.x - self.rect.x
        dy = gravity_object.rect.y - self.rect.y
        distance = math.hypot(dx, dy)
        force = G * self.mass * gravity_object.mass / distance**2
        force_x = force * dx / distance
        force_y = force * dy / distance
        self.speed_x += force_x
        self.speed_y += force_y
        if (self.speed_x > 3):
            self.speed_x = 3
        if (self.speed_y > 3):
            self.speed_y = 3

    def update(self):
        # Update speed with acceleration
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.speed_y = max(-self.max_speed, self.speed_y - self.acceleration)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.speed_y = min(self.max_speed, self.speed_y + self.acceleration)

        # Update position
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Update speed (friction)
        self.speed_x = 0.9*self.speed_x
        self.speed_y = 0.9*self.speed_y

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

class LargeMassObject(pygame.sprite.Sprite):
    def __init__(self, x, y, size, speed_y):
        super().__init__()
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (100, 100, 100), (size,size), size)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_y = speed_y
        self.mass = size * 4
        self.stopped_time = 0  # Time when the object stopped
        self.stopped = False  # Flag to indicate if the object has stopped
        self.pause_over = False  # Flag to indicate if the 30-second pause is over

    def update(self):
        if not self.stopped:
            self.rect.y += self.speed_y
            if self.rect.centery >= WINDOW_HEIGHT // 2:
                self.rect.centery = WINDOW_HEIGHT // 2
                self.stopped = True
                self.stopped_time = pygame.time.get_ticks()
        else:
            current_time = pygame.time.get_ticks()
            if current_time - self.stopped_time >= 30000:  # 30 seconds
                self.pause_over = True
            if self.pause_over:
                self.rect.y += self.speed_y

def display_game_over(window,score):
    game_over_font = pygame.font.SysFont("Consolas", 72)
    game_over_text = game_over_font.render("Game Over", True, (255, 255, 255))
    score_text = game_over_font.render(f"Score: {score}", True, (255, 255, 255))
    window.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2 - 100))
    window.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))
    pygame.display.flip()

def play_game():
    print("play")
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
    large_mass_object = LargeMassObject(int(WINDOW_WIDTH // 2 - 200), -5300, 200, 1)

    return gravity_objects, blue_objects, player, large_mass_object

def play_game_loop(window, star_layers, gravity_objects, blue_objects, player, large_mass_object):
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

        # Update the player and gravity objects
        for gravity_object in gravity_objects:
            #gravity_object.update(gravity_objects)
            player.apply_gravity(gravity_object)
        player.update()
        game_over = player.update()
        gravity_objects.update()
        blue_objects.update()
        large_mass_object.update()

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
        score_counter = scorefont.render(f"Score: {score}", True, (255, 255, 255))

        # Draw the player and gravity objects
        window.blit(player.image, player.rect)
        blue_objects.draw(window)
        for gravity_object in gravity_objects:
            window.blit(gravity_object.image, gravity_object.rect)
        window.blit(player.image, player.rect)
        #if large_mass_object.alive():  # Check if the large mass object is still alive
        window.blit(large_mass_object.image, large_mass_object.rect)
        window.blit(score_counter, (10, WINDOW_HEIGHT - 50))

        # Check if the game is over
        if game_over == "game_over":
            display_game_over(window,score)
            #running = False

        def update(self):
            clock.tick(1000)

        # Update the display
        pygame.display.flip()

def show_instructions():
    print("instructions")

def infinite_play():
    print("infinity!")

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

    return gravity_objects, blue_objects, player

    # Game loop
def infinite_play_loop(window, star_layers, gravity_objects, blue_objects, player):
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
        score_counter = scorefont.render(f"Score: {score}", True, (255, 255, 255))

        # Draw the player and gravity objects
        window.blit(player.image, player.rect)
        blue_objects.draw(window)
        for gravity_object in gravity_objects:
            window.blit(gravity_object.image, gravity_object.rect)
        window.blit(player.image, player.rect)
        window.blit(score_counter, (10, WINDOW_HEIGHT - 30))

        # Check if the game is over
        if game_over == "game_over":
            display_game_over(window,score)
            #running = False

        def update(self):
            clock.tick(600)

        # Update the display
        pygame.display.flip()

def level_1_layout():
    size_array = np.full(20,80)
    #print(size_array)
    x_array = np.tile([((WINDOW_WIDTH / 2) + (WINDOW_WIDTH * 0.15) - 40), ((WINDOW_WIDTH / 2) - (WINDOW_WIDTH * 0.15) - 40)],10)
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
                    print(selected_item)
                elif (event.key == pygame.K_DOWN) or (event.key == pygame.K_s):
                    selected_item += 1
                    selected_item = selected_item % len(menu_items)
                    print(selected_item)
                
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
                    print(selected_item, menu_items[selected_item][0])
                    if selected_item == 0:
                        print("Go to level")
                        gravity_objects, blue_objects, player, large_mass_object = play_game()
                        play_game_loop(window, star_layers, gravity_objects, blue_objects, player, large_mass_object)
                    elif selected_item == 1:
                        # Call infinite_play function and then run the game loop
                        gravity_objects, blue_objects, player = infinite_play()
                        infinite_play_loop(window, star_layers, gravity_objects, blue_objects, player)
                    elif selected_item == 2:
                        print("Go to Instructions Page")
                    elif selected_item ==3:
                        print("Quit")
                        pygame.quit()
                        return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    play_text = menu_font.render("Play Game", True, (255, 255, 0))
                    arcade_text = menu_font.render("Arcade Play", True, (255, 255, 255))
                    instructions_text = menu_font.render("Instructions", True, (255, 255, 255))
                    quit_text = menu_font.render("Quit", True, (255, 255, 255))
                    print("Go to Level.") #play_game()
                    gravity_objects, blue_objects, player, large_mass_object = play_game()
                    play_game_loop(window, star_layers, gravity_objects, blue_objects, player, large_mass_object)
                elif arcade_rect.collidepoint(event.pos):
                    play_text = menu_font.render("Play Game", True, (255, 255, 255))
                    arcade_text = menu_font.render("Arcade Play", True, (255, 255, 0))
                    instructions_text = menu_font.render("Instructions", True, (255, 255, 255))
                    quit_text = menu_font.render("Quit", True, (255, 255, 255))
                    # Call infinite_play function and then run the game loop
                    gravity_objects, blue_objects, player = infinite_play()
                    infinite_play_loop(window, star_layers, gravity_objects, blue_objects, player)
                elif instructions_rect.collidepoint(event.pos):
                    play_text = menu_font.render("Play Game", True, (255, 255, 255))
                    arcade_text = menu_font.render("Arcade Play", True, (255, 255, 255))
                    instructions_text = menu_font.render("Instructions", True, (255, 255, 0))
                    quit_text = menu_font.render("Quit", True, (255, 255, 255))
                    print("Go to Instructions Page") #show_instructions()
                elif quit_rect.collidepoint(event.pos):
                    play_text = menu_font.render("Play Game", True, (255, 255, 255))
                    arcade_text = menu_font.render("Arcade Play", True, (255, 255, 255))
                    instructions_text = menu_font.render("Instructions", True, (255, 255, 255))
                    quit_text = menu_font.render("Quit", True, (255, 255, 0))
                    print("Quit")
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

        pygame.display.flip()

# Show the menu screen
#show_menu()

if __name__ == "__main__":
    main()