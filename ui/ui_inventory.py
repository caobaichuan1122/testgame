# ============================================================
#  Inventory / Equipment UI — modern RPG layout
#  Left column : bag (rarity-colored items, scrollable)
#  Right column top    : 6 equipment slots
#  Right column middle : selected-item detail + stat comparison
#  Right column bottom : active set bonuses
# ============================================================
import pygame
from core.settings import (
    INV_WIDTH, INV_HEIGHT,
    COLOR_UI, COLOR_ACCENT, COLOR_BLACK, COLOR_GOLD,
)
from systems.inventory import ITEMS, EQUIP_SLOTS, RARITY_COLORS, ITEM_SETS
from systems.i18n import t, tf, get_item_name, get_item_desc
from core.utils import draw_text, get_font, ui, FONT_UI_SM, FONT_UI_MD

# Slot label i18n keys in display order
_SLOT_KEYS = {
    "weapon":  "slot_weapon",
    "helmet":  "slot_helmet",
    "armor":   "slot_armor",
    "boots":   "slot_boots",
    "ring":    "slot_ring",
    "amulet":  "slot_amulet",
}

# Short stat display names
_STAT_KEYS = [
    ("atk",  "stat_atk"),
    ("def_", "stat_def"),
    ("str",  "stat_str"),
    ("dex",  "stat_dex"),
    ("int",  "stat_int"),
    ("crit", "stat_crit"),
]


def _rarity_color(item_id):
    if not item_id:
        return (130, 130, 130)
    r = ITEMS.get(item_id, {}).get("rarity", "common")
    return RARITY_COLORS.get(r, (170, 170, 170))


def _item_color(item_id, selected=False):
    base = _rarity_color(item_id)
    if not selected:
        # Dim unselected items slightly
        return tuple(max(0, c - 40) for c in base)
    return base


class InventoryUI:
    def __init__(self):
        self.selected   = 0   # selected bag-item index
        self.active     = False
        self.mode       = "items"  # "items" or "stats"

    def open(self):
        self.active   = True
        self.selected = 0
        self.mode     = "items"

    def close(self):
        self.active = False

    # ------------------------------------------------------------------
    #  Main draw
    # ------------------------------------------------------------------
    def draw(self, surface, player):
        if not self.active or not player:
            return

        font    = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)

        sw, sh = surface.get_size()

        # Semi-transparent overlay
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # Panel
        pw  = ui(INV_WIDTH)
        ph  = ui(INV_HEIGHT)
        px  = (sw - pw) // 2
        py  = (sh - ph) // 2

        pygame.draw.rect(surface, (22, 20, 32), (px, py, pw, ph), border_radius=6)
        pygame.draw.rect(surface, (70, 55, 95), (px, py, pw, ph), 1, border_radius=6)

        # Title row
        title = t("inventory") if self.mode == "items" else t("stats")
        draw_text(surface, title, px + pw // 2, py + ui(3),
                  font, COLOR_ACCENT, center=True)
        tab_hint = "[Tab] " + (t("stats") if self.mode == "items" else t("inventory"))
        tab_w = font_sm.size(tab_hint)[0]
        draw_text(surface, tab_hint, px + pw - ui(2) - tab_w, py + ui(3), font_sm, (90, 90, 90))

        # Thin divider under title
        pygame.draw.line(surface, (55, 45, 70),
                         (px + ui(2), py + ui(10)),
                         (px + pw - ui(2), py + ui(10)))

        if self.mode == "items":
            self._draw_items(surface, px, py, pw, ph, player, font, font_sm)
        else:
            self._draw_stats(surface, px, py, pw, ph, player, font, font_sm)

    # ------------------------------------------------------------------
    #  Items mode
    # ------------------------------------------------------------------
    def _draw_items(self, surface, px, py, pw, ph, player, font, font_sm):
        inv = player.inventory

        left_w = pw * 43 // 100          # ~43% for bag
        div_x  = px + left_w
        right_x = div_x + ui(3)

        # Vertical divider
        pygame.draw.line(surface, (50, 42, 65),
                         (div_x, py + ui(11)),
                         (div_x, py + ph - ui(2)))

        # ── Left: bag ──────────────────────────────────────────────
        ix   = px + ui(3)
        iy   = py + ui(12)

        # Gold
        gold_text = tf("gold_label", gold=inv.gold)
        draw_text(surface, gold_text, ix, iy, font_sm, COLOR_GOLD)
        iy += ui(8)

        if not inv.items:
            draw_text(surface, t("empty"), ix, iy, font_sm, (80, 80, 80))
        else:
            max_visible = 16
            start = max(0, self.selected - max_visible + 1)
            line_h = ui(8)
            for idx in range(start, min(len(inv.items), start + max_visible)):
                slot     = inv.items[idx]
                item_id  = slot["id"]
                name     = get_item_name(item_id)
                count    = f" x{slot['count']}" if slot.get("count", 1) > 1 else ""
                selected = (idx == self.selected)

                item_y = iy + (idx - start) * line_h

                if selected:
                    hl = pygame.Rect(px + ui(1), item_y - ui(1), left_w - ui(2), line_h - ui(1))
                    pygame.draw.rect(surface, (40, 35, 55), hl, border_radius=3)

                color  = _item_color(item_id, selected)
                prefix = "► " if selected else "  "
                num    = f"{idx+1:02d} "
                draw_text(surface, prefix + num + name + count,
                          ix, item_y, font_sm, color)

        # Key hint at bottom-left
        draw_text(surface, t("use_equip_hint"),
                  ix, py + ph - ui(6), font_sm, (65, 65, 65))

        # ── Right: equipped slots ──────────────────────────────────
        ry    = py + ui(12)
        rw    = pw - left_w - ui(3)
        line_h_eq = ui(9)

        draw_text(surface, t("equipped_label"),
                  right_x, ry, font_sm, (130, 110, 160))
        ry += ui(8)

        for slot_name in EQUIP_SLOTS:
            item_id = inv.equipped.get(slot_name)
            label   = t(_SLOT_KEYS[slot_name])
            if item_id:
                name  = get_item_name(item_id)
                color = _rarity_color(item_id)
            else:
                name  = t("slot_none")
                color = (60, 60, 60)

            # Label in muted color, item name in rarity color
            label_surf = font_sm.render(label + ": ", False, (100, 90, 120))
            surface.blit(label_surf, (right_x, ry))
            draw_text(surface, name,
                      right_x + label_surf.get_width(), ry, font_sm, color)
            ry += line_h_eq

        # Divider between slots and detail
        ry += ui(2)
        pygame.draw.line(surface, (50, 42, 65),
                         (div_x + ui(3), ry),
                         (px + pw - ui(2), ry))
        ry += ui(3)

        # ── Right: selected item detail ────────────────────────────
        if inv.items and 0 <= self.selected < len(inv.items):
            self._draw_item_detail(surface, right_x, ry, rw,
                                   py + ph - ui(12),
                                   inv, inv.items[self.selected]["id"],
                                   font_sm)

        # ── Right: set bonuses ─────────────────────────────────────
        active_sets = inv.get_active_sets()
        if active_sets:
            set_y = py + ph - ui(10)
            pygame.draw.line(surface, (50, 42, 65),
                             (div_x + ui(3), set_y - ui(2)),
                             (px + pw - ui(2), set_y - ui(2)))
            for key, count, total, is_active in active_sets:
                set_name = t(ITEM_SETS[key]["name_key"])
                badge    = (" [" + t("set_active") + "]") if is_active else f" ({count}/{total})"
                color    = (255, 200, 80) if is_active else (140, 120, 80)
                draw_text(surface, set_name + badge, right_x, set_y, font_sm, color)
                set_y += ui(7)

    def _draw_item_detail(self, surface, x, y, max_w, max_y, inv, item_id, font_sm):
        """Draw selected item's detail panel (name, rarity, stats, comparison, desc)."""
        item_data = ITEMS.get(item_id)
        if not item_data:
            return

        # Name in rarity color
        rarity = item_data.get("rarity", "common")
        rc     = RARITY_COLORS.get(rarity, (170, 170, 170))
        name   = get_item_name(item_id)
        draw_text(surface, name, x, y, font_sm, rc)
        y += ui(7)

        if y >= max_y:
            return

        # Rarity badge
        rarity_label = t(f"rarity_{rarity}")
        draw_text(surface, rarity_label, x, y, font_sm, tuple(c // 2 + 40 for c in rc))
        y += ui(7)

        # Stats + comparison (for equipment)
        item_stats = item_data.get("stats", {})
        comparison  = inv.get_stat_comparison(item_id) if item_data.get("slot") else None

        if item_stats:
            for stat_key, i18n_key in _STAT_KEYS:
                val = item_stats.get(stat_key, 0)
                if val == 0:
                    continue
                if y >= max_y:
                    break
                label = t(i18n_key)
                if comparison:
                    delta = comparison.get(stat_key, 0)
                    if delta > 0:
                        delta_str = f" (+{delta})"
                        dc = (100, 220, 100)
                    elif delta < 0:
                        delta_str = f" ({delta})"
                        dc = (220, 80, 80)
                    else:
                        delta_str = ""
                        dc = None
                    draw_text(surface, f"{label}: {val}", x, y, font_sm, (180, 180, 180))
                    if delta_str and dc:
                        stat_w = font_sm.size(f"{label}: {val}")[0]
                        draw_text(surface, delta_str, x + stat_w, y, font_sm, dc)
                else:
                    # Consumable: show heal/mp values
                    draw_text(surface, f"{label}: {val}", x, y, font_sm, (180, 180, 180))
                y += ui(7)

        # Heal/MP for consumables
        if item_data.get("type") == "consumable":
            if "heal" in item_data and y < max_y:
                draw_text(surface, f"HP +{item_data['heal']}", x, y, font_sm, (80, 220, 80))
                y += ui(7)
            if "restore_mp" in item_data and y < max_y:
                draw_text(surface, f"MP +{item_data['restore_mp']}", x, y, font_sm, (100, 140, 255))
                y += ui(7)

        # Description
        if y < max_y:
            desc = get_item_desc(item_id)
            # Word-wrap in available width
            words = desc.split()
            line  = ""
            for word in words:
                test = (line + " " + word).strip()
                if font_sm.size(test)[0] > max_w - ui(2):
                    if line:
                        draw_text(surface, line, x, y, font_sm, (90, 90, 90))
                        y += ui(6)
                        if y >= max_y:
                            break
                    line = word
                else:
                    line = test
            if line and y < max_y:
                draw_text(surface, line, x, y, font_sm, (90, 90, 90))

    # ------------------------------------------------------------------
    #  Stats mode
    # ------------------------------------------------------------------
    def _draw_stats(self, surface, px, py, pw, ph, player, font, font_sm):
        stats  = player.stats
        inv    = player.inventory
        total  = inv.get_total_stats()

        sy     = py + ui(13)
        col_w  = pw // 2
        line_h = ui(9)

        # Base stats
        base_lines = [
            tf("level_label", level=stats.level),
            tf("xp_label",    xp=stats.xp, needed=stats.xp_needed()),
            tf("hp_label",    hp=stats.hp, max_hp=stats.max_hp),
            tf("mp_label",    mp=stats.mp, max_mp=stats.max_mp),
        ]
        for i, line in enumerate(base_lines):
            draw_text(surface, line, px + ui(10), sy + i * line_h, font_sm, COLOR_UI)

        sy2 = sy
        # Equipment stats panel (right column)
        eq_x = px + col_w + ui(5)

        draw_text(surface, t("equipped_label"), eq_x, sy2, font_sm, (130, 110, 160))
        sy2 += ui(8)

        for stat_key, i18n_key in _STAT_KEYS:
            base_val  = getattr(stats, stat_key, 0)
            eq_bonus  = total.get(stat_key, 0)
            if base_val == 0 and eq_bonus == 0:
                continue
            label = t(i18n_key)
            line  = f"{label}: {base_val}"
            if eq_bonus:
                line += f" +{eq_bonus}"
            draw_text(surface, line, eq_x, sy2, font_sm,
                      COLOR_ACCENT if eq_bonus else (190, 190, 190))
            sy2 += ui(8)

        # Free points
        if stats.free_points > 0:
            fy = py + ph - ui(22)
            draw_text(surface, tf("free_points", pts=stats.free_points),
                      px + ui(10), fy, font_sm, COLOR_ACCENT)
            draw_text(surface, t("assign_points_hint"),
                      px + ui(10), fy + ui(7), font_sm, (100, 100, 100))

        # Active sets
        active_sets = inv.get_active_sets()
        if active_sets:
            ay = py + ph - ui(10)
            for key, count, total_pieces, is_active in active_sets:
                set_name = t(ITEM_SETS[key]["name_key"])
                badge    = f" {count}/{total_pieces}" + (" ✓" if is_active else "")
                color    = (255, 200, 80) if is_active else (130, 110, 80)
                draw_text(surface, set_name + badge, px + ui(10), ay, font_sm, color)
                ay += ui(7)

        draw_text(surface, t("menu_nav_hint"),
                  px + pw // 2, py + ph - ui(4), font_sm, (65, 65, 65), center=True)

    # ------------------------------------------------------------------
    #  Input handling
    # ------------------------------------------------------------------
    def handle_mouse(self, pos, player):
        if not self.active or not player:
            return

        sw, sh = pygame.display.get_surface().get_size()
        pw = ui(INV_WIDTH)
        ph = ui(INV_HEIGHT)
        px = (sw - pw) // 2
        py = (sh - ph) // 2

        # Click outside → close
        if not (px <= pos[0] <= px + pw and py <= pos[1] <= py + ph):
            self.close()
            return

        inv = player.inventory
        if self.mode == "items" and inv.items:
            left_w = pw * 43 // 100
            ix     = px + ui(3)
            iy     = py + ui(12) + ui(8)
            line_h = ui(8)
            start  = max(0, self.selected - 15)
            for idx in range(start, min(len(inv.items), start + 16)):
                item_y = iy + (idx - start) * line_h
                if (px <= pos[0] <= px + left_w and
                        item_y <= pos[1] <= item_y + line_h):
                    if self.selected == idx:
                        self._use_or_equip(inv, idx, player)
                    else:
                        self.selected = idx
                    return

    def handle_key(self, key, player):
        if not self.active:
            return
        if key in (pygame.K_i, pygame.K_ESCAPE):
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

        if key in (pygame.K_UP, pygame.K_w):
            self.selected = max(0, self.selected - 1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.selected = min(len(inv.items) - 1, self.selected + 1)
        elif key in (pygame.K_j, pygame.K_RETURN, pygame.K_KP_ENTER):
            if 0 <= self.selected < len(inv.items):
                self._use_or_equip(inv, self.selected, player)
                self.selected = min(self.selected, max(0, len(inv.items) - 1))
        elif key == pygame.K_k:
            if 0 <= self.selected < len(inv.items):
                inv.remove_item(inv.items[self.selected]["id"])
                self.selected = min(self.selected, max(0, len(inv.items) - 1))

    def _use_or_equip(self, inv, idx, player):
        slot      = inv.items[idx]
        item_data = ITEMS.get(slot["id"], {})
        if item_data.get("type") == "consumable":
            inv.use_item(slot["id"], player.stats)
        elif item_data.get("slot") in EQUIP_SLOTS:
            inv.equip(slot["id"])
