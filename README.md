# Middle-earth: Shadows of Arda

[中文](#中文) | [English](#english)

---

## 中文

一款基于 Python + Pygame 的 **45度等距视角像素风 RPG**，以中土世界为背景。

### 游戏特性

- **等距地图**：60×60 瓦片地图，涵盖 8 大地区
- **三种战斗模式**：近战（剑）、远程（弓）、魔法，实时切换
- **回合制战斗场景**：触碰敌人进入独立战斗界面
- **对话系统**：分支对话、打字机效果、回调触发
- **任务系统**：击杀、收集、探索、护送、限时任务五种类型
- **商店 & 背包**：购买装备、道具，管理物品
- **中英双语**：运行时按 `L` 切换语言
- **像素缩放渲染**：内部分辨率 320×213，3× 放大输出 960×640

### 地图区域

| 区域 | 位置 | 特点 |
|------|------|------|
| 法贡森林 Fangorn | 左上 | 古墓尸妖出没，林中小道 |
| 摩瑞亚矿洞 Moria | 中上 | 石窟地牢，BOSS 洞穴巨魔 |
| 迷雾山脉 Misty Mtns | 右上 | 悬崖峭壁 |
| 霍比屯 Hobbiton | 中心 | 村庄广场，NPC 聚集地 |
| 洛汗平原 Rohan | 左中/右中 | 开阔草原，兽人巡逻 |
| 安都因河 Anduin | 左下 | 深水区域 |
| 奥斯吉利亚斯桥 Osgiliath | 中下 | 跨河石桥 |
| 魔多荒原 Mordor | 右下 | 沙漠废土，乌鲁克弓手 |

### 操作说明

| 按键 | 功能 |
|------|------|
| `W / A / S / D` | 8方向移动（等距坐标） |
| `1` | 切换近战模式 |
| `2` | 切换远程模式 |
| `3` | 切换魔法模式 |
| `Z` | 攻击 |
| `E` | 与 NPC 交互 |
| `I` | 打开背包 |
| `Q` | 查看任务日志 |
| `Tab` | 展开/收起消息日志 |
| `L` | 切换中文 / English |
| `Esc` | 暂停 / 返回上级 |

### NPC

| NPC | 类型 | 位置 | 功能 |
|-----|------|------|------|
| Gandalf | 任务 | 霍比屯 | 发布击杀兽人 & BOSS 任务 |
| Barliman | 商店 | 霍比屯 | 综合杂货店 |
| Gimli | 商店 | 霍比屯 | 武器铺，分支对话 |
| Arwen | 治疗 | 霍比屯 | 花费 20 金币全额回血 |
| Boromir | 任务 | 霍比屯北 | 发布探索任务 |
| Frodo | 任务 | 洛汗东 | 发布护送任务 |
| Sam | 任务 | 奥斯吉利亚斯 | 发布限时击杀任务 |

### 任务列表

| 任务 | 类型 | 奖励 |
|------|------|------|
| 消灭兽人 | 击杀 ×5 | 100 XP / 50 金 / 加拉德瑞姆弓 |
| 击败洞穴巨魔 | BOSS 击杀 | 300 XP / 150 金 / 秘银战甲 |
| 收集兽人血 | 收集 ×3 | 80 XP / 40 金 / 米路弗+树须饮 |
| 探索三大区域 | 探索 | 120 XP / 60 金 / 精灵胸针 |
| 护送弗罗多 | 护送 | 100 XP / 80 金 / 米路弗 |
| 限时歼灭乌鲁克 | 限时击杀 ×3 | 150 XP / 100 金 / 巫师法杖 |

### 安装 & 运行

**依赖：** Python 3.9+，Pygame 2.x

```bash
pip install pygame
python main.py
```

### 项目结构

```
testgame/
├── main.py            # 入口
├── game.py            # 主循环 & 状态机
├── settings.py        # 全局配置
├── demo_level.py      # 关卡构建
├── iso_map.py         # 等距地图渲染
├── camera.py          # 摄像机跟随
├── entity.py          # 实体基类 & 管理器
├── player.py          # 玩家逻辑
├── enemy.py           # 敌人 AI
├── npc.py             # NPC 行为
├── combat.py          # 战斗公式
├── combat_scene.py    # 回合制战斗界面
├── dialogue.py        # 对话系统
├── quest.py           # 任务系统
├── shop.py            # 商店系统
├── inventory.py       # 背包 & 道具
├── stats.py           # 角色属性
├── projectile.py      # 弹丸（箭 / 魔法）
├── i18n.py            # 中英国际化
├── sprite_manager.py  # 精灵加载
├── ui_*.py            # 各 UI 模块
├── chat_log.py        # 消息日志
└── assets/            # 素材（不纳入 Git）
    ├── images/
    ├── sounds/
    └── ...
```

---

## English

A **45° isometric pixel-art RPG** built with Python + Pygame, set in the world of Middle-earth.

### Features

- **Isometric Map**: 60×60 tile map spanning 8 distinct regions
- **Three Combat Modes**: Melee (sword), Ranged (bow), Magic — switch anytime
- **Turn-based Combat Scene**: Touch an enemy to enter a dedicated battle screen
- **Dialogue System**: Branching conversations, typewriter effect, callback triggers
- **Quest System**: Five types — Kill, Collect, Explore, Escort, Timed Kill
- **Shop & Inventory**: Buy weapons, items, and manage equipment
- **Bilingual**: Press `L` in-game to toggle between Chinese and English
- **Pixel Scaling**: Internal resolution 320×213, scaled 3× to 960×640

### Map Regions

| Region | Position | Description |
|--------|----------|-------------|
| Fangorn Forest | Top-left | Barrow-wights lurk among ancient trees |
| Mines of Moria | Top-center | Stone dungeon, Cave Troll BOSS |
| Misty Mountains | Top-right | Sheer cliffs and rocky peaks |
| Hobbiton | Center | Village square, NPC hub |
| Fields of Rohan | Mid-left/right | Open plains, orc patrols |
| River Anduin | Bottom-left | Deep river waters |
| Osgiliath Bridge | Bottom-center | Ancient stone bridge crossing |
| Mordor Wastes | Bottom-right | Barren desert, Uruk-hai archers |

### Controls

| Key | Action |
|-----|--------|
| `W / A / S / D` | Move in 8 directions (isometric) |
| `1` | Switch to Melee mode |
| `2` | Switch to Ranged mode |
| `3` | Switch to Magic mode |
| `Z` | Attack |
| `E` | Interact with NPC |
| `I` | Open Inventory |
| `Q` | View Quest Log |
| `Tab` | Toggle message log |
| `L` | Switch language |
| `Esc` | Pause / Back |

### NPCs

| NPC | Type | Location | Role |
|-----|------|----------|------|
| Gandalf | Quest | Hobbiton | Issues orc-kill & BOSS quests |
| Barliman | Shop | Hobbiton | General goods store |
| Gimli | Shop | Hobbiton | Weapon shop, branching dialogue |
| Arwen | Healer | Hobbiton | Full heal for 20 gold |
| Boromir | Quest | North Hobbiton | Issues exploration quest |
| Frodo | Quest | East Rohan | Issues escort quest |
| Sam | Quest | Osgiliath | Issues timed kill quest |

### Quest List

| Quest | Type | Rewards |
|-------|------|---------|
| Slay the Orcs | Kill ×5 | 100 XP / 50 Gold / Galadhrim Bow |
| Defeat Cave Troll | BOSS Kill | 300 XP / 150 Gold / Mithril Coat |
| Collect Orc Blood | Collect ×3 | 80 XP / 40 Gold / Miruvor + Ent-draught |
| Explore Three Regions | Explore | 120 XP / 60 Gold / Elven Brooch |
| Escort Frodo | Escort | 100 XP / 80 Gold / Miruvor |
| Timed Uruk Purge | Timed Kill ×3 | 150 XP / 100 Gold / Wizard's Staff |

### Installation & Running

**Requirements:** Python 3.9+, Pygame 2.x

```bash
pip install pygame
python main.py
```

### Project Structure

```
testgame/
├── main.py            # Entry point
├── game.py            # Main loop & state machine
├── settings.py        # Global config
├── demo_level.py      # Level builder
├── iso_map.py         # Isometric map renderer
├── camera.py          # Camera follow
├── entity.py          # Entity base class & manager
├── player.py          # Player logic
├── enemy.py           # Enemy AI
├── npc.py             # NPC behaviors
├── combat.py          # Damage formulas
├── combat_scene.py    # Turn-based battle screen
├── dialogue.py        # Dialogue system
├── quest.py           # Quest system
├── shop.py            # Shop system
├── inventory.py       # Inventory & items
├── stats.py           # Character stats
├── projectile.py      # Projectiles (arrows / magic)
├── i18n.py            # Bilingual i18n
├── sprite_manager.py  # Sprite loader
├── ui_*.py            # UI modules
├── chat_log.py        # Message log
└── assets/            # Assets (excluded from Git)
    ├── images/
    ├── sounds/
    └── ...
```
