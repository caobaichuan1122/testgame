# ============================================================
#  Message log: persistent game message history
#  (combat / loot / quest / system / dialogue)
# ============================================================

# Message category colors
CATEGORY_COLORS = {
    "combat":   (220, 80, 80),
    "loot":     (255, 215, 0),
    "quest":    (80, 220, 80),
    "system":   (180, 180, 180),
    "dialogue": (100, 200, 220),
    "player":   (150, 220, 255),
}

MAX_MESSAGES = 100


class ChatLog:
    def __init__(self):
        self.messages = []  # [(text, category, tick)]
        self._tick = 0

    def add(self, text, category="system"):
        self.messages.append((text, category, self._tick))
        if len(self.messages) > MAX_MESSAGES:
            self.messages.pop(0)

    def get_recent(self, n=5):
        return self.messages[-n:]

    def advance_tick(self):
        self._tick += 1

    @property
    def tick(self):
        return self._tick
