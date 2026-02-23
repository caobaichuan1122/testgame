# ============================================================
#  Entry point
# ============================================================
from core.logger import setup_logging, get_logger
from core.game import Game

log = get_logger("main")


def main():
    setup_logging()
    log.info("Game starting")
    try:
        game = Game()
        game.run()
    except Exception:
        log.exception("Unhandled exception — game crashed")
        raise
    finally:
        log.info("Game exited")


if __name__ == "__main__":
    main()
