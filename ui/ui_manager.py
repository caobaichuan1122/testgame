# ============================================================
#  UI dispatcher: manages all UI subsystems
# ============================================================
import pygame
from ui.ui_hud import HUD
from ui.ui_dialogue import DialogueUI
from ui.ui_inventory import InventoryUI
from ui.ui_shop import ShopUI
from ui.ui_quest import QuestUI
from ui.ui_menu import MenuUI
from ui.ui_chat import ChatUI
from ui.ui_minimap import MinimapUI
from systems.i18n import t, tf
from core.utils import get_font, FONT_UI_SM


class UIManager:
    def __init__(self):
        self.hud = HUD()
        self.dialogue_ui = DialogueUI()
        self.inventory_ui = InventoryUI()
        self.shop_ui = ShopUI()
        self.quest_ui = QuestUI()
        self.menu_ui = MenuUI()
        self.chat_ui = ChatUI()
        self.minimap = MinimapUI()
        self._game = None  # set by game.py when needed

        # Player chat input
        self._chat_input_active = False
        self._chat_input_text = ""

    @property
    def has_overlay(self):
        """Whether any overlay UI is open (blocks game input)."""
        return (self.inventory_ui.active or
                self.shop_ui.active or
                self.quest_ui.active or
                self.chat_ui.expanded or
                self._chat_input_active)

    @property
    def in_dialogue(self):
        return False  # Dialogue is managed by dialogue_manager

    def open_dialogue(self, dialogue_id, speaker=""):
        """Open a dialogue."""
        if self._game and self._game.dialogue_manager:
            self._game.dialogue_manager.start(dialogue_id, speaker)

    def open_shop(self, shop_id):
        self.shop_ui.open(shop_id)

    def close_all(self):
        self.inventory_ui.close()
        self.shop_ui.close()
        self.quest_ui.close()
        self.chat_ui.close()
        self._chat_input_active = False
        self._chat_input_text = ""

    def handle_text_input(self, text):
        """Handle pygame.TEXTINPUT events."""
        if self._chat_input_active:
            self._chat_input_text += text

    def handle_key(self, key, game):
        """Handle UI key events; return True if the key was consumed."""
        # M toggles the minimap (works regardless of other UI state)
        if key == pygame.K_m:
            self.minimap.toggle()
            return True

        # Dialogue takes priority
        if game.dialogue_manager and game.dialogue_manager.is_active:
            self.dialogue_ui.handle_key(key, game.dialogue_manager, game)
            return True

        # While chat input is active
        if self._chat_input_active:
            if key == pygame.K_RETURN:
                # Send message
                msg = self._chat_input_text.strip()
                if msg:
                    game.chat_log.add(tf("you_said", msg=msg), "player")
                self._chat_input_active = False
                self._chat_input_text = ""
                return True
            elif key == pygame.K_ESCAPE:
                self._chat_input_active = False
                self._chat_input_text = ""
                return True
            elif key == pygame.K_BACKSPACE:
                self._chat_input_text = self._chat_input_text[:-1]
                return True
            # Consume all keys while in chat input mode
            return True

        # Message log expanded mode
        if self.chat_ui.expanded:
            if self.chat_ui.handle_key(key, game.chat_log):
                return True

        # Shop UI
        if self.shop_ui.active:
            self.shop_ui.handle_key(key, game.entities.player, game.shop_manager)
            return True

        # Inventory UI
        if self.inventory_ui.active:
            self.inventory_ui.handle_key(key, game.entities.player)
            return True

        # Quest log
        if self.quest_ui.active:
            self.quest_ui.handle_key(key, game.quest_manager)
            return True

        # Enter opens chat input box
        if key == pygame.K_RETURN:
            self._chat_input_active = True
            self._chat_input_text = ""
            return True

        # Open message log (T key)
        if key == pygame.K_t:
            self.chat_ui.toggle()
            return True

        # Open inventory
        if key == pygame.K_i:
            self.inventory_ui.open()
            return True

        # Open quest log
        if key == pygame.K_q:
            self.quest_ui.open()
            return True

        return False

    def draw_gameplay(self, surface, game):
        """Draw all in-game UI."""
        player = game.entities.player

        # HUD
        quest_hint = ""
        if game.quest_manager:
            quest_hint = game.quest_manager.active_quest_hint
        self.hud.draw(surface, player, quest_hint)

        # Minimap
        self.minimap.draw(surface, player, game.entities)

        # Message log (drawn after HUD, before dialogue)
        self.chat_ui.draw(surface, game.chat_log)

        # Chat input box
        if self._chat_input_active:
            self._draw_chat_input(surface)

        # Dialogue box
        if game.dialogue_manager and game.dialogue_manager.is_active:
            self.dialogue_ui.draw(surface, game.dialogue_manager)

        # Overlay UIs
        if self.inventory_ui.active:
            self.inventory_ui.draw(surface, player)
        if self.shop_ui.active:
            self.shop_ui.draw(surface, player, game.shop_manager)
        if self.quest_ui.active:
            self.quest_ui.draw(surface, game.quest_manager)

    def _draw_chat_input(self, surface):
        """Draw the chat input box."""
        sw, sh = surface.get_size()
        font = get_font(FONT_UI_SM)
        box_h = 32
        box_w = sw - 20
        box_x = 10
        box_y = sh - box_h - 10

        # Semi-transparent background
        bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 180))
        surface.blit(bg, (box_x, box_y))
        pygame.draw.rect(surface, (120, 160, 220),
                         (box_x, box_y, box_w, box_h), 1)

        # Prompt + text
        prompt = t("say_prompt")
        display_text = prompt + self._chat_input_text

        # Blinking cursor
        cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        display_text += cursor

        text_surf = font.render(display_text, False, (220, 230, 255))
        surface.blit(text_surf, (box_x + 8, box_y + (box_h - text_surf.get_height()) // 2))

        # Control hint
        hint_surf = font.render(t("chat_send_hint"), False, (120, 120, 140))
        surface.blit(hint_surf, (box_x + box_w - hint_surf.get_width() - 8,
                                 box_y + (box_h - hint_surf.get_height()) // 2))
