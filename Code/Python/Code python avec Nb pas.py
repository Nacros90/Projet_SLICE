# -*- coding: utf-8 -*-
"""
Created on Mon May  4 20:20:07 2026"""


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

Nbp = 200 #Nb de pas
Rp = 70 # rayon de la poulie
dx = (Nbp*Rp)/360
v_r = dx            # px/s (vitesse radiale du pion)
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
    # On augmente la visibilité de la heatmap en rendant l'alpha plus sensible.
    # L'alpha augmentera plus vite avec le nombre de visites (c).
    alpha = min(220, 20 + c * 5)

    px = gx * 4
    py = gy * 4
    pygame.draw.rect(heat_surf, (255, 80, 80, alpha), pygame.Rect(px, py, 4, 4))

def draw_hud(r_val, omega_val, nbp_val, v_r_val):
    v_tan = omega_val * r_val
    v_rel = math.sqrt(v_tan**2 + v_r_val**2)

    title = FONT_BIG.render("BANC SLICE - V0 constante", True, YELLOW)
    screen.blit(title, (18, 14))

    lines = [
        f"Nombre de pas (Nbp) = {nbp_val}",
        f"r(t) = {r_val:.1f} px   |   r_min={r_min}  r_max={r_max}",
        f"omega(t) = V0 / r = {omega_val:.3f} rad/s",
        f"v_tan = omega*r = {v_tan:.1f} px/s  (≈ V0)",
        f"v_r = {v_r_val:.1f} px/s   =>  v_rel = sqrt(v_tan^2 + v_r^2) = {v_rel:.1f} px/s",
        "Touches : ESC quitter | ESPACE pause | R reset trace | up/down Nb pas",
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
    # 1) GESTION DU TEMPS
    dt = clock.tick(FPS) / 1000.0              # Temps entre deux images
    # On n'a plus besoin de t_total si on n'utilise pas de sinus

    # --------- Events ---------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
            
        # CETTE PARTIE DOIT ÊTRE BIEN ALIGNÉE ICI :
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_r:
                reset_trace()
    # --- AJOUT : Changement dynamique du nombre de pas ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        Nbp += 1  # Augmente le nombre de pas
    if keys[pygame.K_DOWN]:
        Nbp = max(1, Nbp - 1)  # Diminue sans descendre en dessous de 1

    # On recalcule dx car Nbp a pu changer
    dx = (Nbp * Rp) / 360
    v_r_actuelle = dx

    # --------- Update cinématique ---------
    if not paused:
        # Mise à jour de la position radiale r
        # Le pion avance de façon linéaire (vitesse constante)
        r += r_dir * v_r_actuelle * dt
        
        # Inversion de direction aux limites
        if r >= r_max:
            r = float(r_max)
            r_dir = -1.0
        elif r <= r_min:
            r = float(r_min)
            r_dir = 1.0

        # MAINTIEN DE V0 CONSTANTE
        # C'est ici que la magie opère : omega s'adapte à r
        omega = V0 / max(r, 1e-6)

        # Rotation du disque
        theta = (theta + omega * dt) % (2 * math.pi)

        update_trace(r)
    else:
        omega = V0 / max(r, 1e-6)

    # --------- Draw (Affichage) ---------
    screen.fill(DARK_BG)
    draw_disk(theta)

    # On dessine la trace fine d'abord, puis la heatmap par-dessus pour qu'elle soit plus visible.
    screen.blit(trace_surf, (0, 0))
    screen.blit(heat_surf, (0, 0))

    draw_pion(r)
    
    draw_hud(r, omega, Nbp, v_r_actuelle)

    if paused:
        p = FONT_BIG.render("PAUSE", True, YELLOW)
        screen.blit(p, (WIDTH // 2 - 50, HEIGHT - 60))

    pygame.display.flip()
