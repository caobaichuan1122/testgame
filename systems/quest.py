# ============================================================
#  Quest system: objective tracking, rewards
# ============================================================
from systems.i18n import tf
from core.logger import get_logger

log = get_logger("quest")


class QuestManager:
    """Manages all quests."""

    def __init__(self):
        # quest_id → quest data
        self.quests = {}
        self.active_quest_hint = ""  # Current quest hint

    def register(self, quest_id, data):
        """Register a quest.
        data: {
            "name": str,
            "desc": str,
            "type": "kill" | "collect" | "talk" | "explore" | "escort" | "timed_kill",
            "target": str,           # Target type/item/NPC
            "required": int,         # Required count
            "progress": 0,
            "rewards": {"xp": int, "gold": int, "items": [str]},
            "status": "available",   # available→active→completable→completed / failed
            # explore-specific:
            "zones": [{"name":str, "x1","y1","x2","y2"}],  # List of exploration zones
            "discovered": [],        # Discovered zone names
            # escort-specific:
            "escort_dest": (x, y),   # Escort destination
            "escort_radius": float,  # Arrival radius
            # timed_kill-specific:
            "time_limit": int,       # Seconds
        }
        """
        data.setdefault("progress", 0)
        data.setdefault("status", "available")
        data.setdefault("discovered", [])
        data.setdefault("_timer", 0)
        self.quests[quest_id] = data

    def get_quest(self, quest_id):
        return self.quests.get(quest_id)

    def accept_quest(self, quest_id):
        quest = self.quests.get(quest_id)
        if quest and quest["status"] == "available":
            quest["status"] = "active"
            quest["progress"] = 0
            quest["discovered"] = []
            # Start timer for timed quest
            if quest["type"] == "timed_kill":
                quest["_timer"] = quest.get("time_limit", 60) * 60  # seconds → frames
            self._update_hint()
            log.info("Quest accepted: %s (%s)", quest_id, quest.get("name", ""))
            return True
        return False

    def on_enemy_kill(self, enemy_type):
        """Update quest progress when an enemy is killed."""
        for qid, q in self.quests.items():
            if q["status"] == "active" and q["type"] in ("kill", "timed_kill"):
                if q["target"] == enemy_type:
                    q["progress"] = min(q["progress"] + 1, q["required"])
                    if q["progress"] >= q["required"]:
                        q["status"] = "completable"
        self._update_hint()

    def on_collect(self, item_id):
        for qid, q in self.quests.items():
            if q["status"] == "active" and q["type"] == "collect":
                if q["target"] == item_id:
                    q["progress"] = min(q["progress"] + 1, q["required"])
                    if q["progress"] >= q["required"]:
                        q["status"] = "completable"
        self._update_hint()

    def on_player_move(self, player_wx, player_wy, scene_id=None):
        """Detect exploration quest zones on player movement.

        Zones with a 'scene' key are matched by scene_id + local coords.
        Zones without 'scene' fall back to world-coordinate matching.
        """
        discovered_names = []
        for qid, q in self.quests.items():
            if q["status"] == "active" and q["type"] == "explore":
                zones = q.get("zones", [])
                for zone in zones:
                    if zone["name"] in q["discovered"]:
                        continue
                    zone_scene = zone.get("scene")
                    if zone_scene is not None:
                        # Scene-aware: must be in the right scene AND local area
                        if scene_id != zone_scene:
                            continue
                    # Coordinate check (local coords for scene zones, world for legacy)
                    if (zone["x1"] <= player_wx <= zone["x2"] and
                            zone["y1"] <= player_wy <= zone["y2"]):
                        q["discovered"].append(zone["name"])
                        q["progress"] = len(q["discovered"])
                        discovered_names.append(zone["name"])
                        if q["progress"] >= q["required"]:
                            q["status"] = "completable"
        self._update_hint()
        return discovered_names

    def on_escort_arrive(self, npc_wx, npc_wy):
        """Detect escort NPC arrival at destination."""
        import math
        for qid, q in self.quests.items():
            if q["status"] == "active" and q["type"] == "escort":
                dest = q.get("escort_dest")
                radius = q.get("escort_radius", 3.0)
                if dest:
                    dx = npc_wx - dest[0]
                    dy = npc_wy - dest[1]
                    if math.sqrt(dx * dx + dy * dy) < radius:
                        q["progress"] = q["required"]
                        q["status"] = "completable"
                        self._update_hint()
                        return qid
        return None

    def update_timers(self):
        """Update timed quest timers each frame; return list of just-failed quests."""
        failed = []
        for qid, q in self.quests.items():
            if q["status"] == "active" and q["type"] == "timed_kill":
                if q["_timer"] > 0:
                    q["_timer"] -= 1
                    if q["_timer"] <= 0:
                        q["status"] = "failed"
                        failed.append((qid, q))
                        log.warning("Quest failed (timeout): %s (%s)",
                                    qid, q.get("name", ""))
        if failed:
            self._update_hint()
        return failed

    def complete_quest(self, quest_id, game):
        """Complete a quest and grant rewards."""
        quest = self.quests.get(quest_id)
        if not quest or quest["status"] != "completable":
            return False

        quest["status"] = "completed"
        log.info("Quest completed: %s (%s)", quest_id, quest.get("name", ""))
        rewards = quest.get("rewards", {})

        player = game.entities.player
        if player:
            xp = rewards.get("xp", 0)
            gold = rewards.get("gold", 0)
            if xp > 0:
                player.stats.add_xp(xp)
            if gold > 0:
                player.inventory.gold += gold
            for item_id in rewards.get("items", []):
                player.inventory.add_item(item_id)
            player.add_message(tf("quest_complete_msg", xp=xp, gold=gold))

        self._update_hint()
        return True

    def get_active_quests(self):
        """Get all active quests."""
        return [(qid, q) for qid, q in self.quests.items()
                if q["status"] in ("active", "completable")]

    def get_all_quests(self):
        return list(self.quests.items())

    def _update_hint(self):
        """Update HUD quest hint."""
        for qid, q in self.quests.items():
            if q["status"] == "active":
                if q["type"] == "timed_kill":
                    secs = max(0, q["_timer"] // 60)
                    self.active_quest_hint = tf(
                        "hint_timed", name=q['name'],
                        progress=q['progress'], required=q['required'], secs=secs)
                elif q["type"] == "explore":
                    self.active_quest_hint = tf(
                        "hint_explore", name=q['name'],
                        progress=q['progress'], required=q['required'])
                elif q["type"] == "escort":
                    self.active_quest_hint = tf("hint_escort", name=q['name'])
                else:
                    self.active_quest_hint = tf(
                        "hint_default", name=q['name'],
                        progress=q['progress'], required=q['required'])
                return
            elif q["status"] == "completable":
                self.active_quest_hint = tf("hint_complete", name=q['name'])
                return
        self.active_quest_hint = ""
