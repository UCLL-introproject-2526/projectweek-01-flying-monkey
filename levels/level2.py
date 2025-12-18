import pygame
import random
import sys

from entities.player import Player
from entities.castle import Castle
# NIEUW: Importeer de vallende vijand
from entities.enemies import FallingEnemy

def speel(SCREEN, pause_func=None, assets=None):
    WIDTH, HEIGHT = SCREEN.get_size()
    CLOCK = pygame.time.Clock()
    FONT = pygame.font.SysFont(None, 32)
    BIG_FONT = pygame.font.SysFont(None, 64)

    BG_IMG = assets.get("bg2") if assets.get("bg2") else assets.get("bg")
    GROUND_COLOR = (110, 180, 90)
    BLACK = (0, 0, 0)
    RED = (220, 50, 50)
    YELLOW = (255, 215, 0)
    SKY_BLUE = (135, 206, 235)
    GRAY_BOX = (245, 245, 245)

    player = Player(100, HEIGHT - 150, assets)
    
    player_vel_y = 0
    speed = 5
    jump_power = -15
    gravity = 1
    
    on_ground = False
    game_over = False
    win = False
    camera_x = 0
    
    direction = 1
    walk_frame = 0
    anim_timer = 0
    
    # Lijst voor Enemy objecten
    enemies = []
    
    # LEVEL GENERATIE (ongewijzigd)
    platforms = [pygame.Rect(0, HEIGHT - 50, 500, 50)]
    current_x = 500
    last_platform_y = HEIGHT - 50 

    while current_x < 3000:
        gap = random.randint(50, 130) 
        w = random.randint(100, 300)
        max_jump_up = 100 
        if gap > 90: max_jump_up = 60  
        if gap > 110: max_jump_up = 20
        min_y = last_platform_y - max_jump_up  
        max_y = last_platform_y + 100          
        if min_y < 100: min_y = 100             
        if max_y > HEIGHT - 50: max_y = HEIGHT - 50 
        if min_y > max_y: min_y = max_y - 20
        h = random.randint(min_y, max_y)
        current_x += gap
        platforms.append(pygame.Rect(current_x, h, w, 20))
        current_x += w
        last_platform_y = h
    
    castle_x = current_x + 100
    platforms.append(pygame.Rect(castle_x - 100, HEIGHT - 50, 500, 50))
    castle = Castle(castle_x, HEIGHT - 200, 120, 150, assets)

    running = True
    while running:
        dt = CLOCK.tick(60)

        if BG_IMG: SCREEN.blit(BG_IMG, (0,0))
        else: SCREEN.fill((100, 100, 150))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not game_over and not win:
                        if pause_func:
                            if pause_func(SCREEN) == "MENU": return "MENU"
                if event.key == pygame.K_UP and on_ground and not (win or game_over):
                    player_vel_y = jump_power
                if event.key == pygame.K_RETURN and game_over:
                    return speel(SCREEN, pause_func, assets)
                if win and castle.anim_progress >= 1.0:
                    if event.key == pygame.K_m: return "MENU"

        keys = pygame.key.get_pressed()

        if not (win or game_over):
            is_moving = False
            if keys[pygame.K_LEFT]:
                player.rect.x -= speed
                direction = -1
                is_moving = True
            if keys[pygame.K_RIGHT]:
                player.rect.x += speed
                direction = 1
                is_moving = True
            
            if is_moving and on_ground:
                anim_timer += dt
                if anim_timer > 150:
                    walk_frame = 1 - walk_frame
                    anim_timer = 0
            else: walk_frame = 0

            player.update_visuals(player_vel_y, on_ground, direction, walk_frame)
            player_vel_y += gravity
            player.rect.y += player_vel_y

            on_ground = False
            for plat in platforms:
                if player.rect.colliderect(plat) and player_vel_y >= 0:
                    if player.rect.bottom <= plat.top + 20:
                        player.rect.bottom = plat.top
                        player_vel_y = 0
                        on_ground = True
            
            if player.rect.y > HEIGHT: game_over = True
            
            if player.rect.colliderect(castle.rect): 
                win = True
                castle.win_state = True
                if assets.get("win_sound") and castle.anim_progress == 0:
                    try:
                        pygame.mixer.music.load(assets.get("win_sound"))
                        pygame.mixer.music.play()
                    except: pass
            
            castle.update_animation()

            # NIEUW: VIJANDEN SPAWNEN
            if len(enemies) < 17:
                if len(enemies) < 4 or random.randint(0, 100) < 2:
                    spawn_x = random.randint(int(camera_x), int(camera_x + WIDTH))
                    # Maak een FallingEnemy object aan
                    new_knife = FallingEnemy(spawn_x, -100, assets)
                    enemies.append(new_knife)
            
            # NIEUW: VIJANDEN UPDATE
            for enemy in enemies[:]:
                enemy.update() # Laat het mes vallen
                
                # Check botsing
                if player.rect.colliderect(enemy.rect): 
                    game_over = True
                
                # Verwijder als uit beeld
                if enemy.rect.y > HEIGHT: 
                    enemies.remove(enemy)

            camera_x = player.rect.x - WIDTH // 3
            if camera_x < 0: camera_x = 0

        # ================= TEKENEN =================
        if not game_over:
            for plat in platforms:
                if assets.get("ground"):
                    img = pygame.transform.scale(assets.get("ground"), (plat.width, plat.height))
                    SCREEN.blit(img, (plat.x - camera_x, plat.y))
                else: pygame.draw.rect(SCREEN, GROUND_COLOR, (plat.x - camera_x, plat.y, plat.width, plat.height))
        
            castle.draw(SCREEN, camera_x, HEIGHT)

            # NIEUW: VIJANDEN TEKENEN
            for enemy in enemies:
                enemy.draw(SCREEN, camera_x)

            player.draw(SCREEN, camera_x)

            SCREEN.blit(FONT.render("Level 2 - Survival", True, BLACK), (20, 20))

            if win and castle.anim_progress >= 1.0:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 100))
                SCREEN.blit(overlay, (0,0))
                box_w, box_h = 450, 250
                box_x, box_y = WIDTH//2 - box_w//2, HEIGHT//2 - box_h//2
                pygame.draw.rect(SCREEN, GRAY_BOX, (box_x, box_y, box_w, box_h))
                pygame.draw.rect(SCREEN, BLACK, (box_x, box_y, box_w, box_h), 3)
                text1 = BIG_FONT.render("YOU'VE WON!", True, YELLOW)
                text1_outline = BIG_FONT.render("YOU'VE WON!", True, BLACK)
                SCREEN.blit(text1_outline, (WIDTH//2 - text1.get_width()//2 + 2, box_y + 42))
                SCREEN.blit(text1, (WIDTH//2 - text1.get_width()//2, box_y + 40))
                text2 = FONT.render("Good Job!", True, BLACK)
                SCREEN.blit(text2, (WIDTH//2 - text2.get_width()//2, box_y + 100))
                text3 = FONT.render("Press M for Main Menu", True, (50, 50, 50))
                SCREEN.blit(text3, (WIDTH//2 - text3.get_width()//2, box_y + 160))

        else: 
            SCREEN.fill(BLACK)
            text1 = BIG_FONT.render("GAME OVER", True, RED)
            text2 = FONT.render("You Died", True, RED)
            text3 = FONT.render("Press Enter to Retry", True, SKY_BLUE)
            SCREEN.blit(text1, (WIDTH//2 - text1.get_width()//2, HEIGHT//2 - 80))
            SCREEN.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2 - 20))
            SCREEN.blit(text3, (WIDTH//2 - text3.get_width()//2, HEIGHT//2 + 60))

        pygame.display.update()