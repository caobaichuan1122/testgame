# ============================================================
#  Logging system: file rotation + console output
# ============================================================
import logging
import logging.handlers
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "game.log")
LOG_FORMAT = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False


def setup_logging(level=logging.DEBUG):
    """Initialize the game logging system.

    - File handler: DEBUG+, rotating (1 MB × 3 backups), logs/game.log
    - Console handler: WARNING+ only (keeps terminal clean during gameplay)
    """
    global _initialized
    if _initialized:
        return
    _initialized = True

    os.makedirs(LOG_DIR, exist_ok=True)

    root = logging.getLogger("game")
    root.setLevel(level)

    # Rotating file handler: keeps up to 3 × 1 MB log files
    fh = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    root.addHandler(fh)

    # Console handler: only warnings and above to avoid gameplay noise
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    root.addHandler(ch)


def get_logger(name):
    """Return a named child logger under the 'game' namespace."""
    return logging.getLogger(f"game.{name}")
