# ============================================================
#  SettingsManager — persistent user config (resolution, fullscreen, language)
# ============================================================
import json
import os

RESOLUTIONS = [
    (960, 640),
    (1280, 720),
    (1600, 900),
    (1920, 1080),
]

# 0% to 100% in 10% steps
VOLUME_STEPS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
DIFFICULTY_LEVELS = ["easy", "normal", "hard"]

_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json"
)


class SettingsManager:
    def __init__(self):
        self.resolution_index = 0
        self.fullscreen = False
        self.language = "zh"
        self.music_enabled = True
        self.music_volume_idx = 5   # index into VOLUME_STEPS → 0.5 (50%)
        self.show_fps = False
        self.difficulty = "normal"
        self.load()

    @property
    def resolution(self):
        return RESOLUTIONS[self.resolution_index]

    @property
    def music_volume(self):
        return VOLUME_STEPS[self.music_volume_idx]

    def load(self):
        if not os.path.exists(_CONFIG_PATH):
            return
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            res = tuple(data.get("resolution", [960, 640]))
            res_list = [list(r) for r in RESOLUTIONS]
            if list(res) in res_list:
                self.resolution_index = res_list.index(list(res))
            self.fullscreen = bool(data.get("fullscreen", False))
            lang = data.get("language", "zh")
            if lang in ("zh", "en"):
                self.language = lang
            self.music_enabled = bool(data.get("music_enabled", True))
            vol_idx = data.get("music_volume_idx", 5)
            if isinstance(vol_idx, int) and 0 <= vol_idx < len(VOLUME_STEPS):
                self.music_volume_idx = vol_idx
            self.show_fps = bool(data.get("show_fps", False))
            diff = data.get("difficulty", "normal")
            if diff in DIFFICULTY_LEVELS:
                self.difficulty = diff
        except Exception:
            pass

    def save(self):
        data = {
            "resolution": list(self.resolution),
            "fullscreen": self.fullscreen,
            "language": self.language,
            "music_enabled": self.music_enabled,
            "music_volume_idx": self.music_volume_idx,
            "show_fps": self.show_fps,
            "difficulty": self.difficulty,
        }
        try:
            with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def next_resolution(self):
        self.resolution_index = (self.resolution_index + 1) % len(RESOLUTIONS)

    def prev_resolution(self):
        self.resolution_index = (self.resolution_index - 1) % len(RESOLUTIONS)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen

    def toggle_language(self):
        self.language = "en" if self.language == "zh" else "zh"

    def toggle_music(self):
        self.music_enabled = not self.music_enabled

    def next_volume(self):
        self.music_volume_idx = min(len(VOLUME_STEPS) - 1, self.music_volume_idx + 1)

    def prev_volume(self):
        self.music_volume_idx = max(0, self.music_volume_idx - 1)

    def toggle_fps(self):
        self.show_fps = not self.show_fps

    def next_difficulty(self):
        idx = DIFFICULTY_LEVELS.index(self.difficulty)
        self.difficulty = DIFFICULTY_LEVELS[(idx + 1) % len(DIFFICULTY_LEVELS)]

    def prev_difficulty(self):
        idx = DIFFICULTY_LEVELS.index(self.difficulty)
        self.difficulty = DIFFICULTY_LEVELS[(idx - 1) % len(DIFFICULTY_LEVELS)]
