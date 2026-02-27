# ============================================================
#  Music system — procedural ambient BGM for Middle-earth RPG
#
#  Generates a WAV file once (assets/bgm_main.wav) using pure
#  Python math, then streams it via pygame.mixer.music.
#
#  Style: A minor pentatonic melody (flute-like overtones)
#         + A2/E2 organ drone — Celtic / Howard Shore inspired
# ============================================================
import math
import os
import wave
import array as _arr

_RATE = 22050  # Hz, mono 16-bit

_ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets"
)
_BGM_PATH = os.path.join(_ASSETS_DIR, "bgm_main.wav")

# ── Note frequencies (Hz) ──────────────────────────────────────────────────
_NOTES = {
    "G4": 392.00, "A4": 440.00, "C5": 523.25,
    "D5": 587.33, "E5": 659.25,
    "A2": 110.00, "E2":  82.41,
    "R":    0.00,
}


# ── Waveform helpers ───────────────────────────────────────────────────────

def _one_period(freq, harmonics):
    """Precompute one fundamental period as a list of floats in [-1, 1]."""
    period = max(1, int(_RATE / freq))
    inv_rate = 1.0 / _RATE
    tw = 2.0 * math.pi
    return [
        sum(math.sin(tw * freq * k * i * inv_rate) * a for k, a in harmonics)
        for i in range(period)
    ]


def _make_note(freq, n_samples, vol, atk_frac=0.10, rel_frac=0.20):
    """Tile one waveform period, apply ADSR envelope → list[int16]."""
    if freq == 0 or n_samples <= 0:
        return [0] * n_samples
    # Flute-like: strong fundamental + gentle upper harmonics
    harmonics = [(1, 0.75), (2, 0.18), (3, 0.07)]
    period = _one_period(freq, harmonics)
    plen = len(period)
    atk = max(1, int(n_samples * atk_frac))
    rel = max(1, int(n_samples * rel_frac))
    scale = vol * 32767.0
    result = []
    ap = result.append
    for i in range(n_samples):
        s = period[i % plen]
        if i < atk:
            env = i / atk
        elif i >= n_samples - rel:
            env = (n_samples - i) / rel
        else:
            env = 1.0
        ap(int(s * env * scale))
    return result


def _make_drone(n_total, freq, harmonics, vol):
    """Tile a drone waveform for full duration → list[int16]."""
    period = _one_period(freq, harmonics)
    plen = len(period)
    scale = vol * 32767.0
    return [int(period[i % plen] * scale) for i in range(n_total)]


# ── BGM composition ────────────────────────────────────────────────────────

def _generate_bgm():
    """
    Compose Middle-earth ambient loop and write to assets/bgm_main.wav.

    Structure (A minor pentatonic, ~19 s at 63 BPM):
      Phrase 1 — ascending motif  (bars 1-2)
      Phrase 2 — answering phrase (bars 3-4)
      Phrase 3 — climax + descent (bars 5-6)
      Coda      — resolves to A4  (bars 7-8)
    Background: A2 + E2 organ drone throughout.
    """
    BPM = 63
    beat = 60.0 / BPM  # seconds per beat

    # (note, beats) — A minor pentatonic: A G E D C
    seq = [
        # Phrase 1
        ("E5", 2.0), ("D5", 1.0), ("C5", 1.0),
        ("A4", 2.0), ("G4", 1.0), ("A4", 1.0),
        # Phrase 2
        ("C5", 1.5), ("D5", 0.5), ("E5", 2.0),
        ("D5", 1.5), ("C5", 0.5), ("A4", 2.0),
        # Phrase 3
        ("G4", 1.0), ("A4", 1.0), ("C5", 1.0), ("E5", 1.0),
        ("D5", 2.0), ("C5", 2.0),
        # Coda
        ("A4", 2.0), ("G4", 1.0), ("A4", 1.0),
        ("C5", 1.0), ("D5", 1.0), ("A4", 3.0),
        ("R",  1.0),
    ]

    # ── Build melody ────────────────────────────────────────────────────────
    melody = []
    for note, beats in seq:
        n = int(beats * beat * _RATE)
        melody.extend(_make_note(_NOTES.get(note, 0.0), n, vol=0.30))

    n_total = len(melody)

    # ── Build drone layers ──────────────────────────────────────────────────
    # A2: tonic drone (rich harmonics, organ-like)
    harm_a2 = [(1, 0.50), (2, 0.30), (3, 0.13), (4, 0.07)]
    # E2: perfect fifth below A2, adds depth
    harm_e2 = [(1, 0.55), (2, 0.28), (3, 0.12), (4, 0.05)]
    drone_a = _make_drone(n_total, _NOTES["A2"], harm_a2, vol=0.10)
    drone_e = _make_drone(n_total, _NOTES["E2"], harm_e2, vol=0.07)

    # ── Mix + fade in/out for clean looping ─────────────────────────────────
    fade = min(int(0.35 * _RATE), n_total // 12)
    mixed = _arr.array("h")
    ap = mixed.append
    for i in range(n_total):
        v = melody[i] + drone_a[i] + drone_e[i]
        if i < fade:
            v = int(v * i / fade)
        elif i > n_total - fade:
            v = int(v * (n_total - i) / fade)
        ap(max(-32767, min(32767, v)))

    # ── Write WAV ───────────────────────────────────────────────────────────
    os.makedirs(_ASSETS_DIR, exist_ok=True)
    with wave.open(_BGM_PATH, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(_RATE)
        wf.writeframes(mixed.tobytes())


# ── MusicManager ───────────────────────────────────────────────────────────

class MusicManager:
    """Manages background music playback using pygame.mixer.music."""

    def __init__(self):
        self._ready = False
        self._enabled = True
        self._volume = 0.55
        self._setup()

    def _setup(self):
        try:
            import pygame
            if not os.path.exists(_BGM_PATH):
                from core.logger import get_logger
                get_logger("music").info("Generating background music (first run)…")
                _generate_bgm()
            self._ready = True
        except Exception as exc:
            try:
                from core.logger import get_logger
                get_logger("music").warning("Music init failed: %s", exc)
            except Exception:
                pass

    def play(self):
        """Start playing (or resume) background music."""
        if not self._ready or not self._enabled:
            return
        try:
            import pygame
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(_BGM_PATH)
                pygame.mixer.music.set_volume(self._volume)
                pygame.mixer.music.play(-1)  # loop forever
        except Exception:
            pass

    def stop(self):
        """Stop background music."""
        try:
            import pygame
            pygame.mixer.music.stop()
        except Exception:
            pass

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        if enabled:
            self.play()
        else:
            self.stop()

    @property
    def enabled(self):
        return self._enabled
