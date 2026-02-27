# ============================================================
#  Message log UI: compact mode (bottom-left) + expanded mode (scrollable panel)
# ============================================================
import pygame
from core.settings import CHAT_LOG_MAX_DISPLAY, CHAT_LOG_FADE_TICKS
from systems.chat_log import CATEGORY_COLORS
from systems.i18n import t
from core.utils import get_font, ui, FONT_UI_SM


class ChatUI:
    def __init__(self):
        self.expanded = False
        self.scroll_offset = 0  # Scroll offset in expanded mode (from bottom)

    def toggle(self):
        self.expanded = not self.expanded
        self.scroll_offset = 0

    def close(self):
        self.expanded = False
        self.scroll_offset = 0

    def handle_key(self, key, chat_log):
        """Handle scroll keys in expanded mode; return True if key was consumed."""
        if not self.expanded:
            return False
        if key == pygame.K_UP or key == pygame.K_w:
            max_scroll = max(0, len(chat_log.messages) - CHAT_LOG_MAX_DISPLAY)
            self.scroll_offset = min(self.scroll_offset + 1, max_scroll)
            return True
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.scroll_offset = max(0, self.scroll_offset - 1)
            return True
        elif key == pygame.K_t or key == pygame.K_ESCAPE:
            self.close()
            return True
        return False

    def draw(self, surface, chat_log):
        if self.expanded:
            self._draw_expanded(surface, chat_log)
        else:
            self._draw_compact(surface, chat_log)

    def _draw_compact(self, surface, chat_log):
        """Compact mode: show last 5 messages in bottom-left; new=opaque, old=fade."""
        recent = chat_log.get_recent(5)
        if not recent:
            return

        font = get_font(FONT_UI_SM)
        line_h = ui(6)
        base_y = surface.get_height() - ui(20)
        current_tick = chat_log.tick

        for i, (text, category, tick) in enumerate(reversed(recent)):
            age = current_tick - tick
            if age < CHAT_LOG_FADE_TICKS:
                alpha = 255
            else:
                fade_progress = min(1.0, (age - CHAT_LOG_FADE_TICKS) / float(CHAT_LOG_FADE_TICKS))
                alpha = max(40, int(255 * (1.0 - fade_progress * 0.7)))

            color = CATEGORY_COLORS.get(category, (180, 180, 180))
            y = base_y - i * line_h

            text_surf = font.render(text, False, color)
            text_surf.set_alpha(alpha)
            surface.blit(text_surf, (ui(4), y))

    def _draw_expanded(self, surface, chat_log):
        """Expanded mode: semi-transparent panel, scrollable full log."""
        font = get_font(FONT_UI_SM)
        line_h = ui(6)
        panel_w = ui(120)
        panel_h = surface.get_height() - ui(30)
        panel_x = ui(2)
        panel_y = ui(15)

        # Semi-transparent background
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 200))
        surface.blit(panel, (panel_x, panel_y))
        pygame.draw.rect(surface, (80, 80, 100),
                         (panel_x, panel_y, panel_w, panel_h), 1)

        # Title
        title_font = get_font(FONT_UI_SM + 4)
        title_surf = title_font.render(t("message_log"), False, (230, 230, 230))
        surface.blit(title_surf, (panel_x + ui(2), panel_y + ui(1)))

        # Hint
        hint_surf = font.render(t("chat_close_hint"), False, (140, 140, 140))
        surface.blit(hint_surf, (panel_x + ui(2), panel_y + ui(5)))

        # Message area
        msg_area_y = panel_y + ui(9)
        msg_area_h = panel_h - ui(11)
        visible_lines = msg_area_h // line_h

        messages = chat_log.messages
        total = len(messages)
        if total == 0:
            empty_surf = font.render(t("no_messages"), False, (120, 120, 120))
            surface.blit(empty_surf, (panel_x + ui(2), msg_area_y + ui(2)))
            return

        end_idx = total - self.scroll_offset
        start_idx = max(0, end_idx - visible_lines)

        y = msg_area_y + ui(1)
        for i in range(start_idx, end_idx):
            text, category, tick = messages[i]
            color = CATEGORY_COLORS.get(category, (180, 180, 180))
            text_surf = font.render(text, False, color)
            surface.blit(text_surf, (panel_x + ui(2), y))
            y += line_h

        if self.scroll_offset > 0:
            arrow_surf = font.render(t("more_below"), False, (140, 140, 140))
            surface.blit(arrow_surf, (panel_x + ui(2), panel_y + panel_h - ui(3)))
        if start_idx > 0:
            arrow_surf = font.render(t("more_above"), False, (140, 140, 140))
            surface.blit(arrow_surf, (panel_x + panel_w - ui(40), msg_area_y - ui(2)))
