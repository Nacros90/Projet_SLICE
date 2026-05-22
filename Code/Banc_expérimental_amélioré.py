# -*- coding: utf-8 -*-
"""
Created on Thu May 21 10:34:03 2026

@author: RYZEN
"""

import sys
import math
import pygame

pygame.init()

# =========================================================
# FENETRE
# =========================================================
WIDTH, HEIGHT = 1400, 720
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SLICE - Banc expérimental amélioré")
clock = pygame.time.Clock()

# =========================================================
# COULEURS
# =========================================================
DARK_BG = (6, 8, 18)

PANEL_BG = (235, 240, 250)

WHITE = (245, 245, 245)
BLACK = (0, 0, 0)

GRAY = (80, 90, 110)

YELLOW = (255, 220, 80)

COPPER = (190, 115, 45)
COPPER_LIGHT = (230, 150, 70)
COPPER_DARK = (90, 50, 20)

CARBON = (45, 45, 45)

BLUE = (40, 120, 255)

# =========================================================
# FONTS
# =========================================================
FONT = pygame.font.SysFont("consolas", 26)
FONT_SMALL = pygame.font.SysFont("consolas", 20)
FONT_BIG = pygame.font.SysFont("arialblack", 38)

# =========================================================
# GEOMETRIE
# =========================================================
CENTER = (WIDTH // 2 - 120, HEIGHT // 2 + 40)

R_DISK = 300

r_min = 45
r_max = 270

# vitesse tangentielle cible
V0 = 320

# nombre de points
Nbp = 200

Rp = 70

# =========================================================
# VARIABLES
# =========================================================
r = float(r_min)
r_dir = 1.0

theta = 0.0

paused = False

compteur_print = 0
frequence_affichage = 300

# =========================================================
# SURFACES
# =========================================================
trace_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
heat_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

visit = {}

# =========================================================
# RESET
# =========================================================
def reset_trace():
    global trace_surf, heat_surf, visit

    trace_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    heat_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    visit = {}

# =========================================================
# POSITION PION
# =========================================================
def pion_world_pos(r_val):
    cx, cy = CENTER
    return cx + r_val, cy

# =========================================================
# BACKGROUND
# =========================================================
def draw_background():

    screen.fill(DARK_BG)

    # grille
    for x in range(0, WIDTH, 50):
        pygame.draw.line(
            screen,
            (18, 22, 38),
            (x, 0),
            (x, HEIGHT),
            1
        )

    for y in range(0, HEIGHT, 50):
        pygame.draw.line(
            screen,
            (18, 22, 38),
            (0, y),
            (WIDTH, y),
            1
        )

    pygame.draw.circle(
        screen,
        (20, 30, 55),
        CENTER,
        R_DISK + 45,
        3
    )

# =========================================================
# DISQUE
# =========================================================
def draw_disk(angle_rad):

    cx, cy = CENTER

    # ombre
    pygame.draw.circle(
        screen,
        (0, 0, 0),
        (cx + 10, cy + 12),
        R_DISK
    )

    # disque
    pygame.draw.circle(screen, COPPER, (cx, cy), R_DISK)

    # cercles cuivre
    for i in range(0, R_DISK, 20):

        color = (
            max(80, COPPER[0] - i // 3),
            max(45, COPPER[1] - i // 4),
            max(20, COPPER[2] - i // 5)
        )

        pygame.draw.circle(
            screen,
            color,
            (cx, cy),
            R_DISK - i,
            2
        )

    pygame.draw.circle(
        screen,
        COPPER_DARK,
        (cx, cy),
        R_DISK,
        8
    )

    pygame.draw.circle(
        screen,
        COPPER_LIGHT,
        (cx, cy),
        R_DISK - 10,
        2
    )

    # axe central
    pygame.draw.circle(screen, (30, 30, 30), (cx, cy), 18)
    pygame.draw.circle(screen, WHITE, (cx, cy), 18, 2)

    # rayon mobile
    L = R_DISK - 20

    x2 = cx + L * math.cos(angle_rad)
    y2 = cy + L * math.sin(angle_rad)

    pygame.draw.line(
        screen,
        WHITE,
        (cx, cy),
        (int(x2), int(y2)),
        4
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (int(x2), int(y2)),
        7
    )

# =========================================================
# PION
# =========================================================
def draw_pion(r_val):

    cx, cy = CENTER

    xw, yw = pion_world_pos(r_val)

    # bras
    pygame.draw.line(
        screen,
        (220, 220, 220),
        (cx, cy),
        (int(xw), int(yw)),
        4
    )

    pygame.draw.line(
        screen,
        BLUE,
        (cx, cy + 6),
        (int(xw), int(yw + 6)),
        2
    )

    # pion
    pygame.draw.circle(
        screen,
        (0, 0, 0),
        (int(xw + 4), int(yw + 5)),
        15
    )

    pygame.draw.circle(
        screen,
        CARBON,
        (int(xw), int(yw)),
        16
    )

    pygame.draw.circle(
        screen,
        (100, 100, 100),
        (int(xw), int(yw)),
        16,
        3
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (int(xw - 5), int(yw - 5)),
        4
    )

# =========================================================
# TRACE
# =========================================================
def update_trace(r_val):

    xw, yw = pion_world_pos(r_val)

    pygame.draw.circle(
        trace_surf,
        (255, 255, 255, 45),
        (int(xw), int(yw)),
        3
    )

    gx, gy = int(xw // 5), int(yw // 5)

    key = (gx, gy)

    visit[key] = visit.get(key, 0) + 1

    alpha = min(210, 15 + visit[key] * 4)

    pygame.draw.rect(
        heat_surf,
        (255, 60, 60, alpha),
        pygame.Rect(gx * 5, gy * 5, 5, 5)
    )

# =========================================================
# HUD
# =========================================================
def draw_hud(r_val, omega_val, nbp_val):

    v_tan = omega_val * r_val

    panel_x = 930
    panel_y = 60

    panel_w = 420
    panel_h = 430

    panel_rect = pygame.Rect(
        panel_x,
        panel_y,
        panel_w,
        panel_h
    )

    pygame.draw.rect(
        screen,
        PANEL_BG,
        panel_rect,
        border_radius=18
    )

    pygame.draw.rect(
        screen,
        (20, 40, 80),
        panel_rect,
        4,
        border_radius=18
    )

    title = FONT_BIG.render(
        "BANC SLICE",
        True,
        (10, 25, 60)
    )

    screen.blit(
        title,
        (panel_x + 35, panel_y + 25)
    )

    subtitle = FONT_SMALL.render(
        "Vitesse tangentielle constante",
        True,
        GRAY
    )

    screen.blit(
        subtitle,
        (panel_x + 35, panel_y + 80)
    )

    lines = [
        f"Nbp        : {nbp_val}",
        f"r(t)       : {r_val:.1f} px",
        f"omega(t)   : {omega_val:.3f} rad/s",
        f"Vt reelle  : {v_tan:.1f} px/s",
        f"V0 cible   : {V0} px/s"
    ]

    y = panel_y + 125

    for s in lines:

        surf = FONT.render(s, True, BLACK)

        screen.blit(
            surf,
            (panel_x + 35, y)
        )

        y += 42

    pygame.draw.line(
        screen,
        (20, 40, 80),
        (panel_x + 30, panel_y + 345),
        (panel_x + panel_w - 30, panel_y + 345),
        2
    )

    commandes = [
        "ESPACE : Pause",
        "UP/DOWN: Modifier Nbp",
        "ESC    : Quitter"
    ]

    y = panel_y + 360

    for cmd in commandes:

        surf = FONT_SMALL.render(
            cmd,
            True,
            (120, 40, 20)
        )

        screen.blit(
            surf,
            (panel_x + 35, y)
        )

        y += 23

# =========================================================
# BARRE VITESSE
# =========================================================
def draw_speed_bar(omega_val):

    bar_x = 930

    # DECALAGE VERS LE BAS
    bar_y = 560

    bar_w = 420
    bar_h = 38

    value = min(1.0, omega_val / 10)

    txt = FONT_SMALL.render(
        "Niveau de vitesse angulaire",
        True,
        WHITE
    )

    screen.blit(
        txt,
        (bar_x, bar_y - 35)
    )

    pygame.draw.rect(
        screen,
        PANEL_BG,
        (bar_x, bar_y, bar_w, bar_h),
        border_radius=15
    )

    pygame.draw.rect(
        screen,
        (20, 40, 80),
        (bar_x, bar_y, bar_w, bar_h),
        3,
        border_radius=15
    )

    pygame.draw.rect(
        screen,
        BLUE,
        (
            bar_x + 4,
            bar_y + 4,
            int((bar_w - 8) * value),
            bar_h - 8
        ),
        border_radius=12
    )

# =========================================================
# BOUCLE PRINCIPALE
# =========================================================
while True:

    dt = clock.tick(FPS) / 1000.0

    # =====================================================
    # EVENTS
    # =====================================================
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key == pygame.K_SPACE:
                paused = not paused

    # =====================================================
    # CLAVIER
    # =====================================================
    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        Nbp += 1

    if keys[pygame.K_DOWN]:
        Nbp = max(1, Nbp - 1)

    # =====================================================
    # MOUVEMENT
    # =====================================================
    dx = (Nbp * Rp) / 360

    if not paused:

        r += r_dir * dx * dt

        if r >= r_max:
            r = float(r_max)
            r_dir = -1.0

        elif r <= r_min:
            r = float(r_min)
            r_dir = 1.0

        omega = V0 / max(r, 1e-6)

        theta = (theta + omega * dt) % (2 * math.pi)

        update_trace(r)

        compteur_print += 1

        if compteur_print % frequence_affichage == 0:

            print(
                f"VERIF: Vt = {omega * r:.2f} | R = {r:.1f}"
            )

            compteur_print = 0

    else:

        omega = V0 / max(r, 1e-6)

    # =====================================================
    # AFFICHAGE
    # =====================================================
    draw_background()

    screen.blit(heat_surf, (0, 0))
    screen.blit(trace_surf, (0, 0))

    draw_disk(theta)

    draw_pion(r)

    draw_hud(r, omega, Nbp)

    draw_speed_bar(omega)

    # =====================================================
    # PAUSE
    # =====================================================
    if paused:

        pause_text = FONT_BIG.render(
            "PAUSE",
            True,
            YELLOW
        )

        screen.blit(
            pause_text,
            (WIDTH // 2 - 60, HEIGHT - 80)
        )

    pygame.display.flip()