# ============================================================
#  主菜单/暂停/游戏结束（屏幕分辨率）
# ============================================================
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_UI, COLOR_ACCENT, COLOR_BG, WINDOW_TITLE,
)
from i18n import t
from utils import draw_text, get_font, FONT_UI_SM, FONT_UI_MD, FONT_UI_LG


class MenuUI:
    def draw_main_menu(self, surface):
        font_big = get_font(FONT_UI_LG)
        font_sm = get_font(FONT_UI_SM)

        surface.fill(COLOR_BG)

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 3

        draw_text(surface, WINDOW_TITLE, cx, cy,
                  font_big, COLOR_UI, center=True)
        draw_text(surface, t("press_enter_start"), cx, cy + 60,
                  font_sm, COLOR_ACCENT, center=True)

        controls = [
            t("controls_move"),
            t("controls_attack"),
            t("controls_interact"),
            t("controls_quest"),
        ]
        for i, line in enumerate(controls):
            draw_text(surface, line, cx, cy + 120 + i * 28,
                      font_sm, (120, 120, 120), center=True)
        draw_text(surface, t("lang_switch_hint"), cx, cy + 120 + len(controls) * 28 + 10,
                  font_sm, (120, 120, 120), center=True)

    def draw_pause(self, surface):
        font_big = get_font(FONT_UI_LG)
        font_sm = get_font(FONT_UI_SM)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 3

        draw_text(surface, t("paused"), cx, cy,
                  font_big, COLOR_UI, center=True)
        draw_text(surface, t("press_esc_resume"), cx, cy + 50,
                  font_sm, COLOR_ACCENT, center=True)
        draw_text(surface, t("lang_switch_hint"), cx, cy + 90,
                  font_sm, (120, 120, 120), center=True)

    def draw_game_over(self, surface):
        font_big = get_font(FONT_UI_LG)
        font_sm = get_font(FONT_UI_SM)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 3

        draw_text(surface, t("game_over"), cx, cy,
                  font_big, COLOR_ACCENT, center=True)
        draw_text(surface, t("press_enter_restart"), cx, cy + 50,
                  font_sm, COLOR_UI, center=True)
