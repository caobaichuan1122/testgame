# ============================================================
#  Shop system: buy/sell logic
# ============================================================
from inventory import ITEMS
from i18n import t, tf, get_item_name


class ShopManager:
    """Manages all shops."""

    def __init__(self):
        self.shops = {}  # shop_id -> shop data

    def register(self, shop_id, item_ids):
        """Register a shop.
        item_ids: list of item_id strings
        """
        self.shops[shop_id] = {
            "items": item_ids,
        }

    def get_shop(self, shop_id):
        return self.shops.get(shop_id)

    def get_shop_items(self, shop_id):
        """Get shop item list [{id, name, price, ...}]."""
        shop = self.shops.get(shop_id)
        if not shop:
            return []
        result = []
        for item_id in shop["items"]:
            item_data = ITEMS.get(item_id)
            if item_data:
                result.append({"id": item_id, **item_data})
        return result

    def buy_item(self, shop_id, item_id, player):
        """Buy item; return (success, message)."""
        item_data = ITEMS.get(item_id)
        if not item_data:
            return False, t("item_not_found")

        price = item_data.get("price", 0)
        if player.inventory.gold < price:
            return False, t("not_enough_gold")

        if not player.inventory.add_item(item_id):
            return False, t("inventory_full")

        player.inventory.gold -= price
        return True, tf("bought_item", name=get_item_name(item_id))

    def sell_item(self, item_id, player):
        """Sell item at half price; return (success, message)."""
        item_data = ITEMS.get(item_id)
        if not item_data:
            return False, t("item_not_found")

        if not player.inventory.has_item(item_id):
            return False, t("dont_have_item")

        sell_price = item_data.get("price", 0) // 2
        player.inventory.remove_item(item_id)
        player.inventory.gold += sell_price
        return True, tf("sold_for", price=sell_price)
