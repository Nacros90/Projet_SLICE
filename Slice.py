# -*- coding: utf-8 -*-
"""
Created on Mon Feb  2 01:22:30 2026

@author: RYZEN
"""

# -*- coding: utf-8 -*-
import sys
import math
import pygame

pygame.init()

# ============================
# Fenêtre + constantes
# ============================
WIDTH, HEIGHT = 1000, 700
FPS = 60

DARK_BG = (8, 10, 20)
WHITE = (255, 255, 255)
GRAY = (140, 140, 140)
YELLOW = (255, 240, 80)
COPPER = (184, 115, 51)
CARBON = (60, 60, 60)
RED = (255, 90, 90)

FONT = pygame.font.SysFont("consolas", 20)
FONT_BIG = pygame.font.SysFont("arialblack", 28)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SLICE - Banc expérimental (V0 constante)")
clock = pygame.time.Clock()

# ============================
# Paramètres du banc
# ============================

CENTER = (WIDTH // 2, HEIGHT // 2 + 40)

R_DISK = 240          # rayon disque (pixels)
r_min = 35            # rayon minimal du pion (px) -> important pour éviter omega infini
r_max = 215           # rayon maximal (px)

# Vitesse du train imposée : V0 = omega * r
V0 = 320.0            # px/s (vitesse tangentielle imposée au contact)

# Mouvement radial du pion (va-et-vient)
v_r = 90.0            # px/s (vitesse radiale du pion)
r = float(r_min)      # position radiale initiale
r_dir = 1.0           # +1 vers l'extérieur, -1 vers le centre

# Rotation disque
theta = 0.0           # angle actuel (rad)

# Trace / heatmap
trace_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
heat_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
heat_surf.fill((0, 0, 0, 0))
visit = {}  # (gx,gy) -> count

paused = False

def reset_trace():
    global trace_surf, heat_surf, visit
    trace_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    heat_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    heat_surf.fill((0, 0, 0, 0))
    visit = {}

def pion_world_pos(r_val: float):
    """Guide radial sur l'axe x du repère labo : P = (cx + r, cy)."""
    cx, cy = CENTER
    return (cx + r_val, cy)

def draw_disk(angle_rad: float):
    cx, cy = CENTER

    # disque cuivre
    pygame.draw.circle(screen, COPPER, (cx, cy), R_DISK)
    pygame.draw.circle(screen, (90, 60, 25), (cx, cy), R_DISK, width=7)

    # marqueur d'angle pour visualiser la rotation
    L = R_DISK - 12
    x2 = cx + L * math.cos(angle_rad)
    y2 = cy + L * math.sin(angle_rad)
    pygame.draw.line(screen, WHITE, (cx, cy), (int(x2), int(y2)), 3)

def draw_pion(r_val: float):
    cx, cy = CENTER
    xw, yw = pion_world_pos(r_val)

    # guide radial
    pygame.draw.line(screen, (200, 200, 200), (cx, cy), (int(xw), int(yw)), 2)

    # pion carbone
    pygame.draw.circle(screen, CARBON, (int(xw), int(yw)), 11)
    pygame.draw.circle(screen, (0, 0, 0), (int(xw), int(yw)), 11, 2)

def update_trace(r_val: float):
    xw, yw = pion_world_pos(r_val)

    # trace fine
    pygame.draw.circle(trace_surf, (255, 255, 255, 35), (int(xw), int(yw)), 2)

    # heatmap simple en grille 4x4
    gx = int(xw // 4)
    gy = int(yw // 4)
    key = (gx, gy)
    visit[key] = visit.get(key, 0) + 1
    c = visit[key]

    alpha = min(190, 10 + c * 3)
    px = gx * 4
    py = gy * 4
    pygame.draw.rect(heat_surf, (255, 80, 80, alpha), pygame.Rect(px, py, 4, 4))

def draw_hud(r_val: float, omega_val: float):
    # vitesses
    v_tan = omega_val * r_val  # devrait être ~ V0
    # ici v_rel = sqrt(v_tan^2 + v_r^2) car le pion translate
    v_rel = math.sqrt(v_tan**2 + v_r**2)

    title = FONT_BIG.render("BANC SLICE - V0 constante", True, YELLOW)
    screen.blit(title, (18, 14))

    lines = [
        f"V0 (vitesse train imposée) = {V0:.1f} px/s",
        f"r(t) = {r_val:.1f} px   |   r_min={r_min}  r_max={r_max}",
        f"omega(t) = V0 / r = {omega_val:.3f} rad/s",
        f"v_tan = omega*r = {v_tan:.1f} px/s  (≈ V0)",
        f"v_r = {v_r:.1f} px/s   =>  v_rel = sqrt(v_tan^2 + v_r^2) = {v_rel:.1f} px/s",
        "Touches : ESC quitter | ESPACE pause | R reset trace | ↑/↓ v_r | ←/→ V0",
    ]

    y = 55
    for s in lines:
        surf = FONT.render(s, True, WHITE if "Touches" not in s else GRAY)
        screen.blit(surf, (18, y))
        y += 24

# ============================
# Boucle principale
# ============================
while True:
    dt = clock.tick(FPS) / 1000.0

    # --------- Events ---------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_r:
                reset_trace()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        v_r = min(500.0, v_r + 2.0)
    if keys[pygame.K_DOWN]:
        v_r = max(0.0, v_r - 2.0)

    if keys[pygame.K_RIGHT]:
        V0 = min(1200.0, V0 + 4.0)
    if keys[pygame.K_LEFT]:
        V0 = max(10.0, V0 - 4.0)

    # --------- Update cinématique ---------
    if not paused:
        # 1) Translation radiale du pion : r(t)
        r += r_dir * v_r * dt
        if r >= r_max:
            r = float(r_max)
            r_dir = -1.0
        elif r <= r_min:
            r = float(r_min)
            r_dir = 1.0

        # 2) Vitesse angulaire pour imposer V0 constant : omega(t) = V0 / r(t)
        omega = V0 / max(r, 1e-6)  # sécurité (r_min évite déjà le problème)

        # 3) Rotation disque : theta(t)
        theta = (theta + omega * dt) % (2 * math.pi)

        # 4) Trace/heatmap de la position du contact (pion sur le disque)
        update_trace(r)
    else:
        omega = V0 / max(r, 1e-6)

    # --------- Draw ---------
    screen.fill(DARK_BG)

    # couches de visite
    screen.blit(heat_surf, (0, 0))
    screen.blit(trace_surf, (0, 0))

    draw_disk(theta)
    draw_pion(r)
    draw_hud(r, omega)

    # indicateur pause
    if paused:
        p = FONT_BIG.render("PAUSE", True, YELLOW)
        rect = p.get_rect(center=(WIDTH // 2, HEIGHT - 40))
        screen.blit(p, rect)

    pygame.display.flip()
