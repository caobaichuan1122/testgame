# ============================================================
#  API Client — pre-built interfaces for Django backend
#  All methods return (success: bool, data: dict | str)
#  Connection errors are caught and returned as (False, msg)
#  so the game can fall back to offline mode gracefully.
# ============================================================
import requests
from core.logger import get_logger

log = get_logger("api")

API_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 5  # seconds


class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token: str | None = None
        self.username: str | None = None
        self.user_id: int | None = None
        self.is_online: bool = False

    # ── Internal helpers ───────────────────────────────────────

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Token {self.token}"
        return h

    def _post(self, endpoint: str, data: dict) -> tuple:
        try:
            resp = requests.post(
                f"{self.base_url}{endpoint}",
                json=data,
                headers=self._headers(),
                timeout=TIMEOUT,
            )
            return resp.status_code, resp.json()
        except requests.exceptions.ConnectionError:
            log.warning("Connection refused: %s", endpoint)
            return None, {"detail": "Cannot connect to server"}
        except requests.exceptions.Timeout:
            log.warning("Timeout: %s", endpoint)
            return None, {"detail": "Request timed out"}
        except Exception as e:
            log.error("API error [%s]: %s", endpoint, e)
            return None, {"detail": str(e)}

    def _get(self, endpoint: str, params: dict | None = None) -> tuple:
        try:
            resp = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=self._headers(),
                timeout=TIMEOUT,
            )
            return resp.status_code, resp.json()
        except requests.exceptions.ConnectionError:
            log.warning("Connection refused: %s", endpoint)
            return None, {"detail": "Cannot connect to server"}
        except requests.exceptions.Timeout:
            log.warning("Timeout: %s", endpoint)
            return None, {"detail": "Request timed out"}
        except Exception as e:
            log.error("API error [%s]: %s", endpoint, e)
            return None, {"detail": str(e)}

    # ── Auth ───────────────────────────────────────────────────

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """POST /api/auth/login/
        Django side: knox / dj-rest-auth token login.
        Returns (True, welcome_msg) or (False, error_msg).
        """
        status, data = self._post("/api/auth/login/", {
            "username": username,
            "password": password,
        })
        if status == 200:
            self.token = data.get("token") or data.get("key")
            self.username = data.get("username", username)
            self.user_id = data.get("user_id")
            self.is_online = True
            log.info("Login OK: %s (user_id=%s)", self.username, self.user_id)
            return True, f"Welcome, {self.username}!"
        if status is None:
            return False, data.get("detail", "Cannot connect to server")
        # 400 / 401
        detail = data.get("detail") or data.get("non_field_errors", ["Login failed"])[0]
        log.warning("Login failed for %s: %s", username, detail)
        return False, str(detail)

    def register(self, username: str, password: str) -> tuple[bool, str]:
        """POST /api/auth/register/
        Django side: dj-rest-auth registration endpoint.
        Returns (True, msg) or (False, error_msg).
        """
        status, data = self._post("/api/auth/register/", {
            "username": username,
            "password1": password,
            "password2": password,
        })
        if status == 201:
            log.info("Register OK: %s", username)
            return True, "Account created! Please log in."
        if status is None:
            return False, data.get("detail", "Cannot connect to server")
        # Extract first validation error
        for field, msgs in data.items():
            if isinstance(msgs, list) and msgs:
                return False, str(msgs[0])
        return False, data.get("detail", "Registration failed")

    def logout(self) -> tuple[bool, str]:
        """POST /api/auth/logout/
        Invalidates the server-side token.
        Always clears local credentials even if request fails.
        """
        if not self.token:
            return True, "Already logged out"
        self._post("/api/auth/logout/", {})
        self.token = None
        self.username = None
        self.user_id = None
        self.is_online = False
        log.info("Logged out")
        return True, "Logged out"

    # ── Save / Load ────────────────────────────────────────────

    def save_game(self, save_data: dict) -> tuple[bool, str]:
        """POST /api/game/save/
        save_data example:
          {
            "level": 5,
            "hp": 60, "mp": 30,
            "gold": 250,
            "xp": 1200,
            "position": [30, 30],
            "inventory": ["sting", "miruvor"],
            "equipped": {"weapon": "sting"},
            "quests": {"quest_orc": "completed"}
          }
        """
        if not self.token:
            return False, "Not logged in"
        status, data = self._post("/api/game/save/", save_data)
        if status in (200, 201):
            log.info("Cloud save OK for %s", self.username)
            return True, "Game saved to cloud"
        if status is None:
            return False, data.get("detail", "Cannot connect to server")
        return False, data.get("detail", "Save failed")

    def load_save(self) -> tuple[bool, dict | str]:
        """GET /api/game/save/
        Returns (True, save_dict) on success, (False, error_msg) otherwise.
        """
        if not self.token:
            return False, "Not logged in"
        status, data = self._get("/api/game/save/")
        if status == 200:
            log.info("Cloud load OK for %s", self.username)
            return True, data
        if status == 404:
            return False, "No cloud save found"
        if status is None:
            return False, data.get("detail", "Cannot connect to server")
        return False, data.get("detail", "Load failed")

    # ── Ranking ────────────────────────────────────────────────

    def get_ranking(self, limit: int = 10) -> tuple[bool, list | str]:
        """GET /api/game/ranking/?limit=10
        Returns (True, [ {username, level, kills, ...}, ... ]) or (False, msg).
        """
        status, data = self._get("/api/game/ranking/", params={"limit": limit})
        if status == 200:
            return True, data
        if status is None:
            return False, data.get("detail", "Cannot connect to server")
        return False, data.get("detail", "Failed to fetch ranking")


# Global singleton — import and use anywhere:
#   from core.api_client import api
#   ok, msg = api.login("player1", "password")
api = APIClient()
