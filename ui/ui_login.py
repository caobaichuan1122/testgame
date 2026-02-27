# ============================================================
#  Login / Register screen (screen resolution)
#  Shown before the main menu.
#  Tab   — switch between username / password fields
#  Enter — confirm (login or register depending on active tab)
#  ESC   — skip and play offline
# ============================================================
import pygame
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_ACCENT, COLOR_UI
from core.utils import draw_text, get_font, FONT_UI_SM, FONT_UI_MD, FONT_UI_LG


# UI measurements (pixels at screen resolution)
_PANEL_W = 400
_PANEL_H = 320
_FIELD_H = 36
_FIELD_W = 300


class _InputField:
    """Single text input box."""

    def __init__(self, label: str, masked: bool = False, max_len: int = 32):
        self.label = label
        self.masked = masked
        self.max_len = max_len
        self.text = ""
        self.active = False

    def handle_key(self, key: int) -> bool:
        """Return True if key was consumed."""
        if not self.active:
            return False
        if key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
            return True
        return False

    def handle_text(self, char: str):
        if self.active and len(self.text) < self.max_len:
            self.text += char

    def draw(self, surface, x, y, font, focused: bool):
        # Label
        label_surf = font.render(self.label, False, (160, 160, 180))
        surface.blit(label_surf, (x, y - 20))

        # Box background
        box_color = (45, 45, 60) if not focused else (55, 55, 80)
        border_color = COLOR_ACCENT if focused else (80, 80, 100)
        pygame.draw.rect(surface, box_color, (x, y, _FIELD_W, _FIELD_H), border_radius=4)
        pygame.draw.rect(surface, border_color, (x, y, _FIELD_W, _FIELD_H), 1, border_radius=4)

        # Text / cursor
        display = ("*" * len(self.text)) if self.masked else self.text
        if focused:
            cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            display += cursor
        text_surf = font.render(display, False, COLOR_UI)
        surface.blit(text_surf, (x + 10, y + (_FIELD_H - text_surf.get_height()) // 2))


class LoginUI:
    """Login / Register screen shown at game startup."""

    # Tabs
    TAB_LOGIN = "login"
    TAB_REGISTER = "register"

    def __init__(self):
        self._tab = self.TAB_LOGIN
        self._username = _InputField("Username", max_len=32)
        self._password = _InputField("Password", masked=True, max_len=64)
        self._focus = 0          # 0 = username, 1 = password
        self._status_msg = ""    # feedback message shown under buttons
        self._status_ok = True   # True = green, False = red
        self._busy = False       # True while waiting for API response
        self._username.active = True
        self._update_active()

    # ── Public API ─────────────────────────────────────────────

    def set_status(self, msg: str, ok: bool = True):
        self._status_msg = msg
        self._status_ok = ok
        self._busy = False

    def handle_text(self, char: str):
        self._username.handle_text(char)
        self._password.handle_text(char)

    def handle_key(self, key: int, game) -> bool:
        """
        Returns True  → login/register attempt triggered (caller should call api)
        Returns False → just UI navigation, no action needed
        Returns "offline" → player chose to skip login
        """
        if self._busy:
            return False

        if key == pygame.K_TAB:
            # Switch focus between fields
            self._focus = (self._focus + 1) % 2
            self._update_active()
            return False

        if key == pygame.K_BACKSPACE:
            self._username.handle_key(key)
            self._password.handle_key(key)
            return False

        if key == pygame.K_ESCAPE:
            return "offline"

        if key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            return self._confirm(game)

        # F1/F2 to switch tab
        if key == pygame.K_F1:
            self._tab = self.TAB_LOGIN
            self._status_msg = ""
            return False
        if key == pygame.K_F2:
            self._tab = self.TAB_REGISTER
            self._status_msg = ""
            return False

        return False

    def draw(self, surface):
        surface.fill(COLOR_BG)

        font_lg = get_font(FONT_UI_LG)
        font_md = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        # Title
        draw_text(surface, "Middle-earth: Shadows of Arda",
                  cx, cy - 175, font_lg, COLOR_UI, center=True)

        # Panel background
        px = cx - _PANEL_W // 2
        py = cy - _PANEL_H // 2
        panel = pygame.Surface((_PANEL_W, _PANEL_H), pygame.SRCALPHA)
        panel.fill((20, 20, 32, 220))
        surface.blit(panel, (px, py))
        pygame.draw.rect(surface, (60, 60, 90), (px, py, _PANEL_W, _PANEL_H), 1)

        # Tab buttons
        tab_y = py + 14
        tab_w = _PANEL_W // 2
        for i, (label, tab) in enumerate(
                [("F1  Login", self.TAB_LOGIN), ("F2  Register", self.TAB_REGISTER)]):
            active = self._tab == tab
            tx = px + i * tab_w
            bg = (50, 50, 75) if active else (30, 30, 45)
            pygame.draw.rect(surface, bg, (tx, tab_y, tab_w, 28))
            color = COLOR_ACCENT if active else (120, 120, 140)
            draw_text(surface, label, tx + tab_w // 2, tab_y + 5, font_sm, color, center=True)
        pygame.draw.line(surface, (60, 60, 90),
                         (px, tab_y + 28), (px + _PANEL_W, tab_y + 28))

        # Input fields
        field_x = cx - _FIELD_W // 2
        self._username.draw(surface, field_x, py + 68, font_sm, self._focus == 0)
        self._password.draw(surface, field_x, py + 140, font_sm, self._focus == 1)

        # Confirm button
        btn_label = "Login" if self._tab == self.TAB_LOGIN else "Register"
        btn_text = "Connecting..." if self._busy else f"Enter — {btn_label}"
        btn_color = (100, 100, 120) if self._busy else COLOR_ACCENT
        draw_text(surface, btn_text, cx, py + 212, font_md, btn_color, center=True)

        # Offline button
        draw_text(surface, "ESC — Play Offline",
                  cx, py + 248, font_sm, (100, 100, 120), center=True)

        # Status message
        if self._status_msg:
            color = (80, 220, 100) if self._status_ok else (220, 80, 80)
            draw_text(surface, self._status_msg, cx, py + _PANEL_H + 12,
                      font_sm, color, center=True)

    # ── Internal ───────────────────────────────────────────────

    def _update_active(self):
        self._username.active = (self._focus == 0)
        self._password.active = (self._focus == 1)

    def _confirm(self, game) -> bool:
        username = self._username.text.strip()
        password = self._password.text

        if not username:
            self.set_status("Username cannot be empty", ok=False)
            return False
        if not password:
            self.set_status("Password cannot be empty", ok=False)
            return False

        self._busy = True
        self._status_msg = ""

        from core.api_client import api
        if self._tab == self.TAB_LOGIN:
            ok, msg = api.login(username, password)
        else:
            ok, msg = api.register(username, password)
            if ok:
                # Auto-switch to login tab after registration
                self._tab = self.TAB_LOGIN
                self._password.text = ""
                self.set_status(msg, ok=True)
                return False

        self.set_status(msg, ok=ok)
        return ok  # True means login succeeded → caller advances state
