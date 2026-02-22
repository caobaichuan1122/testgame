"""
Generate Middle-earth themed pixel-art spritesheets for the game.
Run once:  python generate_sprites.py
Then start the game normally:  python main.py
"""
import os
import random
import pygame

pygame.init()

ASSETS = os.path.join(os.path.dirname(__file__), "assets")


def put(surf, x, y, color):
    """Safe pixel put."""
    if 0 <= x < surf.get_width() and 0 <= y < surf.get_height():
        surf.set_at((x, y), color)


def rect(surf, x, y, w, h, color):
    for dy in range(h):
        for dx in range(w):
            put(surf, x + dx, y + dy, color)


def mirror_h(surf):
    """Return horizontally mirrored copy."""
    return pygame.transform.flip(surf, True, False)


# ============================================================
#  Player spritesheet: 32x32 per frame (Ranger of the North)
#  Row 0: idle (4 frames — breathing animation)
#  Row 1: walk (6 frames)
# ============================================================
def gen_player():
    frame_w, frame_h = 32, 32
    cols_idle, cols_walk = 4, 6
    total_cols = max(cols_idle, cols_walk)
    sheet = pygame.Surface((total_cols * frame_w, 2 * frame_h), pygame.SRCALPHA)

    skin = (220, 185, 145)
    hair = (45, 35, 25)
    cloak = (55, 70, 50)        # Ranger green
    cloak_dark = (40, 55, 38)
    tunic = (75, 65, 55)        # Weathered brown
    tunic_dark = (55, 48, 40)
    pants = (50, 50, 45)
    pants_dark = (35, 35, 30)
    boots = (70, 50, 35)
    eye = (30, 40, 50)
    belt = (50, 40, 30)

    def draw_char(f, body_offset_y=0, leg_phase=0):
        """Draw one character frame onto surface f (32x32)."""
        cx = 16  # center x

        # -- boots --
        if leg_phase == 0:
            rect(f, cx - 4, 27 + body_offset_y, 3, 3, boots)
            rect(f, cx + 1, 27 + body_offset_y, 3, 3, boots)
        elif leg_phase == 1:  # left forward
            rect(f, cx - 5, 26 + body_offset_y, 3, 3, boots)
            rect(f, cx + 2, 28 + body_offset_y, 3, 3, boots)
        elif leg_phase == 2:  # right forward
            rect(f, cx - 4, 28 + body_offset_y, 3, 3, boots)
            rect(f, cx + 3, 26 + body_offset_y, 3, 3, boots)
        elif leg_phase == 3:  # together
            rect(f, cx - 3, 27 + body_offset_y, 3, 3, boots)
            rect(f, cx + 0, 27 + body_offset_y, 3, 3, boots)

        # -- pants / legs --
        rect(f, cx - 4, 22 + body_offset_y, 3, 5, pants)
        rect(f, cx + 1, 22 + body_offset_y, 3, 5, pants_dark)

        # -- tunic / torso --
        rect(f, cx - 5, 14 + body_offset_y, 10, 8, tunic)
        rect(f, cx + 2, 14 + body_offset_y, 3, 8, tunic_dark)
        # belt
        rect(f, cx - 5, 21 + body_offset_y, 10, 1, belt)

        # -- cloak over shoulders --
        rect(f, cx - 7, 13 + body_offset_y, 2, 8, cloak)
        rect(f, cx + 5, 13 + body_offset_y, 2, 8, cloak_dark)
        # cloak tail
        rect(f, cx - 6, 21 + body_offset_y, 1, 5, cloak_dark)
        rect(f, cx + 6, 21 + body_offset_y, 1, 5, cloak_dark)

        # -- arms --
        rect(f, cx - 7, 15 + body_offset_y, 2, 6, tunic)
        rect(f, cx + 5, 15 + body_offset_y, 2, 6, tunic_dark)
        # hands
        rect(f, cx - 7, 21 + body_offset_y, 2, 2, skin)
        rect(f, cx + 5, 21 + body_offset_y, 2, 2, skin)

        # -- head --
        head_y = 5 + body_offset_y
        rect(f, cx - 4, head_y, 8, 9, skin)
        # hair
        rect(f, cx - 5, head_y - 1, 10, 3, hair)
        rect(f, cx - 5, head_y + 2, 2, 3, hair)  # left sideburn
        rect(f, cx + 3, head_y + 2, 2, 3, hair)  # right sideburn
        # eyes
        put(f, cx - 2, head_y + 4, eye)
        put(f, cx + 2, head_y + 4, eye)
        # mouth
        put(f, cx, head_y + 6, (180, 120, 100))

    # Row 0: idle — slight breathing bob
    for i in range(cols_idle):
        frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        bob = -1 if i in (1, 2) else 0
        draw_char(frame, body_offset_y=bob, leg_phase=0)
        sheet.blit(frame, (i * frame_w, 0))

    # Row 1: walk — 6-frame cycle
    walk_legs = [0, 1, 1, 0, 2, 2]
    walk_bob =  [0, -1, 0, 0, -1, 0]
    for i in range(cols_walk):
        frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        draw_char(frame, body_offset_y=walk_bob[i], leg_phase=walk_legs[i])
        sheet.blit(frame, (i * frame_w, frame_h))

    path = os.path.join(ASSETS, "player", "player.png")
    pygame.image.save(sheet, path)
    print(f"  Saved {path}  ({sheet.get_width()}x{sheet.get_height()})")


# ============================================================
#  Orc enemy: 16x16 per frame (dark green/brown brutish)
#  Row 0: idle (4 frames)
#  Row 1: walk (4 frames)
# ============================================================
def gen_orc():
    fw, fh = 16, 16
    cols = 4
    sheet = pygame.Surface((cols * fw, 2 * fh), pygame.SRCALPHA)

    skin = (75, 95, 55)         # Dark olive green
    skin_dark = (55, 70, 40)
    armor = (60, 50, 40)        # Crude leather
    armor_dark = (45, 38, 30)
    eye = (200, 60, 30)         # Red eyes
    tusk = (200, 190, 160)
    loincloth = (80, 60, 40)

    def draw_orc(f, bob=0, leg_phase=0):
        cx = 8
        # head - brutish, wide
        rect(f, cx - 3, 2 + bob, 7, 5, skin)
        rect(f, cx - 2, 1 + bob, 5, 1, skin_dark)  # brow ridge
        # eyes
        put(f, cx - 1, 4 + bob, eye)
        put(f, cx + 2, 4 + bob, eye)
        # tusks
        put(f, cx - 1, 6 + bob, tusk)
        put(f, cx + 2, 6 + bob, tusk)
        # ears
        put(f, cx - 4, 3 + bob, skin_dark)
        put(f, cx + 4, 3 + bob, skin_dark)

        # body - armored
        rect(f, cx - 3, 7 + bob, 7, 5, armor)
        rect(f, cx, 7 + bob, 3, 5, armor_dark)
        # belt
        rect(f, cx - 3, 11 + bob, 7, 1, loincloth)

        # arms
        rect(f, cx - 5, 8 + bob, 2, 4, skin)
        rect(f, cx + 4, 8 + bob, 2, 4, skin_dark)

        # legs
        if leg_phase == 0:
            rect(f, cx - 3, 12 + bob, 3, 3, skin)
            rect(f, cx + 1, 12 + bob, 3, 3, skin_dark)
        else:
            rect(f, cx - 4, 12 + bob, 3, 3, skin)
            rect(f, cx + 2, 12 + bob, 3, 3, skin_dark)

    # idle
    for i in range(cols):
        f = pygame.Surface((fw, fh), pygame.SRCALPHA)
        draw_orc(f, bob=(-1 if i in (1, 2) else 0))
        sheet.blit(f, (i * fw, 0))

    # walk
    legs = [0, 1, 0, 1]
    bobs = [0, -1, 0, -1]
    for i in range(cols):
        f = pygame.Surface((fw, fh), pygame.SRCALPHA)
        draw_orc(f, bob=bobs[i], leg_phase=legs[i])
        sheet.blit(f, (i * fw, fh))

    path = os.path.join(ASSETS, "enemies", "orc.png")
    pygame.image.save(sheet, path)
    print(f"  Saved {path}  ({sheet.get_width()}x{sheet.get_height()})")


# ============================================================
#  Barrow-wight enemy: 16x16 per frame (ghostly pale undead)
# ============================================================
def gen_wight():
    fw, fh = 16, 16
    cols = 4
    sheet = pygame.Surface((cols * fw, 2 * fh), pygame.SRCALPHA)

    shroud = (140, 150, 160)
    shroud_dark = (100, 110, 125)
    glow = (180, 200, 220)
    eye = (100, 180, 220)       # Icy blue eyes
    bone = (180, 175, 165)

    def draw_wight(f, bob=0, arm_phase=0, hover=0):
        cx = 8
        # ghostly shroud / body (flowing robe)
        rect(f, cx - 4, 7 + bob + hover, 8, 7, shroud)
        rect(f, cx, 7 + bob + hover, 4, 7, shroud_dark)
        # shroud bottom - ragged
        put(f, cx - 4, 14 + bob + hover, shroud_dark)
        put(f, cx - 2, 14 + bob + hover, shroud)
        put(f, cx + 1, 14 + bob + hover, shroud_dark)
        put(f, cx + 3, 14 + bob + hover, shroud)

        # skull head
        rect(f, cx - 3, 2 + bob + hover, 6, 5, bone)
        rect(f, cx - 2, 1 + bob + hover, 4, 1, bone)  # top
        # hollow eyes (glowing)
        rect(f, cx - 2, 4 + bob + hover, 2, 1, eye)
        rect(f, cx + 1, 4 + bob + hover, 2, 1, eye)
        # jaw
        rect(f, cx - 2, 6 + bob + hover, 4, 1, (150, 145, 135))

        # arms
        if arm_phase == 0:
            rect(f, cx - 6, 8 + bob + hover, 2, 4, shroud)
            rect(f, cx + 4, 8 + bob + hover, 2, 4, shroud_dark)
        else:
            rect(f, cx - 6, 7 + bob + hover, 2, 4, shroud)
            rect(f, cx + 4, 9 + bob + hover, 2, 4, shroud_dark)
        # bony hands
        put(f, cx - 6, 12 + bob + hover, bone)
        put(f, cx + 5, 12 + bob + hover, bone)

        # ghostly glow aura
        for yy in range(2 + bob + hover, 14 + bob + hover):
            put(f, cx - 5, yy, (*glow, 50))
            put(f, cx + 5, yy, (*glow, 50))

    # idle - floating
    hovers = [0, -1, -1, 0]
    for i in range(cols):
        f = pygame.Surface((fw, fh), pygame.SRCALPHA)
        draw_wight(f, hover=hovers[i])
        sheet.blit(f, (i * fw, 0))

    # walk - drifting
    hovers_w = [0, -1, -2, -1]
    arms = [0, 1, 0, 1]
    for i in range(cols):
        f = pygame.Surface((fw, fh), pygame.SRCALPHA)
        draw_wight(f, hover=hovers_w[i], arm_phase=arms[i])
        sheet.blit(f, (i * fw, fh))

    path = os.path.join(ASSETS, "enemies", "wight.png")
    pygame.image.save(sheet, path)
    print(f"  Saved {path}  ({sheet.get_width()}x{sheet.get_height()})")


# ============================================================
#  Uruk-hai Archer: 16x16 (dark, armored, with bow)
# ============================================================
def gen_uruk():
    fw, fh = 16, 16
    cols = 4
    sheet = pygame.Surface((cols * fw, 2 * fh), pygame.SRCALPHA)

    skin = (85, 65, 45)         # Dark brown
    skin_dark = (60, 45, 30)
    armor = (40, 35, 30)        # Near-black iron armor
    armor_dark = (28, 24, 20)
    eye = (220, 180, 40)        # Yellow eyes
    helmet = (50, 45, 40)
    bow = (100, 70, 35)
    white_hand = (200, 200, 200)  # White Hand of Saruman

    def draw_uruk(f, bob=0, leg_phase=0):
        cx = 8
        # helmet / head
        rect(f, cx - 3, 2 + bob, 6, 3, helmet)
        rect(f, cx - 3, 5 + bob, 6, 3, skin)
        # visor slit / eyes
        put(f, cx - 1, 4 + bob, eye)
        put(f, cx + 1, 4 + bob, eye)
        # chin
        put(f, cx, 7 + bob, skin_dark)

        # body - heavy armor
        rect(f, cx - 3, 8 + bob, 7, 4, armor)
        rect(f, cx, 8 + bob, 3, 4, armor_dark)
        # White Hand emblem
        put(f, cx - 1, 9 + bob, white_hand)
        put(f, cx, 9 + bob, white_hand)
        put(f, cx, 10 + bob, white_hand)

        # bow (right hand)
        rect(f, cx + 4, 5 + bob, 1, 8, bow)
        put(f, cx + 5, 5 + bob, bow)
        put(f, cx + 5, 12 + bob, bow)

        # left arm
        rect(f, cx - 5, 9 + bob, 2, 3, armor)

        # legs
        if leg_phase == 0:
            rect(f, cx - 3, 12 + bob, 3, 3, armor)
            rect(f, cx + 1, 12 + bob, 3, 3, armor_dark)
        else:
            rect(f, cx - 4, 12 + bob, 3, 3, armor)
            rect(f, cx + 2, 12 + bob, 3, 3, armor_dark)

    for i in range(cols):
        f = pygame.Surface((fw, fh), pygame.SRCALPHA)
        draw_uruk(f, bob=(-1 if i in (1, 2) else 0))
        sheet.blit(f, (i * fw, 0))

    legs = [0, 1, 0, 1]
    bobs = [0, -1, 0, -1]
    for i in range(cols):
        f = pygame.Surface((fw, fh), pygame.SRCALPHA)
        draw_uruk(f, bob=bobs[i], leg_phase=legs[i])
        sheet.blit(f, (i * fw, fh))

    path = os.path.join(ASSETS, "enemies", "uruk.png")
    pygame.image.save(sheet, path)
    print(f"  Saved {path}  ({sheet.get_width()}x{sheet.get_height()})")


# ============================================================
#  Cave Troll boss: 32x32 (earthy brown, massive)
# ============================================================
def gen_cave_troll():
    fw, fh = 32, 32
    cols = 4
    sheet = pygame.Surface((cols * fw, 2 * fh), pygame.SRCALPHA)

    skin = (110, 95, 75)        # Earthy brown-gray
    skin_dark = (80, 68, 55)
    skin_light = (135, 120, 100)
    eye = (180, 160, 40)        # Dull yellow
    teeth = (200, 190, 170)
    belly = (120, 105, 85)
    chain = (100, 100, 110)     # Moria chains

    def draw_troll(f, bob=0, arm_phase=0):
        cx = 16
        # massive body
        rect(f, cx - 8, 10 + bob, 16, 14, skin)
        rect(f, cx - 7, 8 + bob, 14, 2, skin)
        # shading
        rect(f, cx + 2, 10 + bob, 6, 14, skin_dark)
        # highlight
        rect(f, cx - 7, 10 + bob, 3, 5, skin_light)
        # belly
        rect(f, cx - 4, 14 + bob, 8, 6, belly)

        # scars / texture
        put(f, cx - 3, 15 + bob, skin_dark)
        put(f, cx - 2, 16 + bob, skin_dark)
        put(f, cx + 4, 13 + bob, skin_dark)
        put(f, cx + 5, 14 + bob, skin_dark)

        # chains around torso
        for x in range(cx - 6, cx + 7, 3):
            put(f, x, 11 + bob, chain)
            put(f, x + 1, 12 + bob, chain)

        # head - small for body
        rect(f, cx - 5, 3 + bob, 10, 7, skin)
        rect(f, cx - 4, 2 + bob, 8, 1, skin_dark)
        # heavy brow
        rect(f, cx - 4, 4 + bob, 9, 1, skin_dark)
        # eyes (small, dull)
        rect(f, cx - 3, 5 + bob, 2, 2, eye)
        rect(f, cx + 2, 5 + bob, 2, 2, eye)
        # wide mouth with teeth
        rect(f, cx - 3, 8 + bob, 7, 1, (60, 40, 30))
        put(f, cx - 2, 8 + bob, teeth)
        put(f, cx, 8 + bob, teeth)
        put(f, cx + 2, 8 + bob, teeth)

        # arms - massive
        ay = 11 + bob + (1 if arm_phase else 0)
        rect(f, cx - 12, ay, 4, 10, skin)
        rect(f, cx - 12, ay, 4, 3, skin_light)
        rect(f, cx + 8, ay, 4, 10, skin_dark)
        rect(f, cx + 8, ay, 4, 3, skin)
        # fists
        rect(f, cx - 13, ay + 10, 5, 3, skin_dark)
        rect(f, cx + 8, ay + 10, 5, 3, skin_dark)

        # legs
        rect(f, cx - 6, 24 + bob, 5, 6, skin_dark)
        rect(f, cx + 1, 24 + bob, 5, 6, skin_dark)
        rect(f, cx - 6, 24 + bob, 5, 2, skin)
        rect(f, cx + 1, 24 + bob, 5, 2, skin)

    for i in range(cols):
        f = pygame.Surface((fw, fh), pygame.SRCALPHA)
        draw_troll(f, bob=(-1 if i in (1, 2) else 0))
        sheet.blit(f, (i * fw, 0))

    arms = [0, 1, 0, 1]
    bobs = [0, -1, 0, -1]
    for i in range(cols):
        f = pygame.Surface((fw, fh), pygame.SRCALPHA)
        draw_troll(f, bob=bobs[i], arm_phase=arms[i])
        sheet.blit(f, (i * fw, fh))

    path = os.path.join(ASSETS, "enemies", "cave_troll.png")
    pygame.image.save(sheet, path)
    print(f"  Saved {path}  ({sheet.get_width()}x{sheet.get_height()})")


# ============================================================
#  NPC: Gandalf-style wizard (grey robes, hat): 16x16
# ============================================================
def gen_gandalf():
    fw, fh = 16, 16
    cols = 4
    sheet = pygame.Surface((cols * fw, fh), pygame.SRCALPHA)

    skin = (225, 190, 150)
    beard = (220, 215, 210)     # White/grey beard
    hat = (90, 85, 80)          # Grey hat
    robe = (130, 125, 120)      # Grey robes
    robe_dark = (95, 90, 85)
    staff = (140, 110, 60)      # Wooden staff
    eye = (50, 80, 130)

    def draw_gandalf(f, bob=0):
        cx = 8
        # pointy hat
        put(f, cx, 0 + bob, hat)
        rect(f, cx - 1, 1 + bob, 3, 1, hat)
        rect(f, cx - 2, 2 + bob, 5, 1, hat)
        # head
        rect(f, cx - 3, 3 + bob, 6, 4, skin)
        # eyes
        put(f, cx - 1, 4 + bob, eye)
        put(f, cx + 1, 4 + bob, eye)
        # beard
        rect(f, cx - 2, 6 + bob, 4, 3, beard)
        put(f, cx - 1, 9 + bob, beard)
        put(f, cx, 9 + bob, beard)

        # robe / body
        rect(f, cx - 3, 7 + bob, 6, 6, robe)
        rect(f, cx, 7 + bob, 3, 6, robe_dark)
        # feet
        rect(f, cx - 3, 13 + bob, 2, 2, (80, 55, 35))
        rect(f, cx + 1, 13 + bob, 2, 2, (80, 55, 35))

        # staff
        rect(f, cx + 4, 3 + bob, 1, 12, staff)
        put(f, cx + 4, 2 + bob, (220, 200, 140))  # glowing tip

        # arms
        rect(f, cx - 5, 8 + bob, 2, 3, robe)
        rect(f, cx + 3, 8 + bob, 2, 3, robe_dark)

    for i in range(cols):
        f = pygame.Surface((fw, fh), pygame.SRCALPHA)
        draw_gandalf(f, bob=(-1 if i in (1, 2) else 0))
        sheet.blit(f, (i * fw, 0))

    path = os.path.join(ASSETS, "npcs", "gandalf.png")
    pygame.image.save(sheet, path)
    print(f"  Saved {path}  ({sheet.get_width()}x{sheet.get_height()})")


# ============================================================
#  NPC: Hobbit (Barliman / Frodo / Sam style): 16x16
# ============================================================
def gen_hobbit():
    fw, fh = 16, 16
    cols = 4
    sheet = pygame.Surface((cols * fw, fh), pygame.SRCALPHA)

    skin = (230, 195, 155)
    hair = (120, 80, 40)        # Curly brown
    vest = (140, 90, 50)        # Earthy vest
    vest_dark = (110, 70, 35)
    shirt = (200, 190, 160)     # Linen shirt
    pants = (90, 110, 70)       # Green pants
    feet = (160, 130, 90)       # Big bare feet
    eye = (50, 60, 40)

    def draw_hobbit(f, bob=0):
        cx = 8
        # head (bigger relative to body - hobbits are short)
        rect(f, cx - 3, 3 + bob, 6, 5, skin)
        # curly hair
        rect(f, cx - 3, 2 + bob, 6, 2, hair)
        put(f, cx - 4, 3 + bob, hair)
        put(f, cx + 3, 3 + bob, hair)
        # eyes
        put(f, cx - 1, 5 + bob, eye)
        put(f, cx + 1, 5 + bob, eye)
        # rosy cheeks
        put(f, cx - 2, 6 + bob, (230, 170, 140))
        put(f, cx + 2, 6 + bob, (230, 170, 140))
        # smile
        put(f, cx, 7 + bob, (200, 140, 120))

        # vest over shirt
        rect(f, cx - 3, 8 + bob, 6, 4, vest)
        rect(f, cx - 1, 8 + bob, 2, 4, shirt)
        rect(f, cx + 1, 8 + bob, 2, 4, vest_dark)

        # pants
        rect(f, cx - 3, 12 + bob, 3, 2, pants)
        rect(f, cx + 0, 12 + bob, 3, 2, pants)

        # big bare feet
        rect(f, cx - 4, 14 + bob, 3, 1, feet)
        rect(f, cx + 1, 14 + bob, 3, 1, feet)

        # arms
        rect(f, cx - 5, 9 + bob, 2, 3, vest)
        rect(f, cx + 3, 9 + bob, 2, 3, vest_dark)

    for i in range(cols):
        f = pygame.Surface((fw, fh), pygame.SRCALPHA)
        draw_hobbit(f, bob=(-1 if i in (1, 2) else 0))
        sheet.blit(f, (i * fw, 0))

    path = os.path.join(ASSETS, "npcs", "hobbit.png")
    pygame.image.save(sheet, path)
    print(f"  Saved {path}  ({sheet.get_width()}x{sheet.get_height()})")


# ============================================================
#  NPC: Dwarf (Gimli style): 16x16
# ============================================================
def gen_dwarf():
    fw, fh = 16, 16
    cols = 4
    sheet = pygame.Surface((cols * fw, fh), pygame.SRCALPHA)

    skin = (220, 180, 140)
    beard = (160, 90, 40)       # Red-brown beard
    helmet = (150, 140, 130)    # Steel helmet
    armor = (130, 125, 120)     # Dwarven plate
    armor_dark = (95, 90, 85)
    boots = (80, 60, 40)
    eye = (40, 50, 60)

    def draw_dwarf(f, bob=0):
        cx = 8
        # helmet
        rect(f, cx - 3, 1 + bob, 6, 3, helmet)
        put(f, cx - 4, 2 + bob, helmet)
        put(f, cx + 3, 2 + bob, helmet)
        # face
        rect(f, cx - 3, 4 + bob, 6, 3, skin)
        # eyes
        put(f, cx - 1, 5 + bob, eye)
        put(f, cx + 1, 5 + bob, eye)
        # big beard
        rect(f, cx - 3, 6 + bob, 6, 3, beard)
        rect(f, cx - 2, 9 + bob, 4, 1, beard)
        put(f, cx, 10 + bob, beard)

        # stocky armored body
        rect(f, cx - 4, 7 + bob, 8, 5, armor)
        rect(f, cx, 7 + bob, 4, 5, armor_dark)

        # short legs with boots
        rect(f, cx - 3, 12 + bob, 3, 3, armor_dark)
        rect(f, cx + 1, 12 + bob, 3, 3, armor_dark)
        rect(f, cx - 3, 14 + bob, 3, 1, boots)
        rect(f, cx + 1, 14 + bob, 3, 1, boots)

        # arms
        rect(f, cx - 6, 8 + bob, 2, 4, armor)
        rect(f, cx + 4, 8 + bob, 2, 4, armor_dark)

    for i in range(cols):
        f = pygame.Surface((fw, fh), pygame.SRCALPHA)
        draw_dwarf(f, bob=(-1 if i in (1, 2) else 0))
        sheet.blit(f, (i * fw, 0))

    path = os.path.join(ASSETS, "npcs", "dwarf.png")
    pygame.image.save(sheet, path)
    print(f"  Saved {path}  ({sheet.get_width()}x{sheet.get_height()})")


# ============================================================
#  NPC: Elf (Arwen style): 16x16
# ============================================================
def gen_elf():
    fw, fh = 16, 16
    cols = 4
    sheet = pygame.Surface((cols * fw, fh), pygame.SRCALPHA)

    skin = (240, 220, 200)      # Fair
    hair = (40, 30, 25)         # Dark hair
    dress = (180, 190, 210)     # Light blue-silver
    dress_dark = (140, 150, 175)
    eye = (60, 100, 140)
    circlet = (220, 200, 140)   # Golden circlet

    def draw_elf(f, bob=0):
        cx = 8
        # head
        rect(f, cx - 3, 2 + bob, 6, 6, skin)
        # long dark hair
        rect(f, cx - 4, 1 + bob, 8, 2, hair)
        rect(f, cx - 4, 3 + bob, 1, 6, hair)
        rect(f, cx + 3, 3 + bob, 1, 6, hair)
        # pointed ears
        put(f, cx - 5, 4 + bob, skin)
        put(f, cx + 4, 4 + bob, skin)
        # circlet
        rect(f, cx - 2, 2 + bob, 5, 1, circlet)
        # eyes
        put(f, cx - 1, 5 + bob, eye)
        put(f, cx + 1, 5 + bob, eye)

        # elegant dress
        rect(f, cx - 3, 8 + bob, 6, 6, dress)
        rect(f, cx, 8 + bob, 3, 6, dress_dark)
        # flowing hem
        put(f, cx - 3, 14 + bob, dress_dark)
        put(f, cx + 2, 14 + bob, dress)

        # arms (slender)
        rect(f, cx - 5, 9 + bob, 2, 3, dress)
        rect(f, cx + 3, 9 + bob, 2, 3, dress_dark)

    for i in range(cols):
        f = pygame.Surface((fw, fh), pygame.SRCALPHA)
        draw_elf(f, bob=(-1 if i in (1, 2) else 0))
        sheet.blit(f, (i * fw, 0))

    path = os.path.join(ASSETS, "npcs", "elf.png")
    pygame.image.save(sheet, path)
    print(f"  Saved {path}  ({sheet.get_width()}x{sheet.get_height()})")


# ============================================================
#  NPC: Gondor Soldier (Boromir style): 16x16
# ============================================================
def gen_gondor():
    fw, fh = 16, 16
    cols = 4
    sheet = pygame.Surface((cols * fw, fh), pygame.SRCALPHA)

    skin = (220, 185, 150)
    hair = (60, 45, 30)
    armor = (170, 170, 180)     # Silver-steel armor
    armor_dark = (130, 130, 140)
    surcoat = (200, 200, 210)   # White surcoat
    tree = (100, 100, 110)      # White tree emblem (darker on white)
    boots = (70, 55, 40)
    eye = (40, 55, 70)

    def draw_gondor(f, bob=0):
        cx = 8
        # head
        rect(f, cx - 3, 2 + bob, 6, 5, skin)
        # hair
        rect(f, cx - 3, 1 + bob, 6, 2, hair)
        rect(f, cx - 3, 3 + bob, 1, 2, hair)
        rect(f, cx + 2, 3 + bob, 1, 2, hair)
        # eyes
        put(f, cx - 1, 4 + bob, eye)
        put(f, cx + 1, 4 + bob, eye)

        # armored torso with surcoat
        rect(f, cx - 3, 7 + bob, 6, 5, surcoat)
        rect(f, cx, 7 + bob, 3, 5, armor)
        # White Tree emblem
        put(f, cx - 1, 8 + bob, tree)
        put(f, cx - 1, 9 + bob, tree)
        put(f, cx - 2, 10 + bob, tree)
        put(f, cx, 10 + bob, tree)

        # legs with boots
        rect(f, cx - 3, 12 + bob, 3, 2, armor_dark)
        rect(f, cx + 1, 12 + bob, 3, 2, armor_dark)
        rect(f, cx - 3, 14 + bob, 3, 1, boots)
        rect(f, cx + 1, 14 + bob, 3, 1, boots)

        # arms
        rect(f, cx - 5, 8 + bob, 2, 3, armor)
        rect(f, cx + 3, 8 + bob, 2, 3, armor_dark)

    for i in range(cols):
        f = pygame.Surface((fw, fh), pygame.SRCALPHA)
        draw_gondor(f, bob=(-1 if i in (1, 2) else 0))
        sheet.blit(f, (i * fw, 0))

    path = os.path.join(ASSETS, "npcs", "gondor.png")
    pygame.image.save(sheet, path)
    print(f"  Saved {path}  ({sheet.get_width()}x{sheet.get_height()})")


# ============================================================
#  Projectiles: arrow.png, magic_bolt.png (single images)
# ============================================================
def gen_projectiles():
    # Arrow: 8x8 (Elven arrow)
    arrow = pygame.Surface((8, 8), pygame.SRCALPHA)
    shaft = (180, 160, 100)
    tip = (200, 200, 210)
    fletch = (80, 120, 60)     # Green fletching
    rect(arrow, 1, 3, 5, 2, shaft)
    rect(arrow, 6, 2, 2, 4, tip)
    put(arrow, 0, 2, fletch)
    put(arrow, 0, 5, fletch)

    path = os.path.join(ASSETS, "projectiles", "arrow.png")
    pygame.image.save(arrow, path)
    print(f"  Saved {path}")

    # Magic bolt: 8x8 (Istari magic — warm white/gold)
    bolt = pygame.Surface((8, 8), pygame.SRCALPHA)
    for dy in range(8):
        for dx in range(8):
            dist = ((dx - 3.5) ** 2 + (dy - 3.5) ** 2) ** 0.5
            if dist < 3.5:
                alpha = int(255 * (1 - dist / 3.5))
                r = min(255, 200 + int(55 * (1 - dist / 3.5)))
                g = min(255, 170 + int(60 * (1 - dist / 3.5)))
                b = min(255, 80 + int(100 * (1 - dist / 3.5)))
                bolt.set_at((dx, dy), (r, g, b, alpha))

    path = os.path.join(ASSETS, "projectiles", "magic_bolt.png")
    pygame.image.save(bolt, path)
    print(f"  Saved {path}")


# ============================================================
#  Isometric terrain tileset: 13 tiles, 32x26 each → 416x26 PNG
# ============================================================
def gen_tiles():
    random.seed(42)  # reproducible textures

    tw, th = 32, 26      # tile pixel size (width, height)
    flat_oy = 10          # flat tiles: diamond starts 10px down (top 10px transparent)
    dh = 16               # diamond height (standard iso)
    num_tiles = 13

    sheet = pygame.Surface((num_tiles * tw, th), pygame.SRCALPHA)

    # --- helpers -----------------------------------------------------------
    def diamond_pts(oy, h=16):
        """Return 4 vertices of an iso diamond at vertical offset oy."""
        return [(16, oy), (31, oy + h // 2), (16, oy + h), (0, oy + h // 2)]

    def in_diamond(x, y, oy, h=16):
        """Test if (x, y) falls inside the diamond."""
        cx, cy = 16, oy + h / 2
        return abs(x - cx) / 16 + abs(y - cy) / (h / 2) <= 1.0

    def fill_dia(surf, oy, color, h=16):
        pygame.draw.polygon(surf, color, diamond_pts(oy, h))

    def add_dots(surf, oy, h, colors, density):
        """Scatter random colored pixels inside the diamond."""
        for y in range(max(0, oy), min(th, oy + h)):
            for x in range(tw):
                if in_diamond(x, y, oy, h) and random.random() < density:
                    put(surf, x, y, random.choice(colors))

    def draw_3d_block(surf, base_color, height, top_color, tex_colors, density):
        """Draw elevated 3D iso block (left/right/top faces)."""
        oy = flat_oy
        # Left face (medium dark)
        dark = tuple(max(0, c - 40) for c in base_color)
        pygame.draw.polygon(surf, dark, [
            (0, oy + 8), (16, oy + 16),
            (16, oy + 16 - height), (0, oy + 8 - height),
        ])
        # Right face (darkest)
        darker = tuple(max(0, c - 60) for c in base_color)
        pygame.draw.polygon(surf, darker, [
            (31, oy + 8), (16, oy + 16),
            (16, oy + 16 - height), (31, oy + 8 - height),
        ])
        # Top face
        top_oy = oy - height
        fill_dia(surf, top_oy, top_color)
        # Texture on top face
        add_dots(surf, top_oy, 16, tex_colors, density)
        # Texture on side faces (sparser)
        for y in range(max(0, oy + 8 - height), oy + 16):
            for x in range(tw):
                a = surf.get_at((x, y)) if 0 <= x < tw and 0 <= y < th else (0, 0, 0, 0)
                if a[3] > 0 and random.random() < density * 0.4:
                    face_c = tuple(max(0, c - 50) for c in random.choice(tex_colors))
                    put(surf, x, y, face_c)

    def add_brick_lines(surf, oy, h, color):
        """Draw horizontal + offset vertical brick lines inside diamond."""
        for y in range(oy, oy + h, 4):
            for x in range(tw):
                if in_diamond(x, y, oy, h):
                    put(surf, x, y, color)
            off = 8 if ((y - oy) // 4) % 2 == 0 else 0
            for x in range(off, tw, 16):
                for dy in range(min(4, oy + h - y)):
                    if in_diamond(x, y + dy, oy, h):
                        put(surf, x, y + dy, color)

    def add_wave_lines(surf, oy, h, color):
        """Draw wavy horizontal highlight lines inside diamond."""
        import math
        for row in range(0, h, 3):
            y = oy + row
            for x in range(tw):
                wy = y + int(math.sin(x * 0.6 + row) * 0.8)
                if 0 <= wy < th and in_diamond(x, wy, oy, h):
                    put(surf, x, wy, color)

    def add_plank_lines(surf, oy, h, color):
        """Draw diagonal plank lines inside diamond (bridge wood)."""
        for y in range(oy, oy + h):
            for x in range(tw):
                if in_diamond(x, y, oy, h) and (x + y) % 6 == 0:
                    put(surf, x, y, color)

    def add_crack_lines(surf, oy, h, color):
        """Draw jagged crack lines inside diamond."""
        cx = 16
        for seg in range(3):
            x = cx + random.randint(-10, 10)
            y = oy + random.randint(2, h - 4)
            for _ in range(random.randint(4, 8)):
                if in_diamond(x, y, oy, h):
                    put(surf, x, y, color)
                x += random.choice([-1, 0, 1])
                y += random.choice([0, 1])

    # --- tile definitions --------------------------------------------------
    tiles = [
        # 0: GRASS — warm green
        dict(base=(70, 140, 55),
             tex=[(55, 120, 40), (85, 160, 65), (60, 130, 45)],
             density=0.18),
        # 1: GRASS2 — deep green
        dict(base=(45, 100, 35),
             tex=[(35, 80, 25), (55, 115, 45), (40, 90, 30)],
             density=0.20),
        # 2: DIRT — brown gravel
        dict(base=(130, 100, 60),
             tex=[(110, 85, 50), (150, 120, 75), (100, 80, 45)],
             density=0.15),
        # 3: STONE — blue-gray brick
        dict(base=(100, 105, 115),
             tex=[(85, 90, 100), (115, 120, 130)],
             density=0.10, pattern='brick',
             pat_color=(80, 85, 95)),
        # 4: STONE2 — dark stone cracks
        dict(base=(70, 72, 82),
             tex=[(55, 58, 68), (85, 88, 95)],
             density=0.10, pattern='crack',
             pat_color=(45, 48, 58)),
        # 5: WATER — blue waves
        dict(base=(40, 85, 170),
             tex=[(30, 75, 155), (35, 80, 160)],
             density=0.08, pattern='wave',
             pat_color=(75, 130, 210)),
        # 6: WATER2 — deep water
        dict(base=(25, 55, 140),
             tex=[(20, 50, 130), (30, 60, 145)],
             density=0.08, pattern='wave',
             pat_color=(50, 90, 175)),
        # 7: SAND — dark sand
        dict(base=(160, 130, 90),
             tex=[(140, 115, 78), (175, 145, 105), (130, 105, 70)],
             density=0.18),
        # 8: BRIDGE — wood planks
        dict(base=(140, 100, 50),
             tex=[(120, 85, 40), (155, 115, 60)],
             density=0.08, pattern='plank',
             pat_color=(110, 78, 35)),
        # 9: TREE — elevated h=10
        dict(base=(25, 80, 25), height=10,
             top_color=(45, 110, 40),
             tex=[(35, 95, 35), (20, 65, 18), (55, 120, 50)],
             density=0.22),
        # 10: WALL — elevated h=6, brick
        dict(base=(65, 55, 50), height=6,
             top_color=(85, 75, 70),
             tex=[(55, 48, 42), (75, 65, 58)],
             density=0.12, pattern='brick',
             pat_color=(50, 42, 38)),
        # 11: CAVE — purple-dark gravel
        dict(base=(50, 45, 55),
             tex=[(40, 35, 48), (60, 55, 68), (45, 40, 52)],
             density=0.15),
        # 12: CLIFF — elevated h=6, cracks
        dict(base=(90, 80, 75), height=6,
             top_color=(110, 100, 95),
             tex=[(75, 68, 62), (105, 95, 88)],
             density=0.15, pattern='crack',
             pat_color=(60, 52, 48)),
    ]

    for idx, td in enumerate(tiles):
        tile = pygame.Surface((tw, th), pygame.SRCALPHA)
        height = td.get('height')

        if height:
            draw_3d_block(tile, td['base'], height,
                          td['top_color'], td['tex'], td['density'])
            # Pattern on top face of elevated tiles
            top_oy = flat_oy - height
            pat = td.get('pattern')
            if pat == 'brick':
                add_brick_lines(tile, top_oy, dh, td['pat_color'])
            elif pat == 'crack':
                add_crack_lines(tile, top_oy, dh, td['pat_color'])
        else:
            # Flat tile
            fill_dia(tile, flat_oy, td['base'])
            add_dots(tile, flat_oy, dh, td['tex'], td['density'])
            # Apply pattern
            pat = td.get('pattern')
            if pat == 'brick':
                add_brick_lines(tile, flat_oy, dh, td['pat_color'])
            elif pat == 'wave':
                add_wave_lines(tile, flat_oy, dh, td['pat_color'])
            elif pat == 'plank':
                add_plank_lines(tile, flat_oy, dh, td['pat_color'])
            elif pat == 'crack':
                add_crack_lines(tile, flat_oy, dh, td['pat_color'])

        sheet.blit(tile, (idx * tw, 0))

    os.makedirs(os.path.join(ASSETS, "tiles"), exist_ok=True)
    path = os.path.join(ASSETS, "tiles", "tileset.png")
    pygame.image.save(sheet, path)
    print(f"  Saved {path}  ({sheet.get_width()}x{sheet.get_height()})")


# ============================================================
if __name__ == "__main__":
    print("Generating Middle-earth sprite assets...")
    gen_tiles()
    gen_player()
    gen_orc()
    gen_wight()
    gen_uruk()
    gen_cave_troll()
    gen_gandalf()
    gen_hobbit()
    gen_dwarf()
    gen_elf()
    gen_gondor()
    gen_projectiles()
    print("Done! Run 'python main.py' to see the sprites in-game.")
