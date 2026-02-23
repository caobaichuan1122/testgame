# ============================================================
#  Quest log UI (screen resolution)
# ============================================================
import pygame
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, QUEST_WIDTH, QUEST_HEIGHT,
    COLOR_UI, COLOR_ACCENT,
)
from systems.i18n import t, tf
from core.utils import draw_text, get_font, ui, FONT_UI_SM, FONT_UI_MD


class QuestUI:
    def __init__(self):
        self.active = False
        self.selected = 0

    def open(self):
        self.active = True
        self.selected = 0

    def close(self):
        self.active = False

    def draw(self, surface, quest_manager):
        if not self.active or not quest_manager:
            return

        font = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        pw, ph = ui(QUEST_WIDTH), ui(QUEST_HEIGHT)
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2
        pygame.draw.rect(surface, (30, 30, 40), (px, py, pw, ph))
        pygame.draw.rect(surface, (80, 80, 100), (px, py, pw, ph), 1)

        draw_text(surface, t("quest_log"), px + pw // 2, py + ui(4),
                  font, COLOR_ACCENT, center=True)

        quests = quest_manager.get_all_quests()
        if not quests:
            draw_text(surface, t("no_quests"), px + ui(10), py + ui(20),
                      font_sm, (100, 100, 100))
            return

        line_h = ui(5.5)
        y = py + ui(20)
        for i, (qid, q) in enumerate(quests):
            status = q["status"]
            if status == "completed":
                tag, color = t("quest_done"), (80, 180, 80)
            elif status == "failed":
                tag, color = t("quest_failed"), (180, 80, 80)
            elif status == "completable":
                tag, color = t("quest_ready"), COLOR_ACCENT
            elif status == "active":
                tag = f"[{q['progress']}/{q['required']}]"
                color = COLOR_UI
            else:
                tag, color = t("quest_new"), (150, 150, 100)
            sel_color = COLOR_ACCENT if i == self.selected else color
            prefix = "> " if i == self.selected else "  "
            draw_text(surface, f"{prefix}{q['name']} {tag}",
                      px + ui(4), y + i * line_h, font_sm, sel_color)

        if 0 <= self.selected < len(quests):
            qid, q = quests[self.selected]
            dy = py + ph - ui(12)
            draw_text(surface, q.get("desc", ""), px + ui(4), dy, font_sm, (180, 180, 180))
            rewards = q.get("rewards", {})
            parts = []
            if rewards.get("xp"):
                parts.append(f"{rewards['xp']}XP")
            if rewards.get("gold"):
                parts.append(f"{rewards['gold']}G")
            if parts:
                draw_text(surface, tf("reward_label", rewards=" + ".join(parts)),
                          px + ui(4), dy + ui(5), font_sm, (200, 200, 100))

    def handle_key(self, key, quest_manager):
        if not self.active:
            return
        if key == pygame.K_q or key == pygame.K_ESCAPE:
            self.close()
            return
        quests = quest_manager.get_all_quests()
        if not quests:
            return
        if key == pygame.K_UP or key == pygame.K_w:
            self.selected = max(0, self.selected - 1)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.selected = min(len(quests) - 1, self.selected + 1)
