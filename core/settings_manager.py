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

_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json"
)


class SettingsManager:
    def __init__(self):
        self.resolution_index = 0
        self.fullscreen = False
        self.language = "zh"
        self.music_enabled = True
        self.load()

    @property
    def resolution(self):
        return RESOLUTIONS[self.resolution_index]

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
        except Exception:
            pass

    def save(self):
        data = {
            "resolution": list(self.resolution),
            "fullscreen": self.fullscreen,
            "language": self.language,
            "music_enabled": self.music_enabled,
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
