# ============================================================
#  Main menu / pause / game over / settings screen
# ============================================================
import pygame
from core.settings import (
    COLOR_UI, COLOR_ACCENT, COLOR_BG, WINDOW_TITLE,
)
from systems.i18n import t
from core.utils import draw_text, get_font, FONT_UI_SM, FONT_UI_MD, FONT_UI_LG

_PAUSE_ITEMS = ["menu_resume", "menu_settings", "menu_main_menu"]


class MenuUI:
    def __init__(self):
        self._slot_sel    = 0   # 0-9, which slot is highlighted in main menu
        self._pause_sel   = 0   # highlighted pause menu item
        self._settings_sel = 0  # highlighted settings row
        self._prompt_sel  = 0   # 0=Save  1=Don't Save  2=Cancel
        self._slots_cache = None  # cached list_slots() result

    def refresh_slots(self):
        """Force re-read of all slot files."""
        from core.save_manager import list_slots
        self._slots_cache = list_slots()

    def _get_slots(self):
        if self._slots_cache is None:
            self.refresh_slots()
        return self._slots_cache

    # ------------------------------------------------------------------
    #  Mouse hittest helpers — return selected index or -1
    # ------------------------------------------------------------------
    def hittest_slot(self, pos) -> int:
        """Main menu: return slot index 0-9 if pos hits a slot row, else -1."""
        sw, sh = pygame.display.get_surface().get_size()
        cx = sw // 2
        slot_h  = 36
        panel_w = min(sw - 80, 560)
        panel_x = cx - panel_w // 2
        panel_y = sh // 6 + 70
        slots = self._get_slots()
        for i in range(len(slots)):
            row_y = panel_y + 10 + i * slot_h
            if panel_x <= pos[0] <= panel_x + panel_w and row_y <= pos[1] <= row_y + slot_h:
                return i
        return -1

    def hittest_pause(self, pos) -> int:
        """Pause menu: return item index 0-2 if clicked, else -1."""
        sw, sh = pygame.display.get_surface().get_size()
        cx = sw // 2
        cy = sh // 5
        item_h  = 52
        panel_w = 300
        panel_x = cx - panel_w // 2
        panel_y = cy + 72
        for i in range(len(_PAUSE_ITEMS)):
            item_y = panel_y + 12 + i * item_h
            if panel_x <= pos[0] <= panel_x + panel_w and item_y <= pos[1] <= item_y + item_h:
                return i
        return -1

    def hittest_save_prompt(self, pos) -> int:
        """Save prompt: return 0/1/2 (Save/NoSave/Cancel) if clicked, else -1."""
        sw, sh = pygame.display.get_surface().get_size()
        dlg_w, dlg_h = 420, 130
        dlg_x = sw // 2 - dlg_w // 2
        dlg_y = sh // 2 - dlg_h // 2
        # Divide dialog button row into three equal zones
        btn_y = dlg_y + 70
        if not (btn_y <= pos[1] <= dlg_y + dlg_h - 10):
            return -1
        zone_w = dlg_w // 3
        if dlg_x <= pos[0] < dlg_x + zone_w:
            return 0
        if dlg_x + zone_w <= pos[0] < dlg_x + zone_w * 2:
            return 1
        if dlg_x + zone_w * 2 <= pos[0] <= dlg_x + dlg_w:
            return 2
        return -1

    def hittest_settings_row(self, pos) -> int:
        """Settings: return row index 0-6 if clicked, else -1."""
        sw, sh = pygame.display.get_surface().get_size()
        cx = sw // 2
        cy = sh // 4
        row_start = cy + 100
        row_h     = 48
        box_x = cx - 260
        box_w = 520
        for i in range(7):
            y = row_start + i * row_h
            if box_x <= pos[0] <= box_x + box_w and y - 8 <= pos[1] <= y + row_h - 8:
                return i
        return -1

    def draw_main_menu(self, surface):
        font_big = get_font(FONT_UI_LG)
        font_md  = get_font(FONT_UI_MD)
        font_sm  = get_font(FONT_UI_SM)

        sw, sh = surface.get_size()
        surface.fill(COLOR_BG)
        cx = sw // 2

        # Title
        draw_text(surface, WINDOW_TITLE, cx, sh // 6, font_big, COLOR_UI, center=True)

        slots = self._get_slots()

        # Slot panel sizing
        slot_h   = 36
        panel_w  = min(sw - 80, 560)
        panel_h  = len(slots) * slot_h + 20
        panel_x  = cx - panel_w // 2
        panel_y  = sh // 6 + 70

        pygame.draw.rect(surface, (28, 26, 34),
                         (panel_x, panel_y, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(surface, (70, 60, 85),
                         (panel_x, panel_y, panel_w, panel_h), 1, border_radius=8)

        for i, meta in enumerate(slots):
            slot_num  = i + 1
            selected  = (i == self._slot_sel)
            row_y     = panel_y + 10 + i * slot_h

            if selected:
                hl = pygame.Rect(panel_x + 4, row_y - 2, panel_w - 8, slot_h - 4)
                pygame.draw.rect(surface, (50, 44, 65), hl, border_radius=5)

            marker = "\u25b6 " if selected else "  "
            num_str = f"{slot_num:02d}"

            if meta:
                level    = meta.get("level", "?")
                zone     = meta.get("zone", "")
                savetime = meta.get("save_time", "")
                row_text = f"{marker}{num_str}  Lv.{level}  {zone}  {savetime}"
                color    = COLOR_ACCENT if selected else COLOR_UI
            else:
                row_text = f"{marker}{num_str}  {t('slot_empty')}"
                color    = COLOR_ACCENT if selected else (100, 100, 100)

            draw_text(surface, row_text, panel_x + 16, row_y + 6, font_sm, color)

        # Hint below panel
        draw_text(surface, t("slot_hint"),
                  cx, panel_y + panel_h + 14, font_sm, (90, 90, 90), center=True)

        # Language hint bottom-center
        draw_text(surface, t("lang_switch_hint"),
                  cx, sh - 20, font_sm, (70, 70, 70), center=True)

    def draw_save_prompt(self, surface):
        """Draw semi-transparent save-before-leaving dialog."""
        font_md = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)

        sw, sh = surface.get_size()

        # Dim background
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # Dialog box
        dlg_w, dlg_h = 420, 130
        dlg_x = sw // 2 - dlg_w // 2
        dlg_y = sh // 2 - dlg_h // 2

        pygame.draw.rect(surface, (35, 32, 45),
                         (dlg_x, dlg_y, dlg_w, dlg_h), border_radius=8)
        pygame.draw.rect(surface, (110, 90, 140),
                         (dlg_x, dlg_y, dlg_w, dlg_h), 2, border_radius=8)

        cx = sw // 2

        draw_text(surface, t("save_prompt_title"),
                  cx, dlg_y + 28, font_md, COLOR_UI, center=True)

        options = ["save_prompt_save", "save_prompt_nosave", "save_prompt_cancel"]
        opt_texts = [t(k) for k in options]

        # Measure total width to center the three options
        gap = 36
        total_w = sum(font_sm.size(tx)[0] for tx in opt_texts) + gap * (len(opt_texts) - 1)
        start_x = cx - total_w // 2

        ox = start_x
        for i, tx in enumerate(opt_texts):
            tw, _ = font_sm.size(tx)
            selected = (i == self._prompt_sel)
            if selected:
                hl = pygame.Rect(ox - 6, dlg_y + 76, tw + 12, 24)
                pygame.draw.rect(surface, (65, 55, 85), hl, border_radius=4)
            color = COLOR_ACCENT if selected else (180, 180, 180)
            draw_text(surface, tx, ox, dlg_y + 80, font_sm, color)
            ox += tw + gap

        # Nav hint
        draw_text(surface, "[← →] Select   [Enter] Confirm   [ESC] Cancel",
                  cx, dlg_y + dlg_h - 18, font_sm, (70, 70, 70), center=True)

    def draw_settings(self, surface, settings_mgr):
        font_big = get_font(FONT_UI_LG)
        font_sm  = get_font(FONT_UI_SM)

        sw, sh = surface.get_size()
        surface.fill(COLOR_BG)

        cx = sw // 2
        cy = sh // 4

        draw_text(surface, t("settings"), cx, cy, font_big, COLOR_UI, center=True)

        option_keys = [
            "settings_resolution",
            "settings_fullscreen",
            "settings_language",
            "settings_music",
            "settings_volume",
            "settings_fps",
            "settings_difficulty",
        ]

        def get_value(idx):
            if idx == 0:
                w, h = settings_mgr.resolution
                return f"{w} x {h}"
            elif idx == 1:
                return t("settings_on") if settings_mgr.fullscreen else t("settings_off")
            elif idx == 2:
                return t("lang_name_zh") if settings_mgr.language == "zh" else t("lang_name_en")
            elif idx == 3:
                return t("settings_on") if settings_mgr.music_enabled else t("settings_off")
            elif idx == 4:
                return f"{int(settings_mgr.music_volume * 100)}%"
            elif idx == 5:
                return t("settings_on") if settings_mgr.show_fps else t("settings_off")
            else:
                return t(f"diff_{settings_mgr.difficulty}")

        row_start = cy + 100
        row_h     = 48
        box_pad   = 16

        box_rect = pygame.Rect(
            cx - 260,
            row_start - box_pad,
            520,
            len(option_keys) * row_h + box_pad * 2,
        )
        pygame.draw.rect(surface, (28, 26, 34), box_rect, border_radius=8)
        pygame.draw.rect(surface, (70, 60, 85), box_rect, 1, border_radius=8)

        label_x = cx - 230
        arrow_x = cx + 10
        value_x = cx + 50

        for i, key in enumerate(option_keys):
            selected = (i == self._settings_sel)
            y = row_start + i * row_h

            if selected:
                hl = pygame.Rect(cx - 258, y - 8, 516, row_h - 6)
                pygame.draw.rect(surface, (48, 42, 62), hl, border_radius=5)

            color  = COLOR_ACCENT if selected else (190, 190, 190)
            marker = "> " if selected else "  "

            draw_text(surface, marker + t(key), label_x, y, font_sm, color)

            if selected:
                draw_text(surface, "< ", arrow_x, y, font_sm, COLOR_ACCENT)
                draw_text(surface, get_value(i), value_x, y, font_sm, COLOR_ACCENT)
                val_surf = get_font(FONT_UI_SM).render(get_value(i), False, COLOR_ACCENT)
                draw_text(surface, " >", value_x + val_surf.get_width(), y,
                          font_sm, COLOR_ACCENT)
            else:
                draw_text(surface, get_value(i), value_x, y, font_sm, (150, 150, 150))

        hint_y = row_start + len(option_keys) * row_h + box_pad + 14
        draw_text(surface, t("settings_nav_hint"), cx, hint_y,
                  font_sm, (90, 90, 90), center=True)

    def draw_pause(self, surface):
        font_big = get_font(FONT_UI_LG)
        font_md  = get_font(FONT_UI_MD)
        font_sm  = get_font(FONT_UI_SM)

        sw, sh = surface.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        cx = sw // 2
        cy = sh // 5

        draw_text(surface, t("paused"), cx, cy, font_big, COLOR_UI, center=True)

        item_h  = 52
        panel_w = 300
        panel_h = len(_PAUSE_ITEMS) * item_h + 24
        panel_x = cx - panel_w // 2
        panel_y = cy + 72

        pygame.draw.rect(surface, (28, 26, 34),
                         (panel_x, panel_y, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(surface, (70, 60, 85),
                         (panel_x, panel_y, panel_w, panel_h), 1, border_radius=8)

        for i, key in enumerate(_PAUSE_ITEMS):
            selected = (i == self._pause_sel)
            item_y   = panel_y + 12 + i * item_h

            if selected:
                hl = pygame.Rect(panel_x + 4, item_y - 4, panel_w - 8, item_h - 6)
                pygame.draw.rect(surface, (50, 44, 65), hl, border_radius=5)

            color  = COLOR_ACCENT if selected else (200, 200, 200)
            marker = ">  " if selected else "   "
            draw_text(surface, marker + t(key), cx, item_y + 6, font_md, color, center=True)

        draw_text(surface, t("menu_nav_hint"),
                  cx, panel_y + panel_h + 14, font_sm, (90, 90, 90), center=True)

    def draw_game_over(self, surface):
        font_big = get_font(FONT_UI_LG)
        font_sm  = get_font(FONT_UI_SM)

        sw, sh = surface.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        cx = sw // 2
        cy = sh // 3

        draw_text(surface, t("game_over"), cx, cy, font_big, COLOR_ACCENT, center=True)
        draw_text(surface, t("press_enter_restart"), cx, cy + 50,
                  font_sm, COLOR_UI, center=True)
