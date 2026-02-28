# ============================================================
#  HUD: HP/MP bars, level, gold, combat mode, quest hints (screen resolution)
# ============================================================
import pygame
from core.settings import (
    COLOR_HP, COLOR_MP, COLOR_GOLD, COLOR_UI, COLOR_ACCENT,
)
from systems.i18n import tf
from core.utils import draw_bar, draw_text, get_font, ui, FONT_UI_SM, FONT_UI_MD


class HUD:
    def draw(self, surface, player, quest_hint=""):
        if not player:
            return

        sw, sh = surface.get_size()
        font = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)
        stats = player.stats

        # HP bar
        draw_bar(surface, ui(4), ui(3), ui(50), ui(6),
                 stats.hp / stats.max_hp, COLOR_HP)
        draw_text(surface, f"HP {stats.hp}/{stats.max_hp}",
                  ui(56), ui(3), font_sm, COLOR_UI)

        # MP bar
        draw_bar(surface, ui(4), ui(11), ui(50), ui(6),
                 stats.mp / stats.max_mp, COLOR_MP)
        draw_text(surface, f"MP {stats.mp}/{stats.max_mp}",
                  ui(56), ui(11), font_sm, COLOR_UI)

        # Level
        draw_text(surface, f"Lv{stats.level}", ui(120), ui(3), font, COLOR_UI)

        # XP bar
        xp_ratio = stats.xp / stats.xp_needed() if stats.xp_needed() > 0 else 0
        draw_bar(surface, ui(120), ui(13), ui(40), ui(4), xp_ratio, (50, 200, 100))

        # Gold
        draw_text(surface, f"G:{player.inventory.gold}",
                  ui(170), ui(3), font, COLOR_GOLD)

        # Free attribute points hint
        if stats.free_points > 0:
            draw_text(surface, f"+{stats.free_points}pts",
                      ui(170), ui(13), font_sm, COLOR_ACCENT)

        # --- Bottom ---
        bottom_y = sh - ui(12)

        # Quest hint (bottom-left)
        if quest_hint:
            draw_text(surface, quest_hint, ui(4), bottom_y, font_sm, COLOR_UI)

        # Interaction hint
        if player.interact_target:
            hint = tf("talk_to", name=player.interact_target.name)
            tw, _ = draw_text(surface, hint, -9999, 0, font_sm)
            draw_text(surface, hint,
                      sw // 2 - tw // 2,
                      sh - ui(24),
                      font_sm, COLOR_ACCENT)

    def draw_zone_banner(self, surface, banner_name, banner_diff, timer, max_timer=240):
        """Draw a centered zone-entry banner with fade in/out."""
        if timer <= 0 or not banner_name:
            return
        sw, sh = surface.get_size()
        # Fade: in for first 30 frames, out for last 60 frames
        if timer > max_timer - 30:
            alpha = int(255 * (max_timer - timer) / 30)
        elif timer < 60:
            alpha = int(255 * timer / 60)
        else:
            alpha = 255
        alpha = max(0, min(255, alpha))

        font_lg = get_font(ui(9))
        font_sm_local = get_font(FONT_UI_SM)

        # Measure text
        name_surf = font_lg.render(banner_name, False, (255, 240, 200))
        diff_surf = font_sm_local.render(banner_diff, False, (220, 180, 80))

        banner_w = max(name_surf.get_width(), diff_surf.get_width()) + ui(20)
        banner_h = name_surf.get_height() + diff_surf.get_height() + ui(10)
        bx = sw // 2 - banner_w // 2
        by = sh // 5

        # Semi-transparent background
        bg = pygame.Surface((banner_w, banner_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, int(alpha * 0.75)))
        pygame.draw.rect(bg, (180, 150, 60, alpha // 2), (0, 0, banner_w, banner_h), 1)
        surface.blit(bg, (bx, by))

        # Zone name
        name_surf.set_alpha(alpha)
        surface.blit(name_surf, (sw // 2 - name_surf.get_width() // 2, by + ui(4)))
        # Difficulty
        diff_surf.set_alpha(alpha)
        surface.blit(diff_surf, (sw // 2 - diff_surf.get_width() // 2,
                                  by + ui(4) + name_surf.get_height() + ui(2)))
