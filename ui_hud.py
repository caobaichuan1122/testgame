# ============================================================
#  HUD：血条/蓝条/等级/金币/战斗模式/任务提示（屏幕分辨率）
# ============================================================
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_HP, COLOR_MP, COLOR_GOLD, COLOR_UI, COLOR_ACCENT,
)
from i18n import tf
from utils import draw_bar, draw_text, get_font, ui, FONT_UI_SM, FONT_UI_MD


class HUD:
    def draw(self, surface, player, quest_hint=""):
        if not player:
            return

        font = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)
        stats = player.stats

        # HP条
        draw_bar(surface, ui(4), ui(3), ui(50), ui(6),
                 stats.hp / stats.max_hp, COLOR_HP)
        draw_text(surface, f"HP {stats.hp}/{stats.max_hp}",
                  ui(56), ui(3), font_sm, COLOR_UI)

        # MP条
        draw_bar(surface, ui(4), ui(11), ui(50), ui(6),
                 stats.mp / stats.max_mp, COLOR_MP)
        draw_text(surface, f"MP {stats.mp}/{stats.max_mp}",
                  ui(56), ui(11), font_sm, COLOR_UI)

        # 等级
        draw_text(surface, f"Lv{stats.level}", ui(120), ui(3), font, COLOR_UI)

        # 经验条
        xp_ratio = stats.xp / stats.xp_needed() if stats.xp_needed() > 0 else 0
        draw_bar(surface, ui(120), ui(13), ui(40), ui(4), xp_ratio, (50, 200, 100))

        # 金币
        draw_text(surface, f"G:{player.inventory.gold}",
                  ui(170), ui(3), font, COLOR_GOLD)

        # 属性点提示
        if stats.free_points > 0:
            draw_text(surface, f"+{stats.free_points}pts",
                      ui(170), ui(13), font_sm, COLOR_ACCENT)

        # --- 底部 ---
        bottom_y = SCREEN_HEIGHT - ui(12)

        # 任务提示（左下）
        if quest_hint:
            draw_text(surface, quest_hint, ui(4), bottom_y, font_sm, COLOR_UI)

        # 交互提示
        if player.interact_target:
            hint = tf("talk_to", name=player.interact_target.name)
            tw, _ = draw_text(surface, hint, -9999, 0, font_sm)
            draw_text(surface, hint,
                      SCREEN_WIDTH // 2 - tw // 2,
                      SCREEN_HEIGHT - ui(24),
                      font_sm, COLOR_ACCENT)
