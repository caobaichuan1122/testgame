# ============================================================
#  游戏全局配置 — 45度等距视角开放世界RPG
# ============================================================
import os

# --- 素材路径 ---
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
SPRITE_CONFIG = os.path.join(ASSETS_DIR, "config.json")

# --- 窗口 ---
WINDOW_TITLE = "Middle-earth: Shadows of Arda"
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
PIXEL_SCALE = 3
INTERNAL_WIDTH = SCREEN_WIDTH // PIXEL_SCALE   # 320
INTERNAL_HEIGHT = SCREEN_HEIGHT // PIXEL_SCALE  # ~213

# --- 帧率 ---
FPS = 60

# --- 等距瓦片 ---
TILE_W = 32    # 菱形宽度（内部分辨率）
TILE_H = 16    # 菱形高度
HALF_W = TILE_W // 2   # 16
HALF_H = TILE_H // 2   # 8

# --- 地图 ---
MAP_COLS = 60
MAP_ROWS = 60

# --- 玩家 ---
PLAYER_SPEED = 1.8       # 世界坐标单位/帧
PLAYER_COLOR = (80, 180, 255)
PLAYER_SIZE = (12, 12)   # 碰撞半径近似

# --- 战斗模式 ---
COMBAT_MELEE = 0
COMBAT_RANGED = 1
COMBAT_MAGIC = 2

# 近战参数
MELEE_RANGE = 1.5
MELEE_ARC = 90         # 度
MELEE_COOLDOWN = 30    # 帧
MELEE_BASE_DMG = 8

# 远程参数
RANGED_RANGE = 8.0
RANGED_COOLDOWN = 25
RANGED_BASE_DMG = 5
ARROW_SPEED = 3.0

# 魔法参数
MAGIC_RANGE = 10.0
MAGIC_COOLDOWN = 45
MAGIC_BASE_DMG = 10
MAGIC_COST = 8
MAGIC_SPEED = 2.5

# --- 颜色 ---
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

# 地形颜色
COLOR_GRASS = (70, 140, 55)          # 夏尔温暖绿
COLOR_GRASS_DARK = (45, 100, 35)     # 法贡森林深绿
COLOR_DIRT = (130, 100, 60)          # 古老泥路
COLOR_STONE = (100, 105, 115)        # 矮人石
COLOR_STONE_DARK = (70, 72, 82)      # 摩瑞亚深石
COLOR_WATER = (40, 85, 170)          # 安都因河
COLOR_WATER_DEEP = (25, 55, 140)     # 深水
COLOR_SAND = (160, 130, 90)          # 魔多荒地
COLOR_BRIDGE = (140, 100, 50)        # 古桥木
COLOR_TREE = (25, 80, 25)            # 古森林
COLOR_WALL = (65, 55, 50)            # 石墙
COLOR_CAVE = (50, 45, 55)            # 矿洞
COLOR_CLIFF = (90, 80, 75)           # 迷雾山脉

# 实体颜色
COLOR_ENEMY_ORC = (80, 100, 60)      # 兽人暗绿
COLOR_ENEMY_WIGHT = (160, 170, 180)  # 古墓尸妖苍白
COLOR_ENEMY_URUK = (90, 70, 50)      # 乌鲁克褐
COLOR_ENEMY_TROLL = (120, 100, 80)   # 洞穴巨魔
COLOR_NPC = (220, 190, 120)          # 古朴NPC金
COLOR_ARROW = (200, 180, 100)
COLOR_MAGIC_BOLT = (130, 80, 255)

# --- 游戏状态 ---
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

# --- 语言 ---
LANGUAGE = "zh"  # "zh" 中文, "en" English

# --- 消息日志 ---
CHAT_LOG_MAX_DISPLAY = 15   # 展开模式可见行数上限
CHAT_LOG_FADE_TICKS = 180   # 紧凑模式消息开始淡出的帧数（3秒@60FPS）
