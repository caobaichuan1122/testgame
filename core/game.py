# ============================================================
#  Game core: state management, main loop — isometric RPG
# ============================================================
import pygame
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, INTERNAL_WIDTH, INTERNAL_HEIGHT,
    PIXEL_SCALE, FPS, COLOR_BG, WINDOW_TITLE,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_COMBAT,
)
from world.camera import Camera
from entities.entity import EntityManager
from entities.player import Player
from ui.ui_manager import UIManager
from systems.chat_log import ChatLog
from systems.combat_scene import CombatScene
from systems.i18n import t, tf, switch_language
from core.logger import get_logger

log = get_logger("game")


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.canvas = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_MENU

        # Subsystems
        self.iso_map = None
        self.camera = Camera()
        self.entities = EntityManager()
        self.chat_log = ChatLog()
        self.ui = UIManager()
        self.ui._game = self
        self.dialogue_manager = None
        self.quest_manager = None
        self.shop_manager = None
        self.combat_scene = CombatScene()

    def load_level(self):
        from world.demo_level import build_demo_level
        log.info("Loading demo level")
        data = build_demo_level()

        self.iso_map = data["iso_map"]
        self.dialogue_manager = data["dialogue_mgr"]
        self.quest_manager = data["quest_mgr"]
        self.shop_manager = data["shop_mgr"]

        self.entities = EntityManager()
        px, py = data["player_start"]
        self.entities.player = Player(px, py)
        self.entities.player.inventory.add_item("sting")
        self.entities.player.inventory.equip("sting")

        for enemy in data["enemies"]:
            self.entities.add_enemy(enemy)
        for npc in data["npcs"]:
            self.entities.add_npc(npc)

        self.camera.snap(px, py)

        self.chat_log = ChatLog()
        self.chat_log.add(t("welcome_msg"), "system")
        log.info("Level loaded: %d enemies, %d NPCs, player at (%s, %s)",
                 len(data["enemies"]), len(data["npcs"]), px, py)

    def start_combat(self, enemy):
        """Trigger turn-based combat."""
        if self.state == STATE_COMBAT:
            return
        log.info("Combat started: player vs %s", enemy.enemy_type)
        self.state = STATE_COMBAT
        self.combat_scene.start(self.entities.player, enemy, self)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
            if event.type == pygame.TEXTINPUT:
                if self.state == STATE_PLAYING:
                    # IME may intercept keystrokes and only emit TEXTINPUT, not KEYDOWN
                    if event.text.lower() == 'e' and not self.ui.has_overlay and not self.ui._chat_input_active:
                        if not (self.dialogue_manager and self.dialogue_manager.is_active):
                            if self.entities.player and self.entities.player.interact_target:
                                self.entities.player.interact_target.interact(self)
                                continue
                    self.ui.handle_text_input(event.text)

    def _handle_keydown(self, key):
        if self.state == STATE_MENU:
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                self.state = STATE_PLAYING
                self.load_level()
            elif key == pygame.K_l:
                switch_language()
            elif key == pygame.K_ESCAPE:
                self.running = False

        elif self.state == STATE_PLAYING:
            if self.ui.handle_key(key, self):
                return
            if self.dialogue_manager and self.dialogue_manager.is_active:
                return
            if key == pygame.K_ESCAPE:
                self.state = STATE_PAUSED
                return
            if self.entities.player:
                self.entities.player.handle_keydown(key, self)

        elif self.state == STATE_COMBAT:
            self.combat_scene.handle_key(key)

        elif self.state == STATE_PAUSED:
            if key == pygame.K_ESCAPE:
                self.state = STATE_PLAYING
            elif key == pygame.K_l:
                switch_language()
                self.load_level()
                self.state = STATE_PLAYING

        elif self.state == STATE_GAME_OVER:
            if key == pygame.K_RETURN:
                self.state = STATE_PLAYING
                self.load_level()
            elif key == pygame.K_ESCAPE:
                self.running = False

    def update(self):
        if self.state == STATE_COMBAT:
            self.combat_scene.update()
            if self.combat_scene.combat_finished:
                result = self.combat_scene.result
                enemy = self.combat_scene.enemy
                self.combat_scene.active = False
                if result == "win":
                    # Enemy is dead, mark as inactive
                    enemy.active = False
                    self.state = STATE_PLAYING
                    log.info("Combat won: defeated %s", enemy.enemy_type)
                elif result == "flee":
                    # Flee success, set combat cooldown on enemy
                    enemy.combat_cooldown = 180  # 3-second cooldown
                    enemy.ai_state = "idle"
                    enemy.ai_timer = 120
                    self.state = STATE_PLAYING
                    log.info("Combat: player fled from %s", enemy.enemy_type)
                elif result == "lose":
                    self.state = STATE_GAME_OVER
                    log.info("Combat lost: player defeated by %s", enemy.enemy_type)
            return

        if self.state == STATE_PLAYING:
            self.chat_log.advance_tick()
            # Advance typewriter effect (must update even with overlay UI)
            if self.dialogue_manager and self.dialogue_manager.is_active:
                self.dialogue_manager.update_typewriter()
                return
            if self.ui.has_overlay:
                return
            # Update timed quest timers
            if self.quest_manager:
                failed = self.quest_manager.update_timers()
                for qid, q in failed:
                    self.chat_log.add(
                        tf("quest_failed_log", name=q['name']), "quest")
                    if self.entities.player:
                        self.entities.player.add_message(t("quest_failed_msg"))

            self.entities.update(self)
            if self.entities.player:
                self.camera.update(
                    self.entities.player.wx,
                    self.entities.player.wy
                )
                if not self.entities.player.stats.alive:
                    self.state = STATE_GAME_OVER
                    log.warning("Player died — game over")

    def draw(self):
        if self.state == STATE_MENU:
            # Menu drawn directly on screen (full screen resolution)
            self.screen.fill(COLOR_BG)
            self.ui.menu_ui.draw_main_menu(self.screen)

        elif self.state == STATE_COMBAT:
            self.combat_scene.draw(self.screen)

        elif self.state == STATE_PLAYING:
            self._draw_world()
            self.ui.draw_gameplay(self.screen, self)

        elif self.state == STATE_PAUSED:
            self._draw_world()
            self.ui.draw_gameplay(self.screen, self)
            self.ui.menu_ui.draw_pause(self.screen)

        elif self.state == STATE_GAME_OVER:
            self._draw_world()
            self.ui.draw_gameplay(self.screen, self)
            self.ui.menu_ui.draw_game_over(self.screen)

        pygame.display.flip()

    def _draw_world(self):
        """Draw game world to canvas, then scale to screen (pixel art)."""
        self.canvas.fill(COLOR_BG)
        if self.iso_map:
            self.iso_map.draw(self.canvas, self.camera)
        self.entities.draw(self.canvas, self.camera)
        scaled = pygame.transform.scale(self.canvas,
                                        (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled, (0, 0))
        # Draw text labels on screen layer (avoid scaling blur)
        self.entities.draw_labels(self.screen, self.camera)

    def run(self):
        log.info("Main loop started")
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        log.info("Main loop ended")
