# ============================================================
#  Music system — procedural zone & combat BGM
#
#  7 distinct tracks generated as WAV files (cached to disk):
#    bgm_shire      → Shire / Hobbiton  (warm, joyful)
#    bgm_elven      → Rivendell / Lothlórien  (ethereal, Dorian)
#    bgm_wilderness → Weathertop / Fangorn / Misty Mts  (tense, brooding)
#    bgm_moria      → Moria / Dead Marshes / Osgiliath  (dark, oppressive)
#    bgm_rohan      → Rohan / Anduin  (heroic, galloping)
#    bgm_mordor     → Mordor / Mount Doom  (menacing, chromatic)
#    bgm_combat     → any combat  (aggressive, percussion-driven)
#
#  Each track is ~10-16 s and loops seamlessly.
# ============================================================
import math
import os
import random as _rnd
import wave
import array as _arr

_RATE = 22050  # Hz, mono 16-bit

_ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets"
)

# ── Zone → track mapping ───────────────────────────────────────────────────
ZONE_TRACKS = {
    "shire":        "bgm_shire",
    "hobbiton":     "bgm_shire",
    "rivendell":    "bgm_elven",
    "lothlorien":   "bgm_elven",
    "weathertop":   "bgm_wilderness",
    "fangorn":      "bgm_wilderness",
    "misty_mts":    "bgm_wilderness",
    "moria":        "bgm_moria",
    "dead_marshes": "bgm_moria",
    "osgiliath":    "bgm_moria",
    "rohan_west":   "bgm_rohan",
    "rohan_center": "bgm_rohan",
    "rohan_east":   "bgm_rohan",
    "anduin":       "bgm_rohan",
    "mordor":       "bgm_mordor",
    "mount_doom":   "bgm_mordor",
}

_TRACK_FILES = {k: os.path.join(_ASSETS_DIR, f"{k}.wav") for k in [
    "bgm_shire", "bgm_elven", "bgm_wilderness",
    "bgm_moria", "bgm_rohan", "bgm_mordor", "bgm_combat",
]}

# ── Note table (Hz) ───────────────────────────────────────────────────────
_N = {
    "A1": 55.00,  "E1": 41.20,
    "C2": 65.41,  "D2": 73.42,  "E2": 82.41,  "F2": 87.31,
    "Gb2": 92.50, "G2": 98.00,  "A2": 110.00, "B2": 123.47,
    "C3": 130.81, "D3": 146.83, "E3": 164.81, "F3": 174.61,
    "Gb3": 185.00,"G3": 196.00, "Ab3": 207.65,"A3": 220.00,
    "Bb3": 233.08,"B3": 246.94,
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23,
    "Fs4": 369.99,"G4": 392.00, "A4": 440.00, "Bb4": 466.16,
    "B4": 493.88,
    "C5": 523.25, "Cs5": 554.37,"D5": 587.33, "E5": 659.25,
    "F5": 698.46, "G5": 783.99, "A5": 880.00,
    "R":  0.00,
}

# ── Timbre presets (harmonics = list of (overtone_k, amplitude)) ──────────
_FLUTE  = [(1, 0.70), (2, 0.20), (3, 0.08), (4, 0.02)]
_BELL   = [(1, 0.55), (2, 0.32), (3, 0.10), (4, 0.03)]
_OBOE   = [(1, 0.55), (3, 0.28), (5, 0.12), (7, 0.05)]
_HOLLOW = [(1, 0.70), (2, 0.08), (3, 0.18), (5, 0.04)]
_HORN   = [(1, 0.50), (2, 0.30), (3, 0.14), (4, 0.06)]
_SAW    = [(1, 0.42), (2, 0.22), (3, 0.16), (4, 0.11), (5, 0.09)]
_SQUARE = [(1, 0.50), (3, 0.25), (5, 0.15), (7, 0.10)]
_WARM   = [(1, 0.50), (2, 0.32), (3, 0.13), (4, 0.05)]
_DEEP   = [(1, 0.60), (2, 0.25), (3, 0.10), (4, 0.05)]


# ── Waveform helpers ───────────────────────────────────────────────────────

def _one_period(freq, harmonics):
    n = max(1, int(_RATE / freq))
    inv = 1.0 / _RATE
    tw = 2.0 * math.pi
    return [
        sum(math.sin(tw * freq * k * i * inv) * a for k, a in harmonics)
        for i in range(n)
    ]


def _make_note(freq, n_samp, vol, harmonics, atk=0.08, rel=0.25):
    if freq == 0 or n_samp <= 0:
        return [0] * n_samp
    period = _one_period(freq, harmonics)
    plen = len(period)
    atk_s = max(1, int(n_samp * atk))
    rel_s = max(1, int(n_samp * rel))
    scale = vol * 32767.0
    out = []
    ap = out.append
    for i in range(n_samp):
        s = period[i % plen]
        if i < atk_s:
            env = i / atk_s
        elif i >= n_samp - rel_s:
            env = (n_samp - i) / rel_s
        else:
            env = 1.0
        ap(int(s * env * scale))
    return out


def _make_drone(n_total, freq, harmonics, vol):
    period = _one_period(freq, harmonics)
    plen = len(period)
    scale = vol * 32767.0
    return [int(period[i % plen] * scale) for i in range(n_total)]


def _make_noise_burst(n_samp, vol, rel_frac=0.80, seed=0):
    """Short percussive noise burst."""
    rng = _rnd.Random(seed)
    rel_s = max(1, int(n_samp * rel_frac))
    scale = vol * 32767.0
    out = []
    for i in range(n_samp):
        s = rng.uniform(-1.0, 1.0)
        env = 1.0 if i < n_samp - rel_s else (n_samp - i) / rel_s
        out.append(int(s * env * scale))
    return out


def _make_percussion(n_total, beat_samp, pattern, vol=0.16):
    """
    pattern: list of (beat_float, vol_multiplier)
    Lays noise bursts at the given beat positions.
    """
    result = [0] * n_total
    burst_len = max(1, beat_samp // 5)
    for beat_f, v_mul in pattern:
        start = int(round(beat_f * beat_samp))
        burst = _make_noise_burst(burst_len, vol * v_mul, seed=int(beat_f * 100))
        for j, s in enumerate(burst):
            idx = start + j
            if idx < n_total:
                result[idx] += s
    return result


def _compose_and_write(path, seq, bpm, harmonics, drone_specs,
                       vol_melody=0.28, add_perc=False, perc_vol=0.15):
    """
    Build a looping track from a note sequence and write to WAV.
      seq         — list of (note_name, beats)
      drone_specs — list of (freq, harmonics, vol)
    """
    beat = 60.0 / bpm
    beat_samp = int(beat * _RATE)

    # Melody
    melody = []
    for note, beats in seq:
        n = max(1, int(beats * beat * _RATE))
        melody.extend(_make_note(_N.get(note, 0.0), n, vol_melody, harmonics))
    n_total = len(melody)

    layers = [melody]

    # Drones
    for freq, harm, vol in drone_specs:
        layers.append(_make_drone(n_total, freq, harm, vol))

    # Percussion (combat only)
    if add_perc:
        total_beats = n_total / beat_samp
        pattern = []
        t = 0.0
        while t < total_beats:
            beat_in_bar = int(t) % 4
            if beat_in_bar in (0, 2):
                pattern.append((t, 1.0))        # kick
            else:
                pattern.append((t, 0.70))       # snare
            if t + 0.5 < total_beats:
                pattern.append((t + 0.5, 0.28)) # hi-hat
            t += 1.0
        layers.append(_make_percussion(n_total, beat_samp, pattern, perc_vol))

    # Mix + symmetric fade for clean looping
    fade = min(int(0.40 * _RATE), n_total // 10)
    mixed = _arr.array("h")
    ap = mixed.append
    for i in range(n_total):
        v = sum(layer[i] for layer in layers)
        if i < fade:
            v = int(v * i / fade)
        elif i > n_total - fade:
            v = int(v * (n_total - i) / fade)
        ap(max(-32767, min(32767, v)))

    os.makedirs(_ASSETS_DIR, exist_ok=True)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(_RATE)
        wf.writeframes(mixed.tobytes())


# ── Individual track generators ────────────────────────────────────────────

def _gen_shire(path):
    """Shire / Hobbiton — C major pentatonic, warm flute, joyful & bouncy."""
    seq = [
        ("G4", 1.0), ("A4", 0.5), ("C5", 0.5), ("E5", 1.5), ("D5", 0.5),
        ("C5", 1.0), ("A4", 1.0),
        ("E5", 0.5), ("D5", 0.5), ("C5", 0.5), ("A4", 0.5),
        ("G4", 1.0), ("A4", 0.5), ("C5", 0.5),
        ("E5", 1.5), ("D5", 0.5), ("C5", 1.0),
        ("G4", 1.5), ("A4", 0.5), ("C5", 2.0),
        ("R",  1.0),
    ]
    _compose_and_write(path, seq, bpm=72, harmonics=_FLUTE,
                       drone_specs=[(_N["G2"], _WARM, 0.09),
                                    (_N["C2"], _WARM, 0.06)],
                       vol_melody=0.30)


def _gen_elven(path):
    """Rivendell / Lothlórien — E Dorian, crystal bell timbre, ethereal."""
    seq = [
        ("E5",  2.5), ("D5",  1.5), ("B4",  2.0), ("A4",  1.0),
        ("Fs4", 1.0), ("A4",  1.0), ("B4",  1.5), ("Cs5", 0.5),
        ("D5",  1.0), ("E5",  2.5), ("R",   1.0),
        ("Cs5", 1.0), ("B4",  1.5), ("A4",  0.5),
        ("Fs4", 1.5), ("E5",  2.0), ("R",   1.5),
    ]
    _compose_and_write(path, seq, bpm=52, harmonics=_BELL,
                       drone_specs=[(_N["E2"], _BELL,  0.08),
                                    (_N["B2"], _WARM,  0.06)],
                       vol_melody=0.26)


def _gen_wilderness(path):
    """Weathertop / Fangorn / Misty Mts — D minor, oboe, brooding tension."""
    seq = [
        ("D4", 2.0), ("F4", 1.0), ("G4", 1.0), ("A4", 2.0),
        ("C5", 1.5), ("A4", 0.5),
        ("D5", 1.0), ("C5", 1.0), ("A4", 1.0), ("F4", 1.0),
        ("G4", 2.0), ("D4", 1.5),
        ("A4", 0.5), ("C5", 0.5), ("D5", 1.5), ("C5", 0.5),
        ("A4", 1.0), ("F4", 1.5), ("D4", 1.5), ("R", 0.5),
    ]
    _compose_and_write(path, seq, bpm=63, harmonics=_OBOE,
                       drone_specs=[(_N["D2"], _DEEP, 0.10),
                                    (_N["A2"], _DEEP, 0.07)],
                       vol_melody=0.28)


def _gen_moria(path):
    """Moria / Dead Marshes — A Phrygian, hollow cave timbre, very slow."""
    seq = [
        ("E4",  3.0), ("D4",  2.0), ("C4",  3.0),
        ("Bb3", 2.0), ("A3",  4.0), ("R",   2.0),
        ("C4",  2.5), ("D4",  2.5), ("Bb3", 3.0),
        ("A3",  5.0), ("R",   2.0),
        ("E4",  2.0), ("C4",  2.0), ("A3",  4.0),
    ]
    _compose_and_write(path, seq, bpm=38, harmonics=_HOLLOW,
                       drone_specs=[(_N["A1"], _DEEP,   0.12),
                                    (_N["E2"], _HOLLOW, 0.05)],
                       vol_melody=0.24)


def _gen_rohan(path):
    """Rohan / Anduin — G major pentatonic, brass horn, triumphant."""
    seq = [
        ("G4", 0.5), ("B4", 0.5), ("D5", 1.0), ("G5", 2.0),
        ("E5", 1.0), ("D5", 1.0),
        ("B4", 0.5), ("D5", 0.5), ("E5", 1.5), ("D5", 0.5),
        ("B4", 1.0), ("A4", 1.5), ("G4", 0.5),
        ("G4", 0.5), ("A4", 0.5), ("B4", 0.5), ("D5", 0.5),
        ("E5", 1.0), ("G5", 2.0), ("D5", 1.0), ("B4", 2.0),
        ("R",  1.0),
    ]
    _compose_and_write(path, seq, bpm=84, harmonics=_HORN,
                       drone_specs=[(_N["G2"], _WARM, 0.10),
                                    (_N["D2"], _HORN, 0.07)],
                       vol_melody=0.28)


def _gen_mordor(path):
    """Mordor / Mount Doom — chromatic descent, sawtooth, tritone drone."""
    seq = [
        ("A3",  4.0), ("Ab3", 3.0), ("G3",  4.0), ("Gb3", 3.0),
        ("F3",  4.0), ("E3",  3.0), ("F3",  2.0), ("Ab3", 2.0),
        ("A3",  4.0), ("R",   2.0),
        ("G3",  3.0), ("F3",  3.0), ("E3",  3.0), ("A3",  4.0),
        ("R",   2.0),
    ]
    _compose_and_write(path, seq, bpm=42, harmonics=_SAW,
                       drone_specs=[(_N["A1"],  _DEEP, 0.13),
                                    (_N["Gb2"], _SAW,  0.06)],  # tritone
                       vol_melody=0.26)


def _gen_combat(path):
    """Combat — A minor, staccato square wave + kick/snare/hi-hat."""
    seq = [
        # Charge
        ("A4", 0.5), ("C5", 0.5), ("E5", 0.5), ("A4", 0.5),
        ("C5", 0.5), ("D5", 0.5), ("E5", 0.5), ("G5", 0.5),
        # Press
        ("A5", 1.0), ("G5", 0.5), ("E5", 0.5),
        ("D5", 0.5), ("C5", 0.5), ("A4", 1.0),
        # Fury
        ("E5", 0.25), ("D5", 0.25), ("C5", 0.25), ("E5", 0.25),
        ("A4", 0.5),  ("C5", 0.5),  ("E5", 0.5),  ("D5", 0.5),
        # Resolve
        ("G5", 0.5), ("E5", 0.5), ("C5", 0.5), ("A4", 0.5),
        ("E5", 2.0), ("R",  0.5),
    ]
    _compose_and_write(path, seq, bpm=128, harmonics=_SQUARE,
                       drone_specs=[(_N["A2"], _SQUARE, 0.08)],
                       vol_melody=0.26, add_perc=True, perc_vol=0.15)


# ── Generator dispatch ─────────────────────────────────────────────────────
_TRACK_GENERATORS = {
    "bgm_shire":      _gen_shire,
    "bgm_elven":      _gen_elven,
    "bgm_wilderness": _gen_wilderness,
    "bgm_moria":      _gen_moria,
    "bgm_rohan":      _gen_rohan,
    "bgm_mordor":     _gen_mordor,
    "bgm_combat":     _gen_combat,
}


# ── MusicManager ───────────────────────────────────────────────────────────

class MusicManager:
    """Zone-aware + combat-aware background music manager."""

    def __init__(self):
        self._ready = False
        self._enabled = True
        self._volume = 0.55
        self._current_track = None   # track name currently loaded/playing
        self._zone_track = "bgm_shire"  # last zone track (resumed after combat)
        self._setup()

    def _setup(self):
        try:
            import pygame  # noqa: F401 — confirm pygame is available
            self._ready = True
            # Generate tracks that are missing (lazy, on first switch)
        except Exception as exc:
            try:
                from core.logger import get_logger
                get_logger("music").warning("Music init failed: %s", exc)
            except Exception:
                pass

    def _ensure_generated(self, track_name):
        """Generate the WAV for track_name if it doesn't exist yet."""
        path = _TRACK_FILES.get(track_name)
        if not path:
            return
        if os.path.exists(path):
            return
        try:
            from core.logger import get_logger
            get_logger("music").info("Generating %s …", track_name)
        except Exception:
            pass
        try:
            _TRACK_GENERATORS[track_name](path)
        except Exception as exc:
            try:
                from core.logger import get_logger
                get_logger("music").warning("Failed to generate %s: %s", track_name, exc)
            except Exception:
                pass

    def _switch_to(self, track_name):
        """Load and play track_name (no-op if already playing it)."""
        if not self._ready or not self._enabled:
            return
        if self._current_track == track_name:
            return
        self._ensure_generated(track_name)
        path = _TRACK_FILES.get(track_name)
        if not path or not os.path.exists(path):
            return
        try:
            import pygame
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self._volume)
            pygame.mixer.music.play(-1)
            self._current_track = track_name
        except Exception:
            pass

    # ── Public API ──────────────────────────────────────────────────────────

    def play_zone(self, zone_id: str):
        """Switch to the music track appropriate for the given zone."""
        track = ZONE_TRACKS.get(zone_id, "bgm_shire")
        self._zone_track = track
        self._switch_to(track)

    def play_combat(self):
        """Switch to the aggressive combat track."""
        self._switch_to("bgm_combat")

    def resume_zone(self):
        """Return to zone music after combat ends."""
        self._switch_to(self._zone_track)

    def play(self):
        """Play default (menu / shire) music — used before any zone is loaded."""
        self._switch_to(self._zone_track)

    def stop(self):
        try:
            import pygame
            pygame.mixer.music.stop()
            self._current_track = None
        except Exception:
            pass

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        if enabled:
            self.play()
        else:
            self.stop()

    def set_volume(self, v: float):
        self._volume = max(0.0, min(1.0, v))
        try:
            import pygame
            pygame.mixer.music.set_volume(self._volume)
        except Exception:
            pass

    @property
    def enabled(self):
        return self._enabled
