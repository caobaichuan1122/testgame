# ============================================================
#  Save / Load system — 10-slot JSON save files
# ============================================================
import json
import os
from datetime import datetime
from core.logger import get_logger

log = get_logger("save")

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_DIR   = os.path.join(_BASE, "saves")
SAVE_VERSION = 3
SLOT_COUNT = 10

def slot_file(slot: int) -> str:
    """Return path for save_01 … save_10."""
    return os.path.join(SAVE_DIR, f"save_{slot:02d}.json")


def _zone_display_name(game) -> str:
    """Return a translated zone name for the save slot display."""
    if not game.scene_mgr:
        return "Unknown"
    active_id = game.scene_mgr.active_id
    try:
        from systems.i18n import t
        from world.demo_level import ZONES
        for z in ZONES:
            if z["id"] == active_id:
                return t(z["name_key"])
    except Exception:
        pass
    return active_id


def list_slots() -> list:
    """Return list of length SLOT_COUNT; each entry is None (empty) or a meta dict."""
    result = []
    for slot in range(1, SLOT_COUNT + 1):
        path = slot_file(slot)
        if not os.path.exists(path):
            result.append(None)
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            result.append(data.get("meta", {}))
        except Exception:
            result.append(None)
    return result


def save(game, slot: int) -> bool:
    """Serialize current game state to saves/save_NN.json. Returns True on success."""
    player = game.entities.player
    if not player:
        return False

    stats = player.stats
    inv   = player.inventory

    # Build meta block
    meta = {
        "slot":      slot,
        "save_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "level":     stats.level,
        "zone":      _zone_display_name(game),
    }

    data = {
        "version": SAVE_VERSION,
        "meta":    meta,
        "player": {
            "wx": player.wx,
            "wy": player.wy,
            "stats": {
                "hp":          stats.hp,
                "max_hp":      stats.max_hp,
                "mp":          stats.mp,
                "max_mp":      stats.max_mp,
                "str":         stats.str,
                "dex":         stats.dex,
                "int":         stats.int,
                "def_":        stats.def_,
                "level":       stats.level,
                "xp":          stats.xp,
                "free_points": stats.free_points,
            },
            "inventory": {
                "gold":    inv.gold,
                "items":   list(inv.items),
                "equipped": dict(inv.equipped),
            },
        },
        "current_scene": game.scene_mgr.active_id if game.scene_mgr else "hobbiton",
        "quests":       {},
        "enemies_dead": [],
    }

    # Quest state
    if game.quest_manager:
        for qid, q in game.quest_manager.quests.items():
            entry = {
                "status":   q["status"],
                "progress": q.get("progress", 0),
            }
            if "discovered" in q:
                entry["discovered"] = list(q["discovered"])
            data["quests"][qid] = entry

    # Dead enemies
    for i, e in enumerate(game.entities.enemies):
        if not e.active:
            data["enemies_dead"].append(i)

    os.makedirs(SAVE_DIR, exist_ok=True)
    path = slot_file(slot)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log.info("Game saved → slot %d (%s)", slot, path)
        return True
    except Exception as exc:
        log.error("Save failed (slot %d): %s", slot, exc)
        return False


def load(game, slot: int) -> bool:
    """Restore game state from saves/save_NN.json. Returns True on success."""
    path = slot_file(slot)
    if not os.path.exists(path):
        log.warning("Load attempted but slot %d has no file", slot)
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        log.error("Load failed (slot %d, read error): %s", slot, exc)
        return False

    if data.get("version") not in (SAVE_VERSION, 2):  # accept v2 (will be migrated)
        log.warning("Save version mismatch in slot %d (%s), ignoring", slot, data.get("version"))
        return False

    # Rebuild level fresh, then overlay saved data
    game.load_level()

    # Restore scene before applying positions / dead enemies
    saved_scene = data.get("current_scene", "hobbiton")
    if saved_scene != "hobbiton" and game.scene_mgr:
        game._activate_scene(saved_scene, start_fade=False)

    player = game.entities.player
    stats  = player.stats
    inv    = player.inventory

    pd = data["player"]
    player.wx = float(pd["wx"])
    player.wy = float(pd["wy"])

    sd = pd["stats"]
    stats.hp          = sd["hp"]
    stats.max_hp      = sd["max_hp"]
    stats.mp          = sd["mp"]
    stats.max_mp      = sd["max_mp"]
    stats.str         = sd["str"]
    stats.dex         = sd["dex"]
    stats.int         = sd["int"]
    stats.def_        = sd["def_"]
    stats.level       = sd["level"]
    stats.xp          = sd["xp"]
    stats.free_points = sd["free_points"]

    id_ = pd["inventory"]
    inv.gold     = id_["gold"]
    inv.items    = id_["items"]
    raw_equipped = id_["equipped"]
    # Migrate old format: "accessory" slot → "ring"
    if "accessory" in raw_equipped and "ring" not in raw_equipped:
        raw_equipped["ring"] = raw_equipped.pop("accessory")
    # Fill any missing new slots with None
    from systems.inventory import EQUIP_SLOTS
    for slot in EQUIP_SLOTS:
        if slot not in raw_equipped:
            raw_equipped[slot] = None
    inv.equipped = raw_equipped

    for qid, qd in data.get("quests", {}).items():
        if qid in game.quest_manager.quests:
            q = game.quest_manager.quests[qid]
            q["status"]   = qd["status"]
            q["progress"] = qd["progress"]
            if "discovered" in qd:
                q["discovered"] = qd["discovered"]

    # Apply dead enemies to the restored scene
    dead_set = set(data.get("enemies_dead", []))
    for i, e in enumerate(game.entities.enemies):
        if i in dead_set:
            e.active = False

    game.camera.snap(player.wx, player.wy)
    log.info("Game loaded ← slot %d (%s)", slot, path)
    return True


def delete_slot(slot: int):
    """Delete a save slot file."""
    path = slot_file(slot)
    if os.path.exists(path):
        os.remove(path)
        log.info("Deleted save slot %d", slot)


def has_any_save() -> bool:
    """Return True if at least one slot has a save file."""
    return any(os.path.exists(slot_file(s)) for s in range(1, SLOT_COUNT + 1))


# Backward-compat alias
has_save = has_any_save
