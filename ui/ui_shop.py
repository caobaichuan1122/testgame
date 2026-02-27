# ============================================================
#  Shop UI (screen resolution)
# ============================================================
import pygame
from core.settings import (
    SHOP_WIDTH, SHOP_HEIGHT,
    COLOR_UI, COLOR_ACCENT, COLOR_GOLD,
)
from systems.inventory import ITEMS
from systems.i18n import t, tf, get_item_name
from core.utils import draw_text, get_font, ui, FONT_UI_SM, FONT_UI_MD


class ShopUI:
    def __init__(self):
        self.active = False
        self.shop_id = None
        self.selected = 0
        self.tab = "buy"

    def open(self, shop_id):
        self.active = True
        self.shop_id = shop_id
        self.selected = 0
        self.tab = "buy"

    def close(self):
        self.active = False
        self.shop_id = None

    def draw(self, surface, player, shop_manager):
        if not self.active or not player or not shop_manager:
            return

        font = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)

        sw, sh = surface.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        pw, ph = ui(SHOP_WIDTH), ui(SHOP_HEIGHT)
        px = (sw - pw) // 2
        py = (sh - ph) // 2
        pygame.draw.rect(surface, (30, 30, 40), (px, py, pw, ph))
        pygame.draw.rect(surface, (80, 80, 100), (px, py, pw, ph), 1)

        buy_c = COLOR_ACCENT if self.tab == "buy" else (100, 100, 100)
        sell_c = COLOR_ACCENT if self.tab == "sell" else (100, 100, 100)
        draw_text(surface, t("shop"), px + pw // 2, py + ui(3),
                  font, COLOR_UI, center=True)
        draw_text(surface, t("buy"), px + ui(30), py + ui(3), font_sm, buy_c)
        draw_text(surface, t("sell"), px + pw - ui(50), py + ui(3), font_sm, sell_c)
        draw_text(surface, tf("gold_label", gold=player.inventory.gold),
                  px + ui(4), py + ui(13), font_sm, COLOR_GOLD)

        line_h = ui(5)
        if self.tab == "buy":
            items = shop_manager.get_shop_items(self.shop_id)
            if not items:
                draw_text(surface, t("empty"), px + ui(10), py + ui(24), font_sm, (100, 100, 100))
            else:
                y = py + ui(24)
                for i in range(min(len(items), 8)):
                    item = items[i]
                    color = COLOR_ACCENT if i == self.selected else COLOR_UI
                    prefix = "> " if i == self.selected else "  "
                    price_c = COLOR_GOLD if player.inventory.gold >= item["price"] else (150, 60, 60)
                    draw_text(surface, f"{prefix}{get_item_name(item['id'])}",
                              px + ui(4), y + i * line_h, font_sm, color)
                    draw_text(surface, f"{item['price']}G",
                              px + pw - ui(40), y + i * line_h, font_sm, price_c)
        else:
            inv = player.inventory
            if not inv.items:
                draw_text(surface, t("nothing_to_sell"), px + ui(10), py + ui(24),
                          font_sm, (100, 100, 100))
            else:
                y = py + ui(24)
                for i in range(min(len(inv.items), 8)):
                    slot = inv.items[i]
                    item_data = ITEMS.get(slot["id"], {})
                    name = get_item_name(slot["id"])
                    sell_price = item_data.get("price", 0) // 2
                    count = f" x{slot['count']}" if slot["count"] > 1 else ""
                    color = COLOR_ACCENT if i == self.selected else COLOR_UI
                    prefix = "> " if i == self.selected else "  "
                    draw_text(surface, f"{prefix}{name}{count}",
                              px + ui(4), y + i * line_h, font_sm, color)
                    draw_text(surface, f"{sell_price}G",
                              px + pw - ui(40), y + i * line_h, font_sm, COLOR_GOLD)

        draw_text(surface, t("shop_hint"),
                  px + ui(4), py + ph - ui(5), font_sm, (120, 120, 120))

    def handle_key(self, key, player, shop_manager):
        if not self.active:
            return
        if key == pygame.K_ESCAPE:
            self.close()
            return
        if key == pygame.K_TAB:
            self.tab = "sell" if self.tab == "buy" else "buy"
            self.selected = 0
            return
        if self.tab == "buy":
            items = shop_manager.get_shop_items(self.shop_id)
            max_idx = len(items) - 1
        else:
            max_idx = len(player.inventory.items) - 1
        if max_idx < 0:
            return
        if key == pygame.K_UP or key == pygame.K_w:
            self.selected = max(0, self.selected - 1)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.selected = min(max_idx, self.selected + 1)
        elif key == pygame.K_j or key == pygame.K_RETURN:
            if self.tab == "buy":
                items = shop_manager.get_shop_items(self.shop_id)
                if 0 <= self.selected < len(items):
                    ok, msg = shop_manager.buy_item(
                        self.shop_id, items[self.selected]["id"], player)
                    player.add_message(msg)
            else:
                inv = player.inventory
                if 0 <= self.selected < len(inv.items):
                    slot = inv.items[self.selected]
                    ok, msg = shop_manager.sell_item(slot["id"], player)
                    player.add_message(msg)
                    self.selected = min(self.selected, max(0, len(inv.items) - 1))
