import pygame
import random

def speel(SCREEN):
    WIDTH, HEIGHT = 800, 450
    CLOCK = pygame.time.Clock()
    FONT = pygame.font.SysFont(None, 32)
    BIG_FONT = pygame.font.SysFont(None, 64)
    try:
        bg_original = pygame.image.load("assets/background.jpg")
        bg_img = pygame.transform.scale(bg_original, (WIDTH, HEIGHT))
    except:
        bg_img = None
    original_image = pygame.image.load("assets/monkey.png")
    player_img = pygame.transform.scale(original_image, (40, 50))
    knife_original = pygame.image.load("assets/knifes.png")
    knife_img = pygame.transform.scale(knife_original, (50, 100))
    SKY = (135, 206, 235)
    GROUND_COLOR = (110, 180, 90)
    RED = (220, 50, 50)
    BLACK = (20, 20, 20)
    GRAY = (160, 160, 160)
    player = pygame.Rect(100, HEIGHT - 120, 32, 45)
    player_vel_y = 0
    on_ground = False
    camera_x = 0
    game_over = False
    win = False
    enemies = []
    platforms = [pygame.Rect(0, HEIGHT - 50, 500, 50)]
    current_x = 500
    last_platform_y = HEIGHT - 50
    MAX_JUMP_X = 120
    MAX_JUMP_Y = 120
    HALF_SCREEN_Y = HEIGHT // 2
    while current_x < 3000:
        gap = random.randint(40, MAX_JUMP_X)
        w = random.randint(120, 250)
        min_y = last_platform_y - MAX_JUMP_Y
        max_y = last_platform_y + 40
        min_y = max(HALF_SCREEN_Y, min_y)
        max_y = min(HEIGHT - 60, max_y)
        h = random.randint(min_y, max_y)
        current_x += gap
        platforms.append(pygame.Rect(current_x, h, w, 20))
        last_platform_y = h
        current_x += w
    castle_x = current_x + 100
    platforms.append(pygame.Rect(castle_x - 100, HEIGHT - 50, 500, 50))
    castle = pygame.Rect(castle_x, HEIGHT - 200, 120, 150)
    flag = pygame.Rect(castle_x - 50, HEIGHT - 250, 10, 200)
    speed = 5
    jump_power = -15
    gravity = 1
    running = True
    while running:
        CLOCK.tick(60)
        if bg_img:
            SCREEN.blit(bg_img, (0, 0))
        else:
            SCREEN.fill(SKY)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"
                if event.key == pygame.K_UP and on_ground and not game_over and not win:
                    player_vel_y = jump_power
                if event.key == pygame.K_r and (game_over or win):
                    return speel(SCREEN)
        keys = pygame.key.get_pressed()
        if not win and not game_over:
            if keys[pygame.K_LEFT]:
                player.x -= speed
            if keys[pygame.K_RIGHT]:
                player.x += speed
            player_vel_y += gravity
            player.y += player_vel_y
            on_ground = False
            for plat in platforms:
                if player.colliderect(plat) and player_vel_y >= 0:
                    if player.bottom <= plat.top + 20:
                        player.bottom = plat.top
                        player_vel_y = 0
                        on_ground = True
            if player.y > HEIGHT:
                game_over = True
            if player.colliderect(castle):
                win = True
            if len(enemies) < 12:
                if len(enemies) < 4 or random.randint(0, 100) < 2:
                    spawn_x = random.randint(int(camera_x), int(camera_x + WIDTH))
                    enemies.append(pygame.Rect(spawn_x, -100, 30, 80))
            for enemy in enemies[:]:
                enemy.y += 5
                if player.colliderect(enemy):
                    game_over = True
                if enemy.y > HEIGHT:
                    enemies.remove(enemy)
            target = player.x - WIDTH // 3
            if target < 0:
                target = 0
            camera_x = target
            for plat in platforms:
                pygame.draw.rect(SCREEN, GROUND_COLOR, (plat.x - camera_x, plat.y, plat.width, plat.height))
            pygame.draw.rect(SCREEN, GRAY, (flag.x - camera_x, flag.y, flag.width, flag.height))
            pygame.draw.rect(SCREEN, RED, (castle.x - camera_x, castle.y, castle.width, castle.height))
            for e in enemies:
                SCREEN.blit(knife_img, (e.x - camera_x, e.y))
            SCREEN.blit(player_img, (player.x - camera_x, player.y))
            SCREEN.blit(FONT.render("Level 2 - Survival (Pas op voor messen!)", True, BLACK), (20, 20))
        elif game_over:
            SCREEN.fill(BLACK)
            SCREEN.blit(BIG_FONT.render("GAME OVER", True, RED), (250, 200))
            SCREEN.blit(FONT.render("Druk R voor retry, ESC voor menu", True, SKY), (220, 260))
        else:
            if bg_img:
                SCREEN.blit(bg_img, (0, 0))
            else:
                SCREEN.fill(SKY)
            SCREEN.blit(BIG_FONT.render("GEWONNEN!", True, BLACK), (250, 200))
            SCREEN.blit(FONT.render("Druk R voor retry, ESC voor menu", True, BLACK), (220, 260))
        pygame.display.update()