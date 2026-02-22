# ============================================================
#  背包系统 + 装备槽 + 物品数据库
# ============================================================


# --- 物品数据库 ---
ITEMS = {
    # 武器
    "sting": {
        "name": "Sting", "type": "weapon", "subtype": "melee",
        "bonus": 2, "price": 30,
        "desc": "An ancient Elven blade that glows blue near Orcs.",
        "color": (180, 140, 80),
    },
    "anduril": {
        "name": "Anduril", "type": "weapon", "subtype": "melee",
        "bonus": 5, "price": 80,
        "desc": "Flame of the West, reforged from the shards of Narsil.",
        "color": (180, 180, 190),
    },
    "bow_galadhrim": {
        "name": "Bow of Galadhrim", "type": "weapon", "subtype": "ranged",
        "bonus": 4, "price": 70,
        "desc": "A graceful bow gifted by the Elves of Lothlorien.",
        "color": (160, 120, 60),
    },
    "wizards_staff": {
        "name": "Wizard's Staff", "type": "weapon", "subtype": "magic",
        "bonus": 6, "price": 100,
        "desc": "A staff imbued with the power of the Istari.",
        "color": (130, 80, 255),
    },
    # 护甲
    "ranger_cloak": {
        "name": "Ranger Cloak", "type": "armor",
        "bonus": 2, "price": 50,
        "desc": "A weathered cloak worn by the Dunedain Rangers.",
        "color": (140, 100, 60),
    },
    "mithril_coat": {
        "name": "Mithril Coat", "type": "armor",
        "bonus": 5, "price": 120,
        "desc": "A coat of mithril rings, light as a feather.",
        "color": (160, 160, 170),
    },
    # 饰品
    "ring_barahir": {
        "name": "Ring of Barahir", "type": "accessory",
        "bonus": 3, "stat": "str", "price": 150,
        "desc": "An ancient ring, heirloom of the House of Isildur.",
        "color": (220, 180, 50),
    },
    "elven_brooch": {
        "name": "Elven Brooch", "type": "accessory",
        "bonus": 3, "stat": "dex", "price": 150,
        "desc": "A leaf-shaped brooch of Lorien, granting swiftness.",
        "color": (50, 200, 150),
    },
    # 任务材料
    "orc_blood": {
        "name": "Orc Blood", "type": "material",
        "price": 5, "stackable": True,
        "desc": "Dark, foul blood of the enemy.",
        "color": (100, 220, 100),
    },
    "morgul_shard": {
        "name": "Morgul Shard", "type": "material",
        "price": 8, "stackable": True,
        "desc": "A cursed fragment from a Morgul blade.",
        "color": (210, 200, 180),
    },
    # 消耗品
    "miruvor": {
        "name": "Miruvor", "type": "consumable",
        "heal": 30, "price": 20, "stackable": True,
        "desc": "The cordial of Imladris, restoring the weary.",
        "color": (220, 50, 50),
    },
    "ent_draught": {
        "name": "Ent-draught", "type": "consumable",
        "restore_mp": 20, "price": 25, "stackable": True,
        "desc": "A draught from the Ents of Fangorn, restoring spirit.",
        "color": (50, 100, 220),
    },
}


class Inventory:
    """背包系统：20格，物品堆叠，装备槽"""

    MAX_SLOTS = 20

    def __init__(self):
        # 背包：列表 of {"id": str, "count": int}
        self.items = []
        # 装备槽
        self.equipped = {
            "weapon": None,   # 物品id
            "armor": None,
            "accessory": None,
        }
        self.gold = 0

    def add_item(self, item_id, count=1):
        """添加物品到背包，返回是否成功"""
        item_data = ITEMS.get(item_id)
        if not item_data:
            return False

        # 可堆叠的物品尝试合并
        if item_data.get("stackable"):
            for slot in self.items:
                if slot["id"] == item_id:
                    slot["count"] += count
                    return True

        if len(self.items) >= self.MAX_SLOTS:
            return False

        self.items.append({"id": item_id, "count": count})
        return True

    def remove_item(self, item_id, count=1):
        """移除物品，返回是否成功"""
        for i, slot in enumerate(self.items):
            if slot["id"] == item_id:
                if slot["count"] >= count:
                    slot["count"] -= count
                    if slot["count"] <= 0:
                        self.items.pop(i)
                    return True
        return False

    def has_item(self, item_id, count=1):
        for slot in self.items:
            if slot["id"] == item_id and slot["count"] >= count:
                return True
        return False

    def count_item(self, item_id):
        for slot in self.items:
            if slot["id"] == item_id:
                return slot["count"]
        return 0

    def equip(self, item_id):
        """装备物品（从背包移到装备槽）"""
        item_data = ITEMS.get(item_id)
        if not item_data:
            return False

        slot_name = None
        if item_data["type"] == "weapon":
            slot_name = "weapon"
        elif item_data["type"] == "armor":
            slot_name = "armor"
        elif item_data["type"] == "accessory":
            slot_name = "accessory"
        else:
            return False

        if not self.has_item(item_id):
            return False

        # 卸下当前装备
        old = self.equipped[slot_name]
        if old:
            self.add_item(old)

        self.remove_item(item_id)
        self.equipped[slot_name] = item_id
        return True

    def unequip(self, slot_name):
        """卸下装备（放回背包）"""
        item_id = self.equipped.get(slot_name)
        if not item_id:
            return False
        if len(self.items) >= self.MAX_SLOTS:
            return False
        self.equipped[slot_name] = None
        self.add_item(item_id)
        return True

    def use_item(self, item_id, stats):
        """使用消耗品"""
        item_data = ITEMS.get(item_id)
        if not item_data or item_data["type"] != "consumable":
            return False
        if not self.has_item(item_id):
            return False

        self.remove_item(item_id)

        if "heal" in item_data:
            stats.heal(item_data["heal"])
        if "restore_mp" in item_data:
            stats.restore_mp(item_data["restore_mp"])
        return True

    def get_equipped_weapon(self):
        """获取已装备武器的数据"""
        wid = self.equipped["weapon"]
        if wid:
            return ITEMS.get(wid)
        return None

    def get_equipped_armor(self):
        aid = self.equipped["armor"]
        if aid:
            return ITEMS.get(aid)
        return None

    def get_total_defense(self):
        """计算装备提供的总防御加成"""
        total = 0
        armor = self.get_equipped_armor()
        if armor:
            total += armor.get("bonus", 0)
        return total

    def get_stat_bonus(self, stat_name):
        """获取装备提供的属性加成"""
        total = 0
        acc_id = self.equipped["accessory"]
        if acc_id:
            acc_data = ITEMS.get(acc_id)
            if acc_data and acc_data.get("stat") == stat_name:
                total += acc_data.get("bonus", 0)
        return total
