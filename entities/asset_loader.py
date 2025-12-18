import pygame
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

class AssetLoader:
    def __init__(self):
        self.bg_img = None
        self.player_idle_img = None
        self.player_walk_frames_right = []
        self.player_walk_frames_left = []
        self.player_idle_left = None
        self.player_jump_right = None
        self.player_jump_left = None
        self.castle_img = None
        self.flag_img = None
        self.enemy_img_left = None
        self.enemy_img_right = None
        self.coin_img = None
        self.wood_img = None
        self.ground_img = None
        self.win_sound = None
        self.coin_sound = None
        self.enemy_die_sound = None

        self.load_assets()

    def load_assets(self):
        # Background
        try:
            bg_original = pygame.image.load(os.path.join(ASSETS_DIR, "background.jpg")).convert()
            self.bg_img = pygame.transform.scale(bg_original, (800, 450))  # Assuming fixed size for now
        except:
            self.bg_img = None

        # Player images
        try:
            monkey_original = pygame.image.load(os.path.join(ASSETS_DIR, "monkey.png")).convert_alpha()
            self.player_idle_img = pygame.transform.scale(monkey_original, (60, 60))

            # Walking frames
            try:
                monkey_lau = pygame.image.load(os.path.join(ASSETS_DIR, "monkey_lau.png")).convert_alpha()
                monkey_rau = pygame.image.load(os.path.join(ASSETS_DIR, "monkey_rau.png")).convert_alpha()
                f0 = pygame.transform.scale(monkey_rau, (60, 60))
                f1 = pygame.transform.scale(monkey_lau, (60, 60))
                self.player_walk_frames_right = [f0, f1]
                self.player_walk_frames_left = [pygame.transform.flip(f, True, False) for f in self.player_walk_frames_right]
            except:
                pass

            self.player_idle_left = pygame.transform.flip(self.player_idle_img, True, False)

            # Jumping
            try:
                monkey_jumping = pygame.image.load(os.path.join(ASSETS_DIR, "monkey_jumping.png")).convert_alpha()
                self.player_jump_right = pygame.transform.scale(monkey_jumping, (60, 60))
                self.player_jump_left = pygame.transform.flip(self.player_jump_right, True, False)
            except:
                pass
        except:
            pass

        # Castle and flag
        try:
            castle_original = pygame.image.load(os.path.join(ASSETS_DIR, "castle.png")).convert_alpha()
            self.castle_img = castle_original
        except:
            pass

        try:
            flag_original = pygame.image.load(os.path.join(ASSETS_DIR, "flag.png")).convert_alpha()
            self.flag_img = flag_original
        except:
            pass

        # Enemy
        try:
            mushroom_original = pygame.image.load(os.path.join(ASSETS_DIR, "mushroom.png")).convert_alpha()
            self.enemy_img_left = pygame.transform.scale(mushroom_original, (65, 65))
            self.enemy_img_right = pygame.transform.flip(self.enemy_img_left, True, False)
        except:
            pass

        # Coin
        try:
            coin_original = pygame.image.load(os.path.join(ASSETS_DIR, "coin.png")).convert_alpha()
            self.coin_img = coin_original
        except:
            pass

        # Wood
        try:
            wood_original = pygame.image.load(os.path.join(ASSETS_DIR, "wood.jpg")).convert_alpha()
            self.wood_img = wood_original
        except:
            pass

        # Ground
        try:
            try:
                ground_original = pygame.image.load(os.path.join(ASSETS_DIR, "ground.jpg")).convert_alpha()
            except:
                ground_original = pygame.image.load(os.path.join(ASSETS_DIR, "grond.png")).convert_alpha()
            self.ground_img = ground_original
        except:
            pass

        # Sounds
        try:
            pygame.mixer.init()
            win_path = os.path.join(ASSETS_DIR, "Sounds", "VSE.mp3")
            if os.path.exists(win_path):
                self.win_sound = pygame.mixer.Sound(win_path)

            coin_path = os.path.join(ASSETS_DIR, "sounds", "coin_sound.mp3")
            if os.path.exists(coin_path):
                self.coin_sound = pygame.mixer.Sound(coin_path)

            enemy_die_path = os.path.join(ASSETS_DIR, "sounds", "roblox_oof.mp3")
            if os.path.exists(enemy_die_path):
                self.enemy_die_sound = pygame.mixer.Sound(enemy_die_path)
        except:
            pass