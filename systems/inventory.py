# ============================================================
#  Inventory system + 6-slot equipment + item database
# ============================================================

# ── Rarity ────────────────────────────────────────────────────────────────
RARITY_COLORS = {
    "common":    (170, 170, 170),
    "uncommon":  (80,  200, 80),
    "rare":      (80,  140, 255),
    "epic":      (200, 80,  255),
    "legendary": (255, 165, 0),
}
RARITY_ORDER = ["common", "uncommon", "rare", "epic", "legendary"]

# ── Equipment slots ────────────────────────────────────────────────────────
EQUIP_SLOTS = ["weapon", "helmet", "armor", "boots", "ring", "amulet"]

# ── Set bonuses ────────────────────────────────────────────────────────────
# bonuses: {pieces_required: {stat: value}}
ITEM_SETS = {
    "mithril": {
        "name_key": "set_mithril",
        "items": ["mithril_coat", "mithril_helm"],
        "bonuses": {2: {"def_": 8, "str": 2}},
    },
    "ranger": {
        "name_key": "set_ranger",
        "items": ["ranger_cloak", "ranger_boots"],
        "bonuses": {2: {"dex": 4, "crit": 8}},
    },
    "shadow": {
        "name_key": "set_shadow",
        "items": ["shadow_boots", "ring_of_shadow"],
        "bonuses": {2: {"dex": 6, "crit": 12}},
    },
}

# ── Item database ──────────────────────────────────────────────────────────
# stats keys: atk, def_, str, dex, int, crit
# slot: which equipment slot the item occupies
ITEMS = {
    # ─── Weapons ──────────────────────────────────────────────────────────
    "wood_sword": {
        "name": "Wooden Sword", "type": "weapon", "subtype": "melee",
        "slot": "weapon", "rarity": "common",
        "stats": {"atk": 2},
        "price": 8,
        "desc": "A crude wooden training sword.",
    },
    "orc_scimitar": {
        "name": "Orc Scimitar", "type": "weapon", "subtype": "melee",
        "slot": "weapon", "rarity": "common",
        "stats": {"atk": 3},
        "price": 15,
        "desc": "A crude curved blade looted from an Orc.",
    },
    "ranger_sword": {
        "name": "Ranger Sword", "type": "weapon", "subtype": "melee",
        "slot": "weapon", "rarity": "uncommon",
        "stats": {"atk": 5, "str": 1},
        "price": 35,
        "desc": "A dependable long sword carried by Dunedain Rangers.",
    },
    "short_bow": {
        "name": "Short Bow", "type": "weapon", "subtype": "ranged",
        "slot": "weapon", "rarity": "common",
        "stats": {"atk": 2},
        "price": 10,
        "desc": "A compact bow for hunting small game.",
    },
    "hunting_bow": {
        "name": "Hunting Bow", "type": "weapon", "subtype": "ranged",
        "slot": "weapon", "rarity": "uncommon",
        "stats": {"atk": 4, "dex": 1},
        "price": 30,
        "desc": "A balanced bow favoured by scouts.",
    },
    "wand_of_light": {
        "name": "Wand of Light", "type": "weapon", "subtype": "magic",
        "slot": "weapon", "rarity": "common",
        "stats": {"atk": 2},
        "price": 12,
        "desc": "A slender wand that flickers with pale light.",
    },
    "elven_staff": {
        "name": "Elven Staff", "type": "weapon", "subtype": "magic",
        "slot": "weapon", "rarity": "uncommon",
        "stats": {"atk": 4, "int": 1},
        "price": 40,
        "desc": "A graceful staff carved from mallorn wood.",
    },
    "sting": {
        "name": "Sting", "type": "weapon", "subtype": "melee",
        "slot": "weapon", "rarity": "rare",
        "stats": {"atk": 6, "dex": 2, "crit": 5},
        "price": 90,
        "desc": "An ancient Elven blade that glows blue near Orcs.",
    },
    "dark_blade": {
        "name": "Dark Blade", "type": "weapon", "subtype": "melee",
        "slot": "weapon", "rarity": "rare",
        "stats": {"atk": 8, "str": 3},
        "price": 110,
        "desc": "A Uruk-hai blade, heavy and brutal.",
    },
    "bow_galadhrim": {
        "name": "Bow of Galadhrim", "type": "weapon", "subtype": "ranged",
        "slot": "weapon", "rarity": "rare",
        "stats": {"atk": 8, "dex": 3},
        "price": 100,
        "desc": "A graceful bow gifted by the Elves of Lothlorien.",
    },
    "elven_longbow": {
        "name": "Elven Longbow", "type": "weapon", "subtype": "ranged",
        "slot": "weapon", "rarity": "rare",
        "stats": {"atk": 9, "dex": 4, "crit": 5},
        "price": 120,
        "desc": "A slender longbow carved from Lothlórien mallorn wood.",
    },
    "morgul_blade": {
        "name": "Morgul Blade", "type": "weapon", "subtype": "melee",
        "slot": "weapon", "rarity": "epic",
        "stats": {"atk": 11, "str": 4, "crit": 10},
        "price": 200,
        "desc": "A cursed blade from Angmar, forged in sorcery.",
    },
    "wizards_staff": {
        "name": "Wizard's Staff", "type": "weapon", "subtype": "magic",
        "slot": "weapon", "rarity": "epic",
        "stats": {"atk": 10, "int": 5},
        "price": 220,
        "desc": "A staff imbued with the power of the Istari.",
    },
    "anduril": {
        "name": "Andúril", "type": "weapon", "subtype": "melee",
        "slot": "weapon", "rarity": "legendary",
        "stats": {"atk": 14, "str": 5, "dex": 3, "crit": 8},
        "price": 500,
        "desc": "Flame of the West, reforged from the shards of Narsil.",
    },

    # ─── Helmets ───────────────────────────────────────────────────────────
    "leather_cap": {
        "name": "Leather Cap", "type": "armor", "subtype": "helmet",
        "slot": "helmet", "rarity": "common",
        "stats": {"def_": 2},
        "price": 12,
        "desc": "A simple leather cap offering minimal protection.",
    },
    "iron_helm": {
        "name": "Iron Helm", "type": "armor", "subtype": "helmet",
        "slot": "helmet", "rarity": "common",
        "stats": {"def_": 4},
        "price": 25,
        "desc": "A plain iron helmet, dented but reliable.",
    },
    "rangers_hood": {
        "name": "Ranger's Hood", "type": "armor", "subtype": "helmet",
        "slot": "helmet", "rarity": "uncommon",
        "stats": {"def_": 3, "dex": 1},
        "price": 45,
        "desc": "A dark hood that helps the wearer move unseen.",
    },
    "dwarf_cap": {
        "name": "Dwarven Cap", "type": "armor", "subtype": "helmet",
        "slot": "helmet", "rarity": "uncommon",
        "stats": {"def_": 5, "str": 1},
        "price": 55,
        "desc": "A reinforced cap forged by dwarven craftsmen.",
    },
    "mithril_helm": {
        "name": "Mithril Helm", "type": "armor", "subtype": "helmet",
        "slot": "helmet", "rarity": "rare",
        "stats": {"def_": 7, "dex": 1},
        "set": "mithril",
        "price": 160,
        "desc": "A gleaming helm of mithril, lighter than it looks.",
    },
    "elven_circlet": {
        "name": "Elven Circlet", "type": "armor", "subtype": "helmet",
        "slot": "helmet", "rarity": "rare",
        "stats": {"def_": 4, "int": 3},
        "price": 140,
        "desc": "A delicate circlet of Elven silver, adorned with star-runes.",
    },
    "crown_of_gondor": {
        "name": "Crown of Gondor", "type": "armor", "subtype": "helmet",
        "slot": "helmet", "rarity": "epic",
        "stats": {"def_": 8, "str": 3, "int": 3},
        "price": 300,
        "desc": "The winged crown of the Kings of Gondor, radiating authority.",
    },

    # ─── Armor (chest) ─────────────────────────────────────────────────────
    "wolf_pelt": {
        "name": "Wolf Pelt", "type": "armor", "subtype": "chest",
        "slot": "armor", "rarity": "common",
        "stats": {"def_": 2},
        "price": 15,
        "desc": "Rough pelt harvested from a warg, offering light protection.",
    },
    "leather_vest": {
        "name": "Leather Vest", "type": "armor", "subtype": "chest",
        "slot": "armor", "rarity": "common",
        "stats": {"def_": 3},
        "price": 20,
        "desc": "A sturdy leather vest worn by village guards.",
    },
    "chain_mail": {
        "name": "Chain Mail", "type": "armor", "subtype": "chest",
        "slot": "armor", "rarity": "uncommon",
        "stats": {"def_": 6, "str": 1},
        "price": 60,
        "desc": "Interlocked iron rings offering solid protection.",
    },
    "ranger_cloak": {
        "name": "Ranger Cloak", "type": "armor", "subtype": "chest",
        "slot": "armor", "rarity": "uncommon",
        "stats": {"def_": 4, "dex": 2},
        "set": "ranger",
        "price": 70,
        "desc": "A weathered cloak worn by the Dunedain Rangers.",
    },
    "uruk_shield": {
        "name": "Uruk Shield", "type": "armor", "subtype": "chest",
        "slot": "armor", "rarity": "rare",
        "stats": {"def_": 8, "str": 2},
        "price": 130,
        "desc": "A heavy iron shield bearing the White Hand of Saruman.",
    },
    "elven_robe": {
        "name": "Elven Robe", "type": "armor", "subtype": "chest",
        "slot": "armor", "rarity": "rare",
        "stats": {"def_": 5, "int": 3},
        "price": 150,
        "desc": "A shimmering robe woven with Elven spellwork.",
    },
    "gondor_plate": {
        "name": "Gondor Plate", "type": "armor", "subtype": "chest",
        "slot": "armor", "rarity": "epic",
        "stats": {"def_": 12, "str": 2},
        "price": 280,
        "desc": "Heavy full plate of the soldiers of Gondor.",
    },
    "mithril_coat": {
        "name": "Mithril Coat", "type": "armor", "subtype": "chest",
        "slot": "armor", "rarity": "legendary",
        "stats": {"def_": 12, "str": 2},
        "set": "mithril",
        "price": 400,
        "desc": "A coat of mithril rings, light as a feather yet strong as dragon-scale.",
    },

    # ─── Boots ─────────────────────────────────────────────────────────────
    "worn_boots": {
        "name": "Worn Boots", "type": "armor", "subtype": "boots",
        "slot": "boots", "rarity": "common",
        "stats": {"def_": 1},
        "price": 6,
        "desc": "Old boots patched many times over.",
    },
    "leather_boots": {
        "name": "Leather Boots", "type": "armor", "subtype": "boots",
        "slot": "boots", "rarity": "common",
        "stats": {"def_": 2},
        "price": 14,
        "desc": "Sturdy leather boots, good for long roads.",
    },
    "iron_boots": {
        "name": "Iron Boots", "type": "armor", "subtype": "boots",
        "slot": "boots", "rarity": "uncommon",
        "stats": {"def_": 4, "str": 1},
        "price": 40,
        "desc": "Heavy iron-shod boots, favoured by dwarves.",
    },
    "ranger_boots": {
        "name": "Ranger Boots", "type": "armor", "subtype": "boots",
        "slot": "boots", "rarity": "uncommon",
        "stats": {"def_": 3, "dex": 2},
        "set": "ranger",
        "price": 55,
        "desc": "Soft-soled boots for silent movement across the wilds.",
    },
    "swift_steps": {
        "name": "Swift Steps", "type": "armor", "subtype": "boots",
        "slot": "boots", "rarity": "rare",
        "stats": {"def_": 3, "dex": 3, "crit": 5},
        "price": 120,
        "desc": "Enchanted boots that make the wearer fleet-footed.",
    },
    "shadow_boots": {
        "name": "Shadow Boots", "type": "armor", "subtype": "boots",
        "slot": "boots", "rarity": "epic",
        "stats": {"def_": 4, "dex": 5, "crit": 8},
        "set": "shadow",
        "price": 240,
        "desc": "Boots wreathed in shadow, worn by the wraiths of Mirkwood.",
    },

    # ─── Rings ─────────────────────────────────────────────────────────────
    "copper_ring": {
        "name": "Copper Ring", "type": "accessory", "subtype": "ring",
        "slot": "ring", "rarity": "common",
        "stats": {"str": 1},
        "price": 10,
        "desc": "A plain copper band with a faint tingle of old magic.",
    },
    "silver_ring": {
        "name": "Silver Ring", "type": "accessory", "subtype": "ring",
        "slot": "ring", "rarity": "uncommon",
        "stats": {"str": 2},
        "price": 40,
        "desc": "A polished silver ring engraved with runes of strength.",
    },
    "ring_of_shadow": {
        "name": "Ring of Shadow", "type": "accessory", "subtype": "ring",
        "slot": "ring", "rarity": "rare",
        "stats": {"dex": 3, "crit": 10},
        "set": "shadow",
        "price": 180,
        "desc": "A jet-black ring that sharpens the senses and quickens the hand.",
    },
    "ring_barahir": {
        "name": "Ring of Barahir", "type": "accessory", "subtype": "ring",
        "slot": "ring", "rarity": "epic",
        "stats": {"str": 4, "def_": 3, "crit": 5},
        "price": 260,
        "desc": "An ancient ring, heirloom of the House of Isildur.",
    },
    "ring_of_power": {
        "name": "Ring of Power", "type": "accessory", "subtype": "ring",
        "slot": "ring", "rarity": "epic",
        "stats": {"str": 4, "int": 4},
        "price": 280,
        "desc": "One of the lesser Rings of Power, still potent beyond measure.",
    },
    "one_ring": {
        "name": "The One Ring", "type": "accessory", "subtype": "ring",
        "slot": "ring", "rarity": "legendary",
        "stats": {"str": 5, "dex": 5, "int": 8, "crit": 15},
        "price": 999,
        "desc": "The One Ring to rule them all. Its power is immense, but it corrupts.",
    },

    # ─── Amulets ───────────────────────────────────────────────────────────
    "stone_pendant": {
        "name": "Stone Pendant", "type": "accessory", "subtype": "amulet",
        "slot": "amulet", "rarity": "common",
        "stats": {"def_": 1},
        "price": 8,
        "desc": "A smooth river stone worn on a leather cord.",
    },
    "necklace_moria": {
        "name": "Necklace of Moria", "type": "accessory", "subtype": "amulet",
        "slot": "amulet", "rarity": "uncommon",
        "stats": {"def_": 3},
        "price": 35,
        "desc": "A dwarven chain found deep in the mines, still faintly warm.",
    },
    "elven_brooch": {
        "name": "Elven Brooch", "type": "accessory", "subtype": "amulet",
        "slot": "amulet", "rarity": "rare",
        "stats": {"dex": 4, "crit": 5},
        "price": 150,
        "desc": "A leaf-shaped brooch of Lorien, granting swiftness.",
    },
    "phial_pendant": {
        "name": "Phial Pendant", "type": "accessory", "subtype": "amulet",
        "slot": "amulet", "rarity": "rare",
        "stats": {"int": 3},
        "price": 140,
        "desc": "A tiny crystal phial sealed at the throat, pulsing with starlight.",
    },
    "evenstar": {
        "name": "Evenstar", "type": "accessory", "subtype": "amulet",
        "slot": "amulet", "rarity": "epic",
        "stats": {"int": 5, "dex": 3},
        "price": 350,
        "desc": "The Evenstar of the Elves, a jewel of unsurpassed beauty and power.",
    },

    # ─── Quest materials ───────────────────────────────────────────────────
    "orc_blood": {
        "name": "Orc Blood", "type": "material",
        "price": 5, "stackable": True,
        "desc": "Dark, foul blood of the enemy.",
    },
    "morgul_shard": {
        "name": "Morgul Shard", "type": "material",
        "price": 8, "stackable": True,
        "desc": "A cursed fragment from a Morgul blade.",
    },
    "goblin_ear": {
        "name": "Goblin Ear", "type": "material",
        "price": 3, "stackable": True,
        "desc": "A trophy from a slain goblin.",
    },
    "spider_silk": {
        "name": "Spider Silk", "type": "material",
        "price": 6, "stackable": True,
        "desc": "Unnervingly strong silk from a Shelob spawn.",
    },

    # ─── Consumables ───────────────────────────────────────────────────────
    "miruvor": {
        "name": "Miruvor", "type": "consumable",
        "heal": 40, "price": 20, "stackable": True,
        "desc": "The cordial of Imladris, restoring the weary.",
    },
    "athelas": {
        "name": "Athelas", "type": "consumable",
        "heal": 80, "price": 35, "stackable": True,
        "desc": "The healing herb of the Rangers, potent against shadow-sickness.",
    },
    "lembas_bread": {
        "name": "Lembas Bread", "type": "consumable",
        "heal": 50, "restore_mp": 30, "price": 40, "stackable": True,
        "desc": "Elven waybread, sustaining body and spirit in one bite.",
    },
    "ent_draught": {
        "name": "Ent-draught", "type": "consumable",
        "restore_mp": 40, "price": 25, "stackable": True,
        "desc": "A draught from the Ents of Fangorn, restoring spirit.",
    },
    "phial_galadriel": {
        "name": "Phial of Galadriel", "type": "consumable",
        "restore_mp": 80, "price": 60, "stackable": True,
        "desc": "A crystal phial filled with starlight, banishing darkness.",
    },
    "elixir_of_power": {
        "name": "Elixir of Power", "type": "consumable",
        "heal": 60, "restore_mp": 30, "price": 55, "stackable": True,
        "desc": "A rare elixir blended from Elven herbs and Ent-water.",
    },
}


class Inventory:
    """Inventory: 20 bag slots + 6 equipment slots."""

    MAX_SLOTS = 20

    def __init__(self):
        self.items = []                          # [{"id": str, "count": int}, ...]
        self.equipped = {s: None for s in EQUIP_SLOTS}
        self.gold = 0

    # ── Bag operations ─────────────────────────────────────────────────────

    def add_item(self, item_id, count=1):
        item_data = ITEMS.get(item_id)
        if not item_data:
            return False
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

    # ── Equipment operations ───────────────────────────────────────────────

    def equip(self, item_id):
        """Move item from bag into its equipment slot; return True on success."""
        item_data = ITEMS.get(item_id)
        if not item_data:
            return False
        slot_name = item_data.get("slot")
        if slot_name not in EQUIP_SLOTS:
            return False
        if not self.has_item(item_id):
            return False
        old = self.equipped[slot_name]
        if old:
            self.add_item(old)
        self.remove_item(item_id)
        self.equipped[slot_name] = item_id
        return True

    def unequip(self, slot_name):
        """Return equipped item to bag; return True on success."""
        item_id = self.equipped.get(slot_name)
        if not item_id:
            return False
        if len(self.items) >= self.MAX_SLOTS:
            return False
        self.equipped[slot_name] = None
        self.add_item(item_id)
        return True

    def use_item(self, item_id, stats):
        item_data = ITEMS.get(item_id)
        if not item_data or item_data.get("type") != "consumable":
            return False
        if not self.has_item(item_id):
            return False
        self.remove_item(item_id)
        if "heal" in item_data:
            stats.heal(item_data["heal"])
        if "restore_mp" in item_data:
            stats.restore_mp(item_data["restore_mp"])
        return True

    # ── Aggregate stats ────────────────────────────────────────────────────

    def get_total_stats(self):
        """Return combined stat bonuses from all equipped items + active sets."""
        total = {"atk": 0, "def_": 0, "str": 0, "dex": 0, "int": 0, "crit": 0}
        for item_id in self.equipped.values():
            if item_id:
                for stat, val in ITEMS.get(item_id, {}).get("stats", {}).items():
                    total[stat] = total.get(stat, 0) + val
        # Set bonuses
        equipped_ids = {v for v in self.equipped.values() if v}
        for set_data in ITEM_SETS.values():
            count = sum(1 for iid in set_data["items"] if iid in equipped_ids)
            for req, bonus in set_data["bonuses"].items():
                if count >= req:
                    for stat, val in bonus.items():
                        total[stat] = total.get(stat, 0) + val
        return total

    def get_active_sets(self):
        """Return list of (set_key, equipped_count, total_pieces, bonuses_active)."""
        equipped_ids = {v for v in self.equipped.values() if v}
        result = []
        for key, set_data in ITEM_SETS.items():
            count = sum(1 for iid in set_data["items"] if iid in equipped_ids)
            if count > 0:
                result.append((key, count, len(set_data["items"]),
                                count >= min(set_data["bonuses"].keys())))
        return result

    def get_stat_comparison(self, item_id):
        """
        Return stat delta dict between item_id and the currently equipped item
        in the same slot.  Positive = improvement, negative = downgrade.
        Returns None if item_id is not equippable.
        """
        item_data = ITEMS.get(item_id)
        if not item_data or "slot" not in item_data:
            return None
        new_stats = item_data.get("stats", {})
        old_id = self.equipped.get(item_data["slot"])
        old_stats = ITEMS.get(old_id, {}).get("stats", {}) if old_id else {}
        all_keys = set(new_stats) | set(old_stats)
        return {k: new_stats.get(k, 0) - old_stats.get(k, 0) for k in all_keys}

    # ── Backward-compatible helpers ────────────────────────────────────────

    def get_equipped_weapon(self):
        wid = self.equipped.get("weapon")
        return ITEMS.get(wid) if wid else None

    def get_total_defense(self):
        return self.get_total_stats().get("def_", 0)

    def get_stat_bonus(self, stat_name):
        return self.get_total_stats().get(stat_name, 0)
