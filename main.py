import pygame
import sys

# ====================
# INITIAL SETUP
# ====================
pygame.init()
player_img = pygame.image.load("assets/monkey.png")
WIDTH, HEIGHT = 800, 450
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Mario-Style Game")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 32)

# ====================
# COLORS
# ====================
SKY = (135, 206, 235)
GROUND = (110, 180, 90)
BROWN = (150, 100, 60)
RED = (220, 50, 50)
BLACK = (20, 20, 20)
GRAY = (160, 160, 160)

# ====================
# PLAYER
# ====================
player = pygame.Rect(100, HEIGHT - 120, 40, 50)
player_vel_y = 0
speed = 5
jump_power = -15
gravity = 1
on_ground = False

# ====================
# WORLD OBJECTS
# ====================
platforms = [
    pygame.Rect(0, HEIGHT - 50, 2000, 50),
    pygame.Rect(300, HEIGHT - 150, 120, 20),
    pygame.Rect(520, HEIGHT - 220, 120, 20),
    pygame.Rect(800, HEIGHT - 170, 120, 20),
]

castle = pygame.Rect(1800, HEIGHT - 200, 120, 150)
flag = pygame.Rect(1750, HEIGHT - 250, 10, 200)

# ====================
# CAMERA
# ====================
camera_x = 0

# ====================
# GAME STATE
# ====================
win = False

# ====================
# FUNCTIONS
# ====================

def move_player(keys):
    global on_ground

    dx = 0
    if keys[pygame.K_LEFT]:
        dx = -speed
    if keys[pygame.K_RIGHT]:
        dx = speed

    player.x += dx

    # gravity
    global player_vel_y
    player_vel_y += gravity
    player.y += player_vel_y

    on_ground = False
    for plat in platforms:
        if player.colliderect(plat) and player_vel_y >= 0:
            player.bottom = plat.top
            player_vel_y = 0
            on_ground = True


def draw_world():
    SCREEN.fill(SKY)

    for plat in platforms:
        pygame.draw.rect(SCREEN, GROUND, (plat.x - camera_x, plat.y, plat.width, plat.height))

    pygame.draw.rect(SCREEN, GRAY, (flag.x - camera_x, flag.y, flag.width, flag.height))
    pygame.draw.rect(SCREEN, RED, (castle.x - camera_x, castle.y, castle.width, castle.height))


def draw_player():
    pygame.draw.rect(SCREEN, BROWN, (player.x - camera_x, player.y, player.width, player.height))


def check_win():
    global win
    if player.colliderect(castle):
        win = True

# ====================
# MAIN LOOP
# ====================
while True:
    CLOCK.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and on_ground:
                player_vel_y = jump_power

    keys = pygame.key.get_pressed()

    if not win:
        move_player(keys)
        check_win()

        # camera follows player
        camera_x = player.x - WIDTH // 3
        camera_x = max(0, camera_x)

        draw_world()
        draw_player()

        SCREEN.blit(FONT.render("Reach the castle!", True, BLACK), (20, 20))
    else:
        SCREEN.fill(SKY)
        SCREEN.blit(FONT.render("YOU WIN!", True, BLACK), (WIDTH//2 - 80, HEIGHT//2))

    pygame.display.update()
