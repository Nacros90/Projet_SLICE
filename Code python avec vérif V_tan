# -*- coding: utf-8 -*-
import sys
import math
import pygame

pygame.init()

# ============================
# Fenêtre + constantes
# ============================
WIDTH, HEIGHT = 1000, 800
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

compteur_print = 0
frequence_affichage = 300  # 5 fois par seconde à 60 FPS

# ============================
# Paramètres du banc
# ============================
CENTER = (WIDTH // 2, HEIGHT // 2 + 40)
R_DISK = 240
r_min = 35
r_max = 215
V0 = 320  # Vitesse tangentielle cible

Nbp = 200 
Rp = 70 
dx = (Nbp * Rp) / 360
r = float(r_min)
r_dir = 1.0
theta = 0.0

# Trace / heatmap
trace_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
heat_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
heat_surf.fill((0, 0, 0, 0))
visit = {}

paused = False

# ============================
# Fonctions
# ============================
def reset_trace():
    global trace_surf, heat_surf, visit
    trace_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    heat_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    heat_surf.fill((0, 0, 0, 0))
    visit = {}

def pion_world_pos(r_val):
    cx, cy = CENTER
    return (cx + r_val, cy)

def draw_disk(angle_rad):
    cx, cy = CENTER
    pygame.draw.circle(screen, COPPER, (cx, cy), R_DISK)
    pygame.draw.circle(screen, (90, 60, 25), (cx, cy), R_DISK, width=7)
    L = R_DISK - 12
    x2 = cx + L * math.cos(angle_rad)
    y2 = cy + L * math.sin(angle_rad)
    pygame.draw.line(screen, WHITE, (cx, cy), (int(x2), int(y2)), 3)

def draw_pion(r_val):
    cx, cy = CENTER
    xw, yw = pion_world_pos(r_val)
    pygame.draw.line(screen, (200, 200, 200), (cx, cy), (int(xw), int(yw)), 2)
    pygame.draw.circle(screen, CARBON, (int(xw), int(yw)), 11)
    pygame.draw.circle(screen, (0, 0, 0), (int(xw), int(yw)), 11, 2)

def update_trace(r_val):
    xw, yw = pion_world_pos(r_val)
    pygame.draw.circle(trace_surf, (255, 255, 255, 35), (int(xw), int(yw)), 2)
    gx, gy = int(xw // 4), int(yw // 4)
    key = (gx, gy)
    visit[key] = visit.get(key, 0) + 1
    alpha = min(190, 10 + visit[key] * 3)
    pygame.draw.rect(heat_surf, (255, 80, 80, alpha), pygame.Rect(gx * 4, gy * 4, 4, 4))

def draw_hud(r_val, omega_val, nbp_val): 
    v_tan = omega_val * r_val
    title = FONT_BIG.render("BANC SLICE - V0 constante", True, YELLOW)
    screen.blit(title, (18, 14))
    lines = [
        f"Nbp = {nbp_val}",
        f"r(t) = {r_val:.1f} px",
        f"omega(t) = {omega_val:.3f} rad/s",
        f"Vt (réelle) = {v_tan:.1f} px/s (Cible: {V0})",
        "ESPACE: Pause | R: Reset | UP/DOWN: Nbp"
    ]
    y = 55
    for s in lines:
        surf = FONT.render(s, True, WHITE)
        screen.blit(surf, (18, y))
        y += 24

# ============================
# Boucle principale
# ============================
while True:
    dt = clock.tick(FPS) / 1000.0

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
    if keys[pygame.K_UP]: Nbp += 1
    if keys[pygame.K_DOWN]: Nbp = max(1, Nbp - 1)
    dx = (Nbp * Rp) / 360

    if not paused:
        r += r_dir * dx * dt
        if r >= r_max:
            r = float(r_max); r_dir = -1.0
        elif r <= r_min:
            r = float(r_min); r_dir = 1.0

        # MAINTIEN DE V0 CONSTANTE
        omega = V0 / max(r, 1e-6)
        theta = (theta + omega * dt) % (2 * math.pi)
        update_trace(r)

        # AFFICHAGE CONSOLE RÉDUIT
        compteur_print += 1
        if compteur_print % frequence_affichage == 0:
            print(f"VERIF: Vt = {omega * r:.2f} | R = {r:.1f}")
            compteur_print = 0
    else:
        omega = V0 / max(r, 1e-6)

    
    screen.fill(DARK_BG)               # On efface l'écran
    screen.blit(heat_surf, (0, 0))      # On affiche la heatmap
    screen.blit(trace_surf, (0, 0))     # On affiche la trace
    draw_disk(theta)                    # On dessine le disque
    draw_pion(r)                        # On dessine le pion
    draw_hud(r, omega, Nbp)             # On affiche les infos

    if paused:
        p = FONT_BIG.render("PAUSE", True, YELLOW)
        screen.blit(p, (WIDTH // 2 - 50, HEIGHT - 60))

    pygame.display.flip() # On rafraîchit l'affichage final
