import pygame
import random
import math

from entities.player import Player
from entities.enemies import BossEnemy


def speel(screen, pause_menu, assets, sfx_on):
    WIDTH, HEIGHT = screen.get_size()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 40)

    # Background
    bg = assets.get("bg_boss") or assets.get("bg")

    # Ground
    ground_height = 70
    ground_rect = pygame.Rect(0, HEIGHT - ground_height, WIDTH, ground_height)
    grond_img = assets.get("ground_boss") or assets.get("ground")

    # Player
    player = Player(100, HEIGHT - ground_height - 60, assets)
    player_vel_y = 0
    speed = 6
    jump_power = -15
    gravity = 1
    on_ground = False
    direction = 1
    walk_frame = 0
    anim_timer = 0

    # Boss (NOW USING BossEnemy)
    boss = BossEnemy(WIDTH // 2 - 50, 50, 100, 100, assets)

    # Knives
    knives = []

    ammo_speed = 3
    ammo_speed_increase_interval = 7  # seconds
    last_ammo_speed_increase = pygame.time.get_ticks()

    # Score
    score = 0
    score_rate = 10
    score_increase_interval = 5
    last_score_increase = 0

    game_over = False
    running = True

    while running:
        dt = clock.tick(60)

        # ---------------- EVENTS ----------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    result = pause_menu(screen)
                    if result == "MENU":
                        return "MENU"

                if event.key == pygame.K_UP and on_ground:
                    player_vel_y = jump_power

        # ---------------- INPUT ----------------
        keys = pygame.key.get_pressed()
        is_moving = False

        if keys[pygame.K_LEFT]:
            player.rect.x -= speed
            direction = -1
            is_moving = True

        if keys[pygame.K_RIGHT]:
            player.rect.x += speed
            direction = 1
            is_moving = True

        # ---------------- PLAYER ANIMATION ----------------
        if is_moving and on_ground:
            anim_timer += dt
            if anim_timer > 150:
                walk_frame = 1 - walk_frame
                anim_timer = 0
        else:
            walk_frame = 0

        player.update_visuals(
            player_vel_y, on_ground, direction, walk_frame, is_moving
        )

        # ---------------- PLAYER PHYSICS ----------------
        player_vel_y += gravity
        player.rect.y += player_vel_y

        on_ground = False
        if player.rect.colliderect(ground_rect) and player_vel_y >= 0:
            if player.rect.bottom <= ground_rect.top + 20:
                player.rect.bottom = ground_rect.top
                player_vel_y = 0
                on_ground = True

        if player.rect.left < 0:
            player.rect.left = 0
        if player.rect.right > WIDTH:
            player.rect.right = WIDTH

        # ---------------- BOSS UPDATE ----------------
        boss.update(dt, WIDTH)
        boss.handle_attacks(knives, ammo_speed)

        # ---------------- AMMO SPEED SCALE ----------------
        if pygame.time.get_ticks() - last_ammo_speed_increase >= ammo_speed_increase_interval * 1000:
            last_ammo_speed_increase = pygame.time.get_ticks()
            ammo_speed += 1

        # ---------------- KNIFE MOVEMENT ----------------
        for knife in knives:
            knife["rect"].x += knife["vx"]
            knife["rect"].y += knife["vy"]

        knives = [
            k for k in knives
            if k["rect"].top < HEIGHT and 0 <= k["rect"].right <= WIDTH
        ]

        # ---------------- COLLISION ----------------
        if not game_over:
            for knife in knives:
                if player.rect.colliderect(knife["rect"]):
                    game_over = True
                    break

        # ---------------- SCORE ----------------
        if not game_over:
            score += score_rate * (dt / 1000)
            if pygame.time.get_ticks() - last_score_increase >= score_increase_interval * 1000:
                last_score_increase = pygame.time.get_ticks()
                score_rate *= 1.1

        # ---------------- DRAW ----------------
        if bg:
            screen.blit(
                pygame.transform.smoothscale(bg, (WIDTH, HEIGHT)),
                (0, 0)
            )
        else:
            screen.fill((50, 50, 100))

        # Ground
        if grond_img:
            orig_w, orig_h = grond_img.get_size()
            tile_h = ground_rect.height
            tile_w = int(orig_w * (tile_h / orig_h)) if orig_h else tile_h
            tile_w = max(tile_w, 64)

            tile_img = pygame.transform.scale(grond_img, (tile_w, tile_h))
            draw_x = 0
            while draw_x < WIDTH:
                screen.blit(tile_img, (draw_x, ground_rect.y))
                tint = pygame.Surface((tile_w, tile_h), pygame.SRCALPHA)
                tint.fill((0, 0, 0, 100))
                screen.blit(tint, (draw_x, ground_rect.y))
                draw_x += tile_w

        # Boss
        boss.draw(screen)

        # Knives
        lightning_img = assets.get("lightning_bolt")
        for knife in knives:
            if lightning_img:
                angle = -math.degrees(math.atan2(knife["vx"], knife["vy"])) if knife["vy"] else 0
                rotated = pygame.transform.rotate(lightning_img, angle)
                rect = rotated.get_rect(center=knife["rect"].center)
                screen.blit(rotated, rect.topleft)
            else:
                pygame.draw.rect(screen, (255, 255, 0), knife["rect"])

        # Player
        if not game_over:
            player.draw(screen, 0)

        # Score
        score_text = font.render(f"Score: {int(score)}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        # ---------------- GAME OVER ----------------
        if game_over:
            over_font = pygame.font.SysFont(None, 80)
            over_text = over_font.render("YOU DIED", True, (255, 0, 0))
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 60))

            score_over = font.render(f"Final Score: {int(score)}", True, (255, 255, 255))
            screen.blit(score_over, (WIDTH // 2 - score_over.get_width() // 2, HEIGHT // 2 + 10))

            restart_text = font.render("Press Enter to restart", True, (255, 255, 0))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))

            pygame.display.update()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "QUIT"
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            return speel(screen, pause_menu, assets, sfx_on)
                        if event.key == pygame.K_ESCAPE:
                            return "MENU"
                clock.tick(30)

        pygame.display.update()

    return "MENU"
