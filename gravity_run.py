import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the game window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Spaceship Sidescroller")

class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = 50
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
        if self.rect.left < 0:
            self.rect.right = WINDOW_WIDTH
        elif self.rect.right > WINDOW_WIDTH:
            self.rect.left = 0

        # Keep the spaceship on the screen
        self.rect.x = max(0, min(WINDOW_WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(WINDOW_HEIGHT - self.rect.height, self.rect.y))

        import random

class GravityObject(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.randint(20,100)
        self.image = pygame.Surface((size, size))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.y = -50
        self.rect.x = random.randint(50, WINDOW_WIDTH - 50)
        self.speed_y = random.randint(1,20)
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


# Create the player and gravity objects
player = Spaceship()
gravity_objects = pygame.sprite.Group()

# Game loop
running = True
clock = pygame.time.Clock()
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Spawn new gravity objects
    if len(gravity_objects) < 5 and random.random() < 0.07:
        gravity_object = GravityObject()
        gravity_objects.add(gravity_object)

    # Update the player and gravity objects
    for gravity_object in gravity_objects:
        #gravity_object.update(gravity_objects)
        player.apply_gravity(gravity_object)
    player.update()
    gravity_objects.update()
    
    # Clear the window
    window.fill((0, 0, 0))

    # Draw the player and gravity objects
    window.blit(player.image, player.rect)
    for gravity_object in gravity_objects:
        window.blit(gravity_object.image, gravity_object.rect)

    # Update the display
    pygame.display.flip()

    # Limit the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()