# ============================================================
#  商店系统：买卖逻辑
# ============================================================
from inventory import ITEMS
from i18n import t, tf, get_item_name


class ShopManager:
    """管理所有商店"""

    def __init__(self):
        self.shops = {}  # shop_id → shop data

    def register(self, shop_id, item_ids):
        """注册商店
        item_ids: list of item_id strings
        """
        self.shops[shop_id] = {
            "items": item_ids,
        }

    def get_shop(self, shop_id):
        return self.shops.get(shop_id)

    def get_shop_items(self, shop_id):
        """获取商店物品列表 [{id, name, price, ...}]"""
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
        """购买物品，返回是否成功"""
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
        """卖出物品（半价），返回是否成功"""
        item_data = ITEMS.get(item_id)
        if not item_data:
            return False, t("item_not_found")

        if not player.inventory.has_item(item_id):
            return False, t("dont_have_item")

        sell_price = item_data.get("price", 0) // 2
        player.inventory.remove_item(item_id)
        player.inventory.gold += sell_price
        return True, tf("sold_for", price=sell_price)
