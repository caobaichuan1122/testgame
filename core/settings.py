# ============================================================
#  Global game settings — 45° isometric open-world RPG
# ============================================================
import os

# --- Asset paths ---
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
SPRITE_CONFIG = os.path.join(ASSETS_DIR, "config.json")

# --- Window ---
WINDOW_TITLE = "Middle-earth: Shadows of Arda"
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
PIXEL_SCALE = 3
INTERNAL_WIDTH = SCREEN_WIDTH // PIXEL_SCALE   # 320
INTERNAL_HEIGHT = SCREEN_HEIGHT // PIXEL_SCALE  # ~213

# --- Frame rate ---
FPS = 60

# --- Isometric tiles ---
TILE_W = 32    # diamond width (internal resolution)
TILE_H = 16    # diamond height
HALF_W = TILE_W // 2   # 16
HALF_H = TILE_H // 2   # 8

# --- Map ---
MAP_COLS = 60
MAP_ROWS = 60

# --- Player ---
PLAYER_SPEED = 1.8       # world units per frame
PLAYER_COLOR = (80, 180, 255)
PLAYER_SIZE = (12, 12)   # collision radius approximation

# --- Combat modes ---
COMBAT_MELEE = 0
COMBAT_RANGED = 1
COMBAT_MAGIC = 2

# Melee params
MELEE_RANGE = 1.5
MELEE_ARC = 90         # degrees
MELEE_COOLDOWN = 30    # frames
MELEE_BASE_DMG = 8

# Ranged params
RANGED_RANGE = 8.0
RANGED_COOLDOWN = 25
RANGED_BASE_DMG = 5
ARROW_SPEED = 3.0

# Magic params
MAGIC_RANGE = 10.0
MAGIC_COOLDOWN = 45
MAGIC_BASE_DMG = 10
MAGIC_COST = 8
MAGIC_SPEED = 2.5

# --- Colors ---
COLOR_BG = (18, 16, 20)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_UI = (230, 230, 230)
COLOR_ACCENT = (255, 90, 95)
COLOR_HP = (220, 50, 50)
COLOR_MP = (50, 100, 220)
COLOR_XP = (50, 200, 100)
COLOR_GOLD = (255, 215, 0)
COLOR_OVERLAY = (0, 0, 0, 150)

# Terrain colors
COLOR_GRASS = (70, 140, 55)          # warm Shire green
COLOR_GRASS_DARK = (45, 100, 35)     # deep Fangorn green
COLOR_DIRT = (130, 100, 60)          # ancient dirt road
COLOR_STONE = (100, 105, 115)        # Dwarven stone
COLOR_STONE_DARK = (70, 72, 82)      # Moria deep stone
COLOR_WATER = (40, 85, 170)          # River Anduin
COLOR_WATER_DEEP = (25, 55, 140)     # deep water
COLOR_SAND = (160, 130, 90)          # Mordor wastes
COLOR_BRIDGE = (140, 100, 50)        # ancient bridge wood
COLOR_TREE = (25, 80, 25)            # ancient forest
COLOR_WALL = (65, 55, 50)            # stone wall
COLOR_CAVE = (50, 45, 55)            # mine cave
COLOR_CLIFF = (90, 80, 75)           # Misty Mountains cliff

# Entity colors
COLOR_ENEMY_ORC = (80, 100, 60)      # orc dark green
COLOR_ENEMY_WIGHT = (160, 170, 180)  # barrow-wight pale
COLOR_ENEMY_URUK = (90, 70, 50)      # Uruk-hai brown
COLOR_ENEMY_TROLL = (120, 100, 80)   # cave troll
COLOR_NPC = (220, 190, 120)          # NPC gold
COLOR_ARROW = (200, 180, 100)
COLOR_MAGIC_BOLT = (130, 80, 255)

# --- Game states ---
STATE_LOGIN = "login"
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"
STATE_COMBAT = "combat"

# --- UI ---
HUD_HEIGHT = 16
DIALOGUE_HEIGHT = 55
INV_WIDTH = 240
INV_HEIGHT = 160
SHOP_WIDTH = 240
SHOP_HEIGHT = 160
QUEST_WIDTH = 220
QUEST_HEIGHT = 150

# --- Language ---
LANGUAGE = "zh"  # "zh" Chinese, "en" English

# --- Online features ---
# Set to True when Django backend is ready to enable login screen
ENABLE_LOGIN = False

# --- Message log ---
CHAT_LOG_MAX_DISPLAY = 15   # max visible lines in expanded mode
CHAT_LOG_FADE_TICKS = 180   # frames before compact messages start fading (3 s @ 60 FPS)
