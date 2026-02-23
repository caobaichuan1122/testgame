# ============================================================
#  Inventory/equipment UI (screen resolution)
# ============================================================
import pygame
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, INV_WIDTH, INV_HEIGHT,
    COLOR_UI, COLOR_ACCENT, COLOR_BLACK, COLOR_GOLD,
)
from systems.inventory import ITEMS
from systems.i18n import t, tf, get_item_name, get_item_desc
from core.utils import draw_text, draw_bar, get_font, ui, FONT_UI_SM, FONT_UI_MD


class InventoryUI:
    def __init__(self):
        self.selected = 0
        self.active = False
        self.mode = "items"

    def open(self):
        self.active = True
        self.selected = 0
        self.mode = "items"

    def close(self):
        self.active = False

    def draw(self, surface, player):
        if not self.active or not player:
            return

        font = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)

        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        # Panel
        pw, ph = ui(INV_WIDTH), ui(INV_HEIGHT)
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2
        pygame.draw.rect(surface, (30, 30, 40), (px, py, pw, ph))
        pygame.draw.rect(surface, (80, 80, 100), (px, py, pw, ph), 1)

        title = t("inventory") if self.mode == "items" else t("stats")
        draw_text(surface, title, px + pw // 2, py + ui(4),
                  font, COLOR_ACCENT, center=True)
        draw_text(surface, t("tab_switch"), px + pw - ui(65), py + ui(4),
                  font_sm, (120, 120, 120))

        if self.mode == "items":
            self._draw_items(surface, px, py, pw, ph, player, font, font_sm)
        else:
            self._draw_stats(surface, px, py, pw, ph, player, font, font_sm)

    def _draw_items(self, surface, px, py, pw, ph, player, font, font_sm):
        inv = player.inventory
        ix = px + ui(4)
        iy = py + ui(18)
        max_visible = 10
        line_h = ui(4.5)

        draw_text(surface, tf("gold_label", gold=inv.gold), ix, iy, font_sm, COLOR_GOLD)
        iy += ui(5)

        if not inv.items:
            draw_text(surface, t("empty"), ix, iy, font_sm, (100, 100, 100))
        else:
            start = max(0, self.selected - max_visible + 1)
            for i in range(start, min(len(inv.items), start + max_visible)):
                slot = inv.items[i]
                name = get_item_name(slot["id"])
                count = f" x{slot['count']}" if slot["count"] > 1 else ""
                color = COLOR_ACCENT if i == self.selected else COLOR_UI
                prefix = "> " if i == self.selected else "  "
                draw_text(surface, f"{prefix}{name}{count}",
                          ix, iy + (i - start) * line_h, font_sm, color)

        # Right side: equipment slots
        ex = px + pw // 2 + ui(10)
        ey = py + ui(18)
        draw_text(surface, t("equipped_label"), ex, ey, font_sm, COLOR_UI)
        ey += ui(5)
        slot_keys = {"weapon": "slot_weapon", "armor": "slot_armor", "accessory": "slot_accessory"}
        for slot_name in ("weapon", "armor", "accessory"):
            item_id = inv.equipped[slot_name]
            name = get_item_name(item_id) if item_id else t("slot_none")
            draw_text(surface, f"{t(slot_keys[slot_name])}: {name}", ex, ey, font_sm, COLOR_UI)
            ey += line_h

        # Selected item description
        if inv.items and 0 <= self.selected < len(inv.items):
            slot = inv.items[self.selected]
            desc = get_item_desc(slot["id"])
            dy = py + ph - ui(10)
            draw_text(surface, desc, px + ui(4), dy, font_sm, (180, 180, 180))
            draw_text(surface, t("use_equip_hint"),
                      px + ui(4), dy + ui(4), font_sm, (120, 120, 120))

    def _draw_stats(self, surface, px, py, pw, ph, player, font, font_sm):
        stats = player.stats
        sy = py + ui(18)
        line_h = ui(5)
        lines = [
            tf("level_label", level=stats.level),
            tf("xp_label", xp=stats.xp, needed=stats.xp_needed()),
            tf("hp_label", hp=stats.hp, max_hp=stats.max_hp),
            tf("mp_label", mp=stats.mp, max_mp=stats.max_mp),
            "",
            tf("str_label", val=stats.str),
            tf("dex_label", val=stats.dex),
            tf("int_label", val=stats.int),
            tf("def_label", val=stats.def_),
        ]
        for i, line in enumerate(lines):
            draw_text(surface, line, px + ui(10), sy + i * line_h, font_sm, COLOR_UI)

        if stats.free_points > 0:
            fy = sy + len(lines) * line_h + ui(3)
            draw_text(surface, tf("free_points", pts=stats.free_points),
                      px + ui(10), fy, font_sm, COLOR_ACCENT)
            draw_text(surface, t("assign_points_hint"),
                      px + ui(10), fy + ui(5), font_sm, (120, 120, 120))

    def handle_key(self, key, player):
        if not self.active:
            return
        if key == pygame.K_i or key == pygame.K_ESCAPE:
            self.close()
            return
        if key == pygame.K_TAB:
            self.mode = "stats" if self.mode == "items" else "items"
            self.selected = 0
            return
        if self.mode == "stats":
            stats = player.stats
            if stats.free_points > 0:
                if key == pygame.K_1:
                    stats.assign_point("str")
                elif key == pygame.K_2:
                    stats.assign_point("dex")
                elif key == pygame.K_3:
                    stats.assign_point("int")
                elif key == pygame.K_4:
                    stats.assign_point("def")
            return
        inv = player.inventory
        if not inv.items:
            return
        if key == pygame.K_UP or key == pygame.K_w:
            self.selected = max(0, self.selected - 1)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.selected = min(len(inv.items) - 1, self.selected + 1)
        elif key == pygame.K_j or key == pygame.K_RETURN:
            if 0 <= self.selected < len(inv.items):
                slot = inv.items[self.selected]
                item_data = ITEMS.get(slot["id"], {})
                if item_data.get("type") == "consumable":
                    inv.use_item(slot["id"], player.stats)
                elif item_data.get("type") in ("weapon", "armor", "accessory"):
                    inv.equip(slot["id"])
                self.selected = min(self.selected, len(inv.items) - 1)
        elif key == pygame.K_k:
            if 0 <= self.selected < len(inv.items):
                slot = inv.items[self.selected]
                inv.remove_item(slot["id"])
                self.selected = min(self.selected, max(0, len(inv.items) - 1))
