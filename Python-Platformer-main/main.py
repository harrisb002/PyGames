import os
import math
import random
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 800
FPS = 60  # Frames per second
PLAYER_VEL = 5   # Player speed

window = pygame.display.set_mode((WIDTH, HEIGHT))

# Function to flip animations
def flip(sprites):
    # Takes in a list of sprites and flips them in x (horizontal) direction
    # EX: flip(surface, bool flip_x, bool flip_y)
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

# Loads all sprite sheets for Character chosen in game: Default "MaskDude"
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    # Determine path of image going to load
    path = join("assets", dir1, dir2)

    # Get all images in the chosen directory
    images = [f for f in listdir(path) if isfile(join(path, f))]  # Loads every single file inside chosen directory

    # Key value pairs, where key is animation style and the value is all the images in that animation EX: All 11 frames in idle
    all_sprites = {}

    # NOTE:
    # Create a rectangle that will determine where the image will be drawn (Sprite sheet that contains multiple of images)
    # And blit it onto the surface. Creating a surface that is the size of individual animation frame
    # Then export animation screen to surface

    # Loading the image(one of the files found in the path) and append the path as well as allow for a transparent background w/alpha
    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):   # Width of the individual image (32 pixels wide) to load the images
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)  # SCRALPHA is for transparent images, 32 is depth
            rect = pygame.Rect(i * width, 0, width, height)  # Rect(Location on original image that we want to grab new frame from)
            surface.blit(sprite_sheet, (0, 0), rect)  # In the pos (0,0) -top_left_most of the new surface, drawing only the frame of the sprite sheet that is desired
            sprites.append(pygame.transform.scale2x(surface))  # Double size of default size

        #For a multi directional animation, need two keys for each animation (Left and right side)
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites  #Strip .png off off base image and append right or left
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)  #For left need to flip because image begins on right animation
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):  #Size is the dimension of the block in the sprite sheet Terrain
    path = join("assets", "Terrain", "Terrain.png") # Find block wanting to draw
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)  # Create image of size passed in parameter
    rect = pygame.Rect(96, 0, size, size)  # Passing position to load the image from the image that contains all terrians
    surface.blit(image, (0, 0), rect)  # Draw image on the screen
    return pygame.transform.scale2x(surface)  # Double the size of image


class Player(pygame.sprite.Sprite):  # Using sprite to allow for pixel perfect collision
    COLOR = (255, 0, 0)  # Set color for player as a class to make same for all players
    GRAVITY = 1  # If want faster gravity make larger
    ANIMATION_DELAY = 2  # Allows for speed in change of frame if lowered (Time between each sprite shown)
    #(Main character directory, The name of the character wanting to load, width, height, True for multi directional sprite)
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)

    def __init__(self, x, y, width, height):
        super().__init__()  # Initializes super class i:e pygame.sprite.Sprite
        self.rect = pygame.Rect(x, y, width, height)  # Represent player as rectangle i:e: tuple that stores 4 values
        self.x_vel = 0  # Directional velocities
        self.y_vel = 0
        self.mask = None
        self.direction = "left"   # Store what direction player is facing for animation
        self.animation_count = 0  # Count to change animation frames
        self.fall_count = 0  # To determine how much to increment velocity by for how long player has been falling for gravity
        self.jump_count= 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8  # Brings you back down because in loop method downward gravity is being applied to bring character back down
        self.animation_count = 0
        self.jump_count += 1

        # Any gravity accumulated is removed if first jump: Timing matters (Jumps higher for second jump if second jump happens close to when first jump happened)
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0


    # Called once per frame(one iteration of while loop) to update animation for player
    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)   # Start garvity at minimum 1 and then after >1 emulate gravity to accelerate falling speed
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2: # 2 seconds
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1  # Used for gravity variable
        self.update_sprite()  # Call to update sprite every frame

    def landed(self):
        self.fall_count = 0  # Stop adding gravity
        self.y_vel = 0   #Stop going down
        self.jump_count = 0  # For double jump

    def hit_head(self):
        self.count = 0
        self.y_vel = -1

    #Used to update what is being shown on the screen
    def update_sprite(self):
        sprite_sheet = "idle"  #Default sprite sheet
        if self.hit:
           sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:  # When only a low amount of gravity is being applied the character is not "falling" but instead is on the ground
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]

        # Show a different sprite every 5 frames in whatever animation
        # Dynamic and allows for any sprite by allowing to pick a new index for a new sprite
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)

        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    #Update sprite for each frame
    def update(self):
        # Adjusts the rectangle based upon sprite being used to better fit surface of currrent sprite
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))

        # Mask is a mapping of all the pixels on the screen and by overlapping two masks to allow for pixel perfect collision
        self.mask = pygame.mask.from_surface(self.sprite)  # Allows for picture perfection collision by using pixel comparison for collisions

    # Function that handles drawing on the screen
    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


#Base class to allow inheritance and functionality to instantiate a valid sprite
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()  # Initializes super class i:e pygame.sprite.Sprite
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

#Get and draw block onto surface
class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        # Get all animations of fire and its name ("on" or "off")
        sprites = self.fire[self.animation_name]

        #Find animation same as in Player
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        # Update sprite for animations
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        # Since fire is static, animation count can become very big and needs to be set back to zero
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

# Returns a list that contains all background tiles
def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))  # Join assests path with Background path as well as filename
    _, _, width, height, = image.get_rect()  # Returns x,y,width,height of image
    tiles = []  # Empty list of tiles

    for i in range(WIDTH // width + 1):  # Find how many tiles are needed to fill screen in x and y direction
        for j in range(HEIGHT // height + 1):
            pos = (i*width, j*height)   # Denotes position as tuple of the top left corner of current image
            tiles.append(pos)

    return tiles, image


# Function to draw everything: Player, blocks, window, ect...
def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)  # Draw background image with the position of tile found in get_background

    for obj in objects:  # Draw object on the screen
        obj.draw(window, offset_x)

    player.draw(window, offset_x)  # Draw player on screen

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj): # Objects are Inherited from sprite class and have the mask property
            if dy > 0:
                player.rect.bottom = obj.rect.top  # Make top of player = to bottom of object
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom  # Moving up and hitting the bottom of the object
                player.hit_head

            collided_objects.append(obj)

    return collided_objects  # To determine what player has collided with

# Check for horizontal collision first by preemtively moving player in x direction and checking to see if collision takes place
#If so move player back to original position and return colided object
def collide(player, objects, dx):
    player.move(dx, 0)  # Checking to see if the player were to move left or right, if it would cause a collision
    player.update()  # Uodate rectangle and mask before checking for collision
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):  # If collision has occurred
            collided_object = obj
            break

    player.move(-dx, 0)   # Move player back to original position
    player.update()
    return collided_object

# Check key presses and collisions
def handle_move(player, objects):
    keys = pygame.key.get_pressed()   # Find all keys being pressed
    player.x_vel = 0  # Set player velocity back to zero to only move player when holding down the key
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)  # Multiply by two to add a little more space between character and object

    # Check direction of movement and check for horizontal collisions first
    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    # Check for vertical collisions
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)

    # Loop through all objects and determine if fire has been hit
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        # Could be no objects and need to make sure to_check is a defined object before accessing name of object
        if obj and obj.name == "fire":
            player.make_hit()

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")
    block_size = 96  #Size of block desired in the terrain file

    player = Player(100, 100, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    # Create floor of blocks
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
                for i in range(-WIDTH//block_size, (WIDTH*2)//block_size)]

    # *floor passes the statement above into this, same as ... in javascipt
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire]

    offset_x = 0
    scroll_area_width = 200  # Start scrolling when this far from middle on either side of the screen

    run = True
    while run:
        clock.tick(FPS) # Ensures while loop runs 60 frames per second

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            # Jumps are declared here (instead of handle_move method) to make sure key is released to only allow one jump
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:  # Only 2 jumps allowed
                    player.jump()

        player.loop(FPS)  # Actually moves player every frame
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        # Screen rolling implementation
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0 or
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
                offset_x += player.x_vel  # Offset the screen by whatever the velocity was that the player just moved to the right/left


    pygame.quit()
    quit()

# Only call main function if call function directly
if __name__ == "__main__":
    main(window)