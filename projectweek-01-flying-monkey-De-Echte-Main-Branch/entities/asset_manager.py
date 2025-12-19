import pygame
import os

class AssetManager:
    def __init__(self, width, height):
        self.assets = {}
        self.width = width
        self.height = height
        self.load_all()

    def load_all(self):
        self._load_image("cloud", "assets/cloud.png", (120, 80))
        # --- ACHTERGRONDEN ---
        self._load_image("bg", "assets/background.jpg", (self.width, self.height))
        self._load_image("bg2", "assets/BACKKKground.jpg", (self.width, self.height), fallback="bg")
        # Boss level background and ground
        self._load_image("bg_boss", "assets/background_boss.gif", (self.width, self.height))
        self._load_image("ground_boss", "assets/cobblestone.png", None)
        # Load and rotate lightning bolt slightly to the left
        try:
            img = pygame.image.load("assets/lightning_bolt.png").convert_alpha()
            img = pygame.transform.scale(img, (30, 30))
            img = pygame.transform.rotate(img, 10)  # Rotate 20 degrees to the left
            self.assets["lightning_bolt"] = img
        except:
            self.assets["lightning_bolt"] = None

        # --- SPELER ---
        # Idle
        if self._load_image("idle", "assets/monkey.png", (60, 50)):
            # Loop animaties (alleen als idle bestaat)
            try:
                rau = pygame.image.load("assets/monkey_rau.png").convert_alpha()
                lau = pygame.image.load("assets/monkey_lau.png").convert_alpha()
                f0 = pygame.transform.scale(rau, (60, 50))
                f1 = pygame.transform.scale(lau, (60, 50))
                self.assets["walk_right"] = [f0, f1]
                self.assets["walk_left"] = [pygame.transform.flip(f, True, False) for f in self.assets["walk_right"]]
            except:
                self.assets["walk_right"] = []
                self.assets["walk_left"] = []

            # Spring animatie
            try:
                jump = pygame.image.load("assets/monkey_jumping.png").convert_alpha()
                r = pygame.transform.scale(jump, (60, 65))
                self.assets["jump_right"] = r
                self.assets["jump_left"] = pygame.transform.flip(r, True, False)
            except:
                self.assets["jump_right"] = None
                self.assets["jump_left"] = None
        else:
            print("FOUT: monkey.png niet gevonden!")

        # --- VIJANDEN & ITEMS ---
        self._load_image("enemy", "assets/mushroom.png", (50, 40))
        self._load_image("coin", "assets/banana.png", (30, 30))
        self._load_image("knife", "assets/knifes.png", (50, 100))
        # Snake animation frames
        self._load_image("slang", "assets/slang.png", (60, 40))
        self._load_image("slang_tong", "assets/slang_tong.png", (60, 40))

        # --- OMGEVING ---
        self._load_image("castle", "assets/castle.png", None) # Geen vaste grootte hier, doen we in class
        self._load_image("flag", "assets/flag.png", None)
        self._load_image("platform", "assets/platform.jpg", None)
        
        # Grond met fallback
        try:
            self._load_image("ground", "assets/ground.jpg", None)
        except:
            self._load_image("ground", "assets/grond.png", None)

        # --- GELUID ---
        pygame.mixer.init()
        win_path = os.path.join("assets", "Sounds", "VSE.mp3")
        oof_path = os.path.join("assets", "sounds", "roblox_oof.mp3")
        coin_path = os.path.join("assets", "sounds", "coin_sound.mp3")
        self.assets["win_sound"] = win_path if os.path.exists(win_path) else None
        self.assets["oof_sound"] = oof_path if os.path.exists(oof_path) else None
        self.assets["coin_sound"] = coin_path if os.path.exists(coin_path) else None

    def _load_image(self, name, path, scale_size, fallback=None):
        """Hulpmethode om code schoon te houden"""
        try:
            img = pygame.image.load(path).convert_alpha()
            if scale_size:
                img = pygame.transform.scale(img, scale_size)
            self.assets[name] = img
            return True
        except:
            if fallback and fallback in self.assets:
                self.assets[name] = self.assets[fallback]
            else:
                self.assets[name] = None
            return False

    def get(self, name):
        return self.assets.get(name)