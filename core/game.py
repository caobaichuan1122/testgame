# ============================================================
#  Game core: state management, main loop — isometric RPG
# ============================================================
import pygame
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, INTERNAL_WIDTH, INTERNAL_HEIGHT,
    PIXEL_SCALE, FPS, COLOR_BG, WINDOW_TITLE,
    STATE_LOGIN, STATE_MENU, STATE_SETTINGS, STATE_PLAYING,
    STATE_PAUSED, STATE_GAME_OVER, STATE_COMBAT, STATE_SAVE_PROMPT,
    ENABLE_LOGIN,
)
from world.camera import Camera
from entities.entity import EntityManager
from entities.player import Player
from ui.ui_manager import UIManager
from systems.chat_log import ChatLog
from systems.combat_scene import CombatScene
from systems.i18n import t, tf, switch_language, set_language
from core.logger import get_logger

log = get_logger("game")

_PLAYING_STATES = (STATE_PLAYING, STATE_PAUSED, STATE_COMBAT)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        # Load saved settings and apply before creating the display
        from core.settings_manager import SettingsManager
        self.settings_mgr = SettingsManager()
        set_language(self.settings_mgr.language)
        flags = pygame.FULLSCREEN if self.settings_mgr.fullscreen else 0
        w, h = self.settings_mgr.resolution
        self.screen = pygame.display.set_mode((w, h), flags)
        # Sync module-level constants so all UI/entity code uses correct dimensions
        import core.settings as _s
        _s.SCREEN_WIDTH = w
        _s.SCREEN_HEIGHT = h
        _s.PIXEL_SCALE = max(1, w // INTERNAL_WIDTH)

        self.canvas = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_LOGIN if ENABLE_LOGIN else STATE_MENU
        self._settings_caller = STATE_MENU  # which state opened the settings screen

        # Save slot tracking
        self.save_slot = None       # int 1-10, set when entering a slot
        self._prompt_action = None  # "quit" | "main_menu"

        # Music (initialized after display so mixer is ready)
        from systems.music import MusicManager
        self.music_mgr = MusicManager()
        if self.settings_mgr.music_enabled:
            self.music_mgr.play()

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

        # Login UI (created once, lives here)
        from ui.ui_login import LoginUI
        self.login_ui = LoginUI()

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
        self.ui.minimap.build(self.iso_map)

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
                if self.state in _PLAYING_STATES:
                    # Prompt to save before quitting
                    self._prompt_action = "quit"
                    self.ui.menu_ui._prompt_sel = 0
                    self.state = STATE_SAVE_PROMPT
                else:
                    self.running = False
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
            if event.type == pygame.TEXTINPUT:
                if self.state == STATE_LOGIN:
                    self.login_ui.handle_text(event.text)
                elif self.state == STATE_PLAYING:
                    if event.text.lower() == 'e' and not self.ui.has_overlay and not self.ui._chat_input_active:
                        if not (self.dialogue_manager and self.dialogue_manager.is_active):
                            if self.entities.player and self.entities.player.interact_target:
                                self.entities.player.interact_target.interact(self)
                                continue
                    self.ui.handle_text_input(event.text)

    def _handle_keydown(self, key):
        if self.state == STATE_LOGIN:
            result = self.login_ui.handle_key(key, self)
            if result == "offline":
                log.info("Player chose offline mode")
                self.state = STATE_MENU
            elif result is True:
                self.state = STATE_MENU
            return

        elif self.state == STATE_MENU:
            slots = self.ui.menu_ui._get_slots()
            num   = len(slots)
            sel   = self.ui.menu_ui._slot_sel

            if key == pygame.K_UP:
                self.ui.menu_ui._slot_sel = (sel - 1) % num
            elif key == pygame.K_DOWN:
                self.ui.menu_ui._slot_sel = (sel + 1) % num
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                slot_num = sel + 1
                meta = slots[sel]
                if meta:
                    # Occupied slot — load save
                    from core.save_manager import load as load_save
                    if load_save(self, slot_num):
                        self.save_slot = slot_num
                        self.state = STATE_PLAYING
                        self.chat_log.add(tf("load_from_slot", n=slot_num), "system")
                        log.info("Loaded slot %d", slot_num)
                else:
                    # Empty slot — start fresh
                    self.load_level()
                    self.save_slot = slot_num
                    self.state = STATE_PLAYING
                    log.info("New game in slot %d", slot_num)
            elif key == pygame.K_DELETE or key == pygame.K_BACKSPACE:
                slot_num = sel + 1
                from core.save_manager import delete_slot
                delete_slot(slot_num)
                self.ui.menu_ui.refresh_slots()
            elif key == pygame.K_s:
                self._settings_caller = STATE_MENU
                self.state = STATE_SETTINGS
            elif key == pygame.K_l:
                switch_language()
                self.ui.menu_ui.refresh_slots()
            elif key == pygame.K_ESCAPE:
                self.running = False

        elif self.state == STATE_SETTINGS:
            self._handle_settings_key(key)

        elif self.state == STATE_PLAYING:
            if key == pygame.K_F5:
                slot = self.save_slot if self.save_slot else 1
                from core.save_manager import save as save_game
                if save_game(self, slot):
                    if self.save_slot is None:
                        self.save_slot = 1
                    self.ui.menu_ui.refresh_slots()
                    if self.entities.player:
                        self.entities.player.add_message(tf("save_to_slot", n=slot))
                return
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
            sel = self.ui.menu_ui._pause_sel
            num = len(["resume", "settings", "main_menu"])
            if key == pygame.K_ESCAPE:
                self.state = STATE_PLAYING
                self.ui.menu_ui._pause_sel = 0
            elif key == pygame.K_UP:
                self.ui.menu_ui._pause_sel = (sel - 1) % num
            elif key == pygame.K_DOWN:
                self.ui.menu_ui._pause_sel = (sel + 1) % num
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                if sel == 0:   # Resume
                    self.state = STATE_PLAYING
                    self.ui.menu_ui._pause_sel = 0
                elif sel == 1:  # Settings
                    self._settings_caller = STATE_PAUSED
                    self.state = STATE_SETTINGS
                elif sel == 2:  # Main Menu — show save prompt
                    self._prompt_action = "main_menu"
                    self.ui.menu_ui._prompt_sel = 0
                    self.state = STATE_SAVE_PROMPT
            elif key == pygame.K_l:
                switch_language()

        elif self.state == STATE_SAVE_PROMPT:
            num = 3  # Save / Don't Save / Cancel
            if key in (pygame.K_LEFT, pygame.K_UP):
                self.ui.menu_ui._prompt_sel = (self.ui.menu_ui._prompt_sel - 1) % num
            elif key in (pygame.K_RIGHT, pygame.K_DOWN):
                self.ui.menu_ui._prompt_sel = (self.ui.menu_ui._prompt_sel + 1) % num
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                choice = self.ui.menu_ui._prompt_sel
                if choice == 0:  # Save
                    slot = self.save_slot if self.save_slot else 1
                    from core.save_manager import save as save_game
                    save_game(self, slot)
                    if self.save_slot is None:
                        self.save_slot = 1
                    self.ui.menu_ui.refresh_slots()
                    self._execute_prompt_action()
                elif choice == 1:  # Don't Save
                    self._execute_prompt_action()
                else:  # Cancel
                    self.state = STATE_PLAYING
            elif key == pygame.K_ESCAPE:
                self.state = STATE_PLAYING

        elif self.state == STATE_GAME_OVER:
            if key == pygame.K_RETURN:
                self.state = STATE_PLAYING
                self.load_level()
            elif key == pygame.K_ESCAPE:
                self.running = False

    def _execute_prompt_action(self):
        """Execute the pending prompt action after save/no-save choice."""
        action = self._prompt_action
        self._prompt_action = None
        if action == "quit":
            self.running = False
        elif action == "main_menu":
            self._return_to_menu()

    def update(self):
        if self.state == STATE_COMBAT:
            self.combat_scene.update()
            if self.combat_scene.combat_finished:
                result = self.combat_scene.result
                enemy  = self.combat_scene.enemy
                self.combat_scene.active = False
                if result == "win":
                    enemy.active = False
                    self.state = STATE_PLAYING
                    log.info("Combat won: defeated %s", enemy.enemy_type)
                elif result == "flee":
                    enemy.combat_cooldown = 180
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
            if self.dialogue_manager and self.dialogue_manager.is_active:
                self.dialogue_manager.update_typewriter()
                return
            if self.ui.has_overlay:
                return
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
        if self.state == STATE_LOGIN:
            self.login_ui.draw(self.screen)

        elif self.state == STATE_MENU:
            self.screen.fill(COLOR_BG)
            self.ui.menu_ui.draw_main_menu(self.screen)

        elif self.state == STATE_SETTINGS:
            self.ui.menu_ui.draw_settings(self.screen, self.settings_mgr)

        elif self.state == STATE_COMBAT:
            self.combat_scene.draw(self.screen)

        elif self.state == STATE_PLAYING:
            self._draw_world()
            self.ui.draw_gameplay(self.screen, self)

        elif self.state == STATE_PAUSED:
            self._draw_world()
            self.ui.draw_gameplay(self.screen, self)
            self.ui.menu_ui.draw_pause(self.screen)

        elif self.state == STATE_SAVE_PROMPT:
            self._draw_world()
            self.ui.draw_gameplay(self.screen, self)
            self.ui.menu_ui.draw_save_prompt(self.screen)

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
        scaled = pygame.transform.scale(self.canvas, self.screen.get_size())
        self.screen.blit(scaled, (0, 0))
        self.entities.draw_labels(self.screen, self.camera)

    def _return_to_menu(self):
        """Tear down the current game world and return to the main menu."""
        self.iso_map = None
        self.entities = EntityManager()
        self.dialogue_manager = None
        self.quest_manager = None
        self.shop_manager = None
        self.chat_log = ChatLog()
        self.combat_scene = CombatScene()
        self.ui.close_all()
        self.ui.menu_ui._pause_sel = 0
        self.ui.menu_ui._slot_sel = 0
        self.ui.menu_ui.refresh_slots()
        self.save_slot = None
        self.state = STATE_MENU
        log.info("Returned to main menu")

    def apply_display_settings(self):
        """Recreate pygame display with current settings; sync module constants."""
        sm = self.settings_mgr
        set_language(sm.language)
        flags = pygame.FULLSCREEN if sm.fullscreen else 0
        w, h = sm.resolution
        self.screen = pygame.display.set_mode((w, h), flags)
        import core.settings as _s
        _s.SCREEN_WIDTH = w
        _s.SCREEN_HEIGHT = h
        _s.PIXEL_SCALE = max(1, w // INTERNAL_WIDTH)
        log.info("Display applied: %dx%d PIXEL_SCALE=%d lang=%s", w, h, _s.PIXEL_SCALE, sm.language)

    def _handle_settings_key(self, key):
        """Handle keyboard input while settings screen is open."""
        sm = self.settings_mgr
        num_opts = 4
        sel = self.ui.menu_ui._settings_sel

        if key in (pygame.K_ESCAPE, pygame.K_RETURN):
            sm.save()
            self.state = self._settings_caller
        elif key == pygame.K_UP:
            self.ui.menu_ui._settings_sel = (sel - 1) % num_opts
        elif key == pygame.K_DOWN:
            self.ui.menu_ui._settings_sel = (sel + 1) % num_opts
        elif key in (pygame.K_LEFT, pygame.K_RIGHT):
            if sel == 0:  # resolution
                if key == pygame.K_LEFT:
                    sm.prev_resolution()
                else:
                    sm.next_resolution()
                self.apply_display_settings()
            elif sel == 1:  # fullscreen
                sm.toggle_fullscreen()
                self.apply_display_settings()
            elif sel == 2:  # language
                sm.toggle_language()
                self.apply_display_settings()
            elif sel == 3:  # music
                sm.toggle_music()
                self.music_mgr.set_enabled(sm.music_enabled)

    def run(self):
        log.info("Main loop started")
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        log.info("Main loop ended")
