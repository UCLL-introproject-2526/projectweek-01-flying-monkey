import pygame
import random
import sys
import math

# ====================
# INITIAL SETUP
# ====================
pygame.init()
WIDTH, HEIGHT = 400, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flying Monke")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 32)
BIG_FONT = pygame.font.SysFont(None, 48)

# ====================
# COLORS
# ====================
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
BLUE = (70, 140, 255)
RED = (220, 60, 60)
GREEN = (60, 200, 120)
YELLOW = (240, 220, 60)
GRAY = (180, 180, 180)
DARK_GRAY = (120, 120, 120)

# ====================
# GAME CONSTANTS
# ====================
LANE_X = [-80, 0, 80]   # logical lane offsets (centered)
ROAD_TOP_WIDTH = 120
ROAD_BOTTOM_WIDTH = 320
ROAD_TOP_Y = 120
ROAD_BOTTOM_Y = HEIGHT
GRAVITY = 1
JUMP_FORCE = -18
SLIDE_TIME = 30

# ====================
# PLAYER
# ====================
player_lane = 0
player_lane_offset = 0   # smooth animation offset
player_y = HEIGHT - 180
player_vel_y = 0
player_width = 40
player_height = 60
player_state = "run"     # run, jump, slide
slide_timer = 0

# ====================
# GAME STATE
# ====================
obstacles = []
coins = []
powerups = []
score = 0
speed = 6
game_over = False
spawn_timer = 0

# ====================
# HELPERS
# ====================

def lane_to_screen_x(lane, depth=1.0):
    """Convert lane + depth to perspective screen X"""
    center = WIDTH // 2
    road_width = ROAD_TOP_WIDTH + (ROAD_BOTTOM_WIDTH - ROAD_TOP_WIDTH) * depth
    lane_spacing = road_width / 3
    return center + (lane * lane_spacing) * 0.6


def draw_road():
    pygame.draw.polygon(
        SCREEN,
        DARK_GRAY,
        [
            (WIDTH//2 - ROAD_TOP_WIDTH//2, ROAD_TOP_Y),
            (WIDTH//2 + ROAD_TOP_WIDTH//2, ROAD_TOP_Y),
            (WIDTH//2 + ROAD_BOTTOM_WIDTH//2, ROAD_BOTTOM_Y),
            (WIDTH//2 - ROAD_BOTTOM_WIDTH//2, ROAD_BOTTOM_Y),
        ],
    )

    # lane lines
    for i in [-1, 1]:
        pygame.draw.line(
            SCREEN,
            GRAY,
            (WIDTH//2 + i * ROAD_TOP_WIDTH//6, ROAD_TOP_Y),
            (WIDTH//2 + i * ROAD_BOTTOM_WIDTH//6, ROAD_BOTTOM_Y),
            3,
        )


def player_rect():
    h = player_height
    if player_state == "slide":
        h = player_height // 2
    return pygame.Rect(player_x - player_width//2, player_y, player_width, h)


def draw_player():
    color = BLUE
    if player_state == "jump":
        color = GREEN
    elif player_state == "slide":
        color = RED

    rect = player_rect()
    pygame.draw.rect(SCREEN, color, rect, border_radius=8)


def spawn_obstacle():
    lane = random.choice([-1, 0, 1])
    kind = random.choice(["low", "high"])
    obstacles.append({
        "lane": lane,
        "y": ROAD_TOP_Y,
        "kind": kind,
    })


def spawn_coin():
    coins.append({
        "lane": random.choice([-1, 0, 1]),
        "y": ROAD_TOP_Y,
    })


def spawn_powerup():
    powerups.append({
        "lane": random.choice([-1, 0, 1]),
        "y": ROAD_TOP_Y,
        "type": "score",
    })


def move_entities(lst):
    for e in lst:
        e["y"] += speed


def draw_obstacles():
    global game_over
    for o in obstacles:
        depth = o["y"] / ROAD_BOTTOM_Y
        x = lane_to_screen_x(o["lane"], depth)
        size = 20 + 40 * depth

        if o["kind"] == "low":
            rect = pygame.Rect(x - size//2, o["y"] + 20, size, size)
        else:
            rect = pygame.Rect(x - size//2, o["y"] - size//2, size, size)

        pygame.draw.rect(SCREEN, BLACK, rect)

        # collision
        if rect.colliderect(player_rect()):
            if o["kind"] == "low" and player_state != "jump":
                game_over = True
            if o["kind"] == "high" and player_state != "slide":
                game_over = True


def draw_coins():
    global score
    for c in coins:
        depth = c["y"] / ROAD_BOTTOM_Y
        x = lane_to_screen_x(c["lane"], depth)
        r = int(6 + 10 * depth)
        pygame.draw.circle(SCREEN, YELLOW, (int(x), int(c["y"])), r)

        if pygame.Rect(x-r, c["y"]-r, r*2, r*2).colliderect(player_rect()):
            score += 50
            coins.remove(c)


def draw_powerups():
    global score
    for p in powerups:
        depth = p["y"] / ROAD_BOTTOM_Y
        x = lane_to_screen_x(p["lane"], depth)
        r = int(8 + 12 * depth)
        pygame.draw.circle(SCREEN, GREEN, (int(x), int(p["y"])), r)

        if pygame.Rect(x-r, p["y"]-r, r*2, r*2).colliderect(player_rect()):
            score += 200
            powerups.remove(p)


def draw_ui():
    SCREEN.blit(FONT.render(f"Score: {score}", True, BLACK), (10, 10))


def reset_game():
    global obstacles, coins, powerups, score, speed, game_over
    global player_lane, player_lane_offset, player_y, player_vel_y, player_state
    obstacles, coins, powerups = [], [], []
    score = 0
    speed = 6
    game_over = False
    player_lane = 0
    player_lane_offset = 0
    player_y = HEIGHT - 180
    player_vel_y = 0
    player_state = "run"

# ====================
# MAIN LOOP
# ====================
while True:
    CLOCK.tick(60)
    SCREEN.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_LEFT and player_lane > -1:
                    player_lane -= 1
                if event.key == pygame.K_RIGHT and player_lane < 1:
                    player_lane += 1
                if event.key == pygame.K_UP and player_state == "run":
                    player_state = "jump"
                    player_vel_y = JUMP_FORCE
                if event.key == pygame.K_DOWN and player_state == "run":
                    player_state = "slide"
                    slide_timer = SLIDE_TIME
            else:
                if event.key == pygame.K_SPACE:
                    reset_game()

    if not game_over:
        # smooth lane animation
        player_lane_offset += (player_lane - player_lane_offset) * 0.2
        player_x = lane_to_screen_x(player_lane_offset, 1.0)

        # jump physics
        if player_state == "jump":
            player_vel_y += GRAVITY
            player_y += player_vel_y
            if player_y >= HEIGHT - 180:
                player_y = HEIGHT - 180
                player_state = "run"

        # slide timer
        if player_state == "slide":
            slide_timer -= 1
            if slide_timer <= 0:
                player_state = "run"

        spawn_timer += 1
        if spawn_timer % 50 == 0:
            spawn_obstacle()
        if spawn_timer % 30 == 0:
            spawn_coin()
        if spawn_timer % 300 == 0:
            spawn_powerup()

        move_entities(obstacles)
        move_entities(coins)
        move_entities(powerups)

        obstacles = [o for o in obstacles if o["y"] < ROAD_BOTTOM_Y + 50]
        coins = [c for c in coins if c["y"] < ROAD_BOTTOM_Y + 50]
        powerups = [p for p in powerups if p["y"] < ROAD_BOTTOM_Y + 50]

        score += 1
        speed += 0.001

        draw_road()
        draw_obstacles()
        draw_coins()
        draw_powerups()
        draw_player()
        draw_ui()

    else:
        draw_road()
        SCREEN.blit(BIG_FONT.render("GAME OVER", True, BLACK), (WIDTH//2 - 120, HEIGHT//2 - 60))
        SCREEN.blit(FONT.render("Press SPACE to restart", True, BLACK), (WIDTH//2 - 130, HEIGHT//2))

    pygame.display.update()
