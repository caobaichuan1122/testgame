# ============================================================
#  Dialogue box UI (screen resolution)
# ============================================================
import pygame
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, DIALOGUE_HEIGHT, COLOR_UI, COLOR_ACCENT
from core.utils import draw_text, get_font, ui, FONT_UI_SM, FONT_UI_MD


class DialogueUI:
    def __init__(self):
        self.selected = 0

    def draw(self, surface, dialogue_mgr):
        if not dialogue_mgr.is_active:
            return

        font = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)

        panel_h = ui(DIALOGUE_HEIGHT)
        panel_y = SCREEN_HEIGHT - panel_h

        # Semi-transparent background
        panel = pygame.Surface((SCREEN_WIDTH, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        surface.blit(panel, (0, panel_y))
        pygame.draw.rect(surface, (80, 80, 100),
                         (0, panel_y, SCREEN_WIDTH, panel_h), 1)

        # Speaker name
        if dialogue_mgr.speaker_name:
            draw_text(surface, dialogue_mgr.speaker_name,
                      ui(6), panel_y + ui(3), font, COLOR_ACCENT)

        # Dialogue text (auto word-wrap)
        text = dialogue_mgr.get_current_text()
        y = panel_y + ui(14)
        words = text.split(" ")
        line = ""
        for word in words:
            test = line + (" " if line else "") + word
            if len(test) > 50:
                draw_text(surface, line, ui(6), y, font_sm, COLOR_UI)
                y += ui(4)
                line = word
            else:
                line = test
        if line:
            draw_text(surface, line, ui(6), y, font_sm, COLOR_UI)

        # Options (only shown after typewriter finishes)
        if dialogue_mgr.typewriter_done:
            options = dialogue_mgr.get_options()
            opt_y = panel_y + panel_h - ui(6) - len(options) * ui(5)
            for i, opt in enumerate(options):
                color = COLOR_ACCENT if i == self.selected else COLOR_UI
                prefix = "> " if i == self.selected else "  "
                draw_text(surface, prefix + opt["label"],
                          ui(10), opt_y + i * ui(5), font_sm, color)
        else:
            # Show "press key to continue" hint
            draw_text(surface, "...", ui(6),
                      panel_y + panel_h - ui(8), font_sm, (150, 150, 150))

    def handle_key(self, key, dialogue_mgr, game):
        if not dialogue_mgr.is_active:
            return False

        # While typewriter is active, confirm key skips it
        if not dialogue_mgr.typewriter_done:
            if key in (pygame.K_RETURN, pygame.K_j, pygame.K_e, pygame.K_SPACE):
                dialogue_mgr.skip_typewriter()
            return False

        options = dialogue_mgr.get_options()
        if key == pygame.K_UP or key == pygame.K_w:
            self.selected = max(0, self.selected - 1)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.selected = min(len(options) - 1, self.selected + 1)
        elif key == pygame.K_RETURN or key == pygame.K_j or key == pygame.K_e:
            ended = dialogue_mgr.select_option(self.selected, game)
            self.selected = 0
            return ended
        return False
