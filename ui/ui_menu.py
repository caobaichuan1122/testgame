# ============================================================
#  Main menu / pause / game over / settings screen
# ============================================================
import pygame
from core.settings import (
    COLOR_UI, COLOR_ACCENT, COLOR_BG, WINDOW_TITLE,
)
from systems.i18n import t
from core.utils import draw_text, get_font, FONT_UI_SM, FONT_UI_MD, FONT_UI_LG


_MENU_ITEMS = ["menu_new_game", "menu_settings", "menu_quit"]
_PAUSE_ITEMS = ["menu_resume", "menu_settings", "menu_main_menu"]


class MenuUI:
    def __init__(self):
        self._menu_sel = 0      # highlighted main menu item
        self._pause_sel = 0     # highlighted pause menu item
        self._settings_sel = 0  # highlighted settings row

    def draw_main_menu(self, surface):
        font_big = get_font(FONT_UI_LG)
        font_md = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)

        sw, sh = surface.get_size()
        surface.fill(COLOR_BG)

        cx = sw // 2
        cy = sh // 5

        # Title
        draw_text(surface, WINDOW_TITLE, cx, cy, font_big, COLOR_UI, center=True)

        # Menu items panel
        item_h = 52
        panel_w = 340
        panel_h = len(_MENU_ITEMS) * item_h + 24
        panel_x = cx - panel_w // 2
        panel_y = cy + 72

        pygame.draw.rect(surface, (28, 26, 34),
                         (panel_x, panel_y, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(surface, (70, 60, 85),
                         (panel_x, panel_y, panel_w, panel_h), 1, border_radius=8)

        for i, key in enumerate(_MENU_ITEMS):
            selected = (i == self._menu_sel)
            item_y = panel_y + 12 + i * item_h

            if selected:
                hl = pygame.Rect(panel_x + 4, item_y - 4, panel_w - 8, item_h - 6)
                pygame.draw.rect(surface, (50, 44, 65), hl, border_radius=5)

            color = COLOR_ACCENT if selected else (200, 200, 200)
            marker = ">  " if selected else "   "
            draw_text(surface, marker + t(key), cx, item_y + 6, font_md, color, center=True)

        # Nav hint below panel
        draw_text(surface, t("menu_nav_hint"),
                  cx, panel_y + panel_h + 14, font_sm, (90, 90, 90), center=True)

        # Controls reference at bottom
        controls = [
            t("controls_move"),
            t("controls_attack"),
            t("controls_interact"),
            t("controls_quest"),
        ]
        ctrl_y = panel_y + panel_h + 60
        for i, line in enumerate(controls):
            draw_text(surface, line, cx, ctrl_y + i * 28,
                      font_sm, (90, 90, 90), center=True)

    def draw_settings(self, surface, settings_mgr):
        font_big = get_font(FONT_UI_LG)
        font_sm = get_font(FONT_UI_SM)

        sw, sh = surface.get_size()
        surface.fill(COLOR_BG)

        cx = sw // 2
        cy = sh // 4

        draw_text(surface, t("settings"), cx, cy,
                  font_big, COLOR_UI, center=True)

        # Option labels and value getters
        option_keys = [
            "settings_resolution",
            "settings_fullscreen",
            "settings_language",
            "settings_music",
        ]

        def get_value(idx):
            if idx == 0:
                w, h = settings_mgr.resolution
                return f"{w} x {h}"
            elif idx == 1:
                return t("settings_on") if settings_mgr.fullscreen else t("settings_off")
            elif idx == 2:
                return t("lang_name_zh") if settings_mgr.language == "zh" else t("lang_name_en")
            else:
                return t("settings_on") if settings_mgr.music_enabled else t("settings_off")

        row_start = cy + 100
        row_h = 58
        box_pad = 20

        # Background panel
        box_rect = pygame.Rect(
            cx - 260,
            row_start - box_pad,
            520,
            len(option_keys) * row_h + box_pad * 2,
        )
        pygame.draw.rect(surface, (28, 26, 34), box_rect, border_radius=8)
        pygame.draw.rect(surface, (70, 60, 85), box_rect, 1, border_radius=8)

        label_x = cx - 230
        arrow_x = cx + 10
        value_x = cx + 50

        for i, key in enumerate(option_keys):
            selected = (i == self._settings_sel)
            y = row_start + i * row_h

            if selected:
                hl = pygame.Rect(cx - 258, y - 10, 516, row_h - 8)
                pygame.draw.rect(surface, (48, 42, 62), hl, border_radius=5)

            color = COLOR_ACCENT if selected else (190, 190, 190)
            marker = "> " if selected else "  "

            draw_text(surface, marker + t(key), label_x, y, font_sm, color)

            if selected:
                draw_text(surface, "< ", arrow_x, y, font_sm, COLOR_ACCENT)
                draw_text(surface, get_value(i), value_x, y, font_sm, COLOR_ACCENT)
                val_surf = get_font(FONT_UI_SM).render(get_value(i), False, COLOR_ACCENT)
                draw_text(surface, " >", value_x + val_surf.get_width(), y,
                          font_sm, COLOR_ACCENT)
            else:
                draw_text(surface, get_value(i), value_x, y, font_sm, (150, 150, 150))

        # Navigation hint
        hint_y = row_start + len(option_keys) * row_h + box_pad + 20
        draw_text(surface, t("settings_nav_hint"), cx, hint_y,
                  font_sm, (90, 90, 90), center=True)

    def draw_pause(self, surface):
        font_big = get_font(FONT_UI_LG)
        font_md = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)

        sw, sh = surface.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        cx = sw // 2
        cy = sh // 5

        draw_text(surface, t("paused"), cx, cy, font_big, COLOR_UI, center=True)

        item_h = 52
        panel_w = 300
        panel_h = len(_PAUSE_ITEMS) * item_h + 24
        panel_x = cx - panel_w // 2
        panel_y = cy + 72

        pygame.draw.rect(surface, (28, 26, 34),
                         (panel_x, panel_y, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(surface, (70, 60, 85),
                         (panel_x, panel_y, panel_w, panel_h), 1, border_radius=8)

        for i, key in enumerate(_PAUSE_ITEMS):
            selected = (i == self._pause_sel)
            item_y = panel_y + 12 + i * item_h

            if selected:
                hl = pygame.Rect(panel_x + 4, item_y - 4, panel_w - 8, item_h - 6)
                pygame.draw.rect(surface, (50, 44, 65), hl, border_radius=5)

            color = COLOR_ACCENT if selected else (200, 200, 200)
            marker = ">  " if selected else "   "
            draw_text(surface, marker + t(key), cx, item_y + 6, font_md, color, center=True)

        draw_text(surface, t("menu_nav_hint"),
                  cx, panel_y + panel_h + 14, font_sm, (90, 90, 90), center=True)

    def draw_game_over(self, surface):
        font_big = get_font(FONT_UI_LG)
        font_sm = get_font(FONT_UI_SM)

        sw, sh = surface.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        cx = sw // 2
        cy = sh // 3

        draw_text(surface, t("game_over"), cx, cy,
                  font_big, COLOR_ACCENT, center=True)
        draw_text(surface, t("press_enter_restart"), cx, cy + 50,
                  font_sm, COLOR_UI, center=True)
