
import sys          # Permet de quitter proprement le programme
import math         # Permet d’utiliser pi, cos, sin, etc.
import pygame       # Bibliothèque utilisée pour l’affichage graphique

pygame.init()       # Initialisation de Pygame

# =========================================================
# FENÊTRE
# =========================================================
WIDTH, HEIGHT = 1400, 900        # Dimensions de la fenêtre
FPS = 60                         # Nombre d’images par seconde

screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Création de la fenêtre
pygame.display.set_caption("SLICE - Banc expérimental avec courbes")  # Titre
clock = pygame.time.Clock()      # Horloge pour contrôler la vitesse

# =========================================================
# COULEURS
# =========================================================
DARK_BG = (6, 8, 18)             # Fond sombre
PANEL_BG = (235, 240, 250)       # Fond clair des panneaux

WHITE = (245, 245, 245)          # Blanc
BLACK = (0, 0, 0)                # Noir
GRAY = (80, 90, 110)             # Gris
YELLOW = (255, 220, 80)          # Jaune

COPPER = (190, 115, 45)          # Couleur cuivre du disque
COPPER_LIGHT = (230, 150, 70)    # Cuivre clair
COPPER_DARK = (90, 50, 20)       # Cuivre foncé

CARBON = (45, 45, 45)            # Couleur du pion carbone

BLUE = (40, 120, 255)            # Bleu
RED = (255, 80, 80)              # Rouge
GREEN = (80, 200, 120)           # Vert

# =========================================================
# POLICES
# =========================================================
FONT = pygame.font.SysFont("consolas", 24)        # Police normale
FONT_SMALL = pygame.font.SysFont("consolas", 18)  # Petite police
FONT_BIG = pygame.font.SysFont("arialblack", 36)  # Grande police

# =========================================================
# PARAMÈTRES PHYSIQUES DU CODE ARDUINO
# =========================================================
RAYON_MIN_CM = 1.35              # Rayon minimal réel en cm
RAYON_MAX_CM = 7.5               # Rayon maximal réel en cm

V0_CM_S = 25.0                   # Vitesse tangentielle cible en cm/s

# =========================================================
# GÉOMÉTRIE VISUELLE
# =========================================================
CENTER = (400, HEIGHT // 2 + 40)  # Centre du disque décalé vers la gauche

R_DISK_PX = 300                  # Rayon graphique du disque en pixels

PX_PAR_CM = R_DISK_PX / RAYON_MAX_CM  # Conversion : nombre de pixels pour 1 cm

r_min_px = RAYON_MIN_CM * PX_PAR_CM   # Rayon minimal converti en pixels
r_max_px = RAYON_MAX_CM * PX_PAR_CM   # Rayon maximal converti en pixels

# =========================================================
# VARIABLES DE SIMULATION
# =========================================================
Nbp = 200                        # Nombre de points utilisé pour régler le déplacement
Rp = 70                          # Paramètre de déplacement du pion

r_px = float(r_min_px)           # Position initiale du pion en pixels
r_dir = 1.0                      # Sens du déplacement du pion

theta = 0.0                      # Angle de rotation du disque
paused = False                   # Variable de pause

# =========================================================
# SURFACES POUR TRACE ET HEATMAP
# =========================================================
trace_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  # Surface de trace blanche
heat_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)   # Surface de heatmap rouge
heat_surf.fill((0, 0, 0, 0))                                  # Fond transparent

visit = {}                         # Dictionnaire qui compte les passages du pion

# =========================================================
# DONNÉES POUR LES COURBES
# =========================================================
rayon_data = []                    # Liste des rayons en cm
omega_data = []                    # Liste des vitesses angulaires
vt_data = []                       # Liste des vitesses tangentielles

MAX_POINTS = 250                   # Nombre maximal de points affichés sur le graphe

# =========================================================
# CONVERSION PIXELS -> CM
# =========================================================
def px_to_cm(val_px):
    return val_px / PX_PAR_CM      # Convertit une distance en pixels vers cm

# =========================================================
# POSITION DU PION
# =========================================================
def pion_world_pos(r_val):
    cx, cy = CENTER                # Récupération du centre du disque
    return cx + r_val, cy          # Le pion se déplace horizontalement

# =========================================================
# FOND DE L’ÉCRAN
# =========================================================
def draw_background():
    screen.fill(DARK_BG)           # Efface l’écran avec un fond sombre

    for x in range(0, WIDTH, 50):  # Lignes verticales de la grille
        pygame.draw.line(screen, (18, 22, 38), (x, 0), (x, HEIGHT), 1)

    for y in range(0, HEIGHT, 50): # Lignes horizontales de la grille
        pygame.draw.line(screen, (18, 22, 38), (0, y), (WIDTH, y), 1)

    pygame.draw.circle(screen, (20, 30, 55), CENTER, R_DISK_PX + 45, 3)  # Cercle décoratif

# =========================================================
# DESSIN DU DISQUE
# =========================================================
def draw_disk(angle_rad):
    cx, cy = CENTER                # Centre du disque

    pygame.draw.circle(screen, (0, 0, 0), (cx + 10, cy + 12), R_DISK_PX)  # Ombre
    pygame.draw.circle(screen, COPPER, (cx, cy), R_DISK_PX)              # Disque

    for i in range(0, R_DISK_PX, 20):  # Cercles internes pour effet métallique
        color = (
            max(80, COPPER[0] - i // 3),
            max(45, COPPER[1] - i // 4),
            max(20, COPPER[2] - i // 5)
        )
        pygame.draw.circle(screen, color, (cx, cy), R_DISK_PX - i, 2)

    pygame.draw.circle(screen, COPPER_DARK, (cx, cy), R_DISK_PX, 8)       # Bord foncé
    pygame.draw.circle(screen, COPPER_LIGHT, (cx, cy), R_DISK_PX - 10, 2) # Bord clair

    pygame.draw.circle(screen, (30, 30, 30), (cx, cy), 18)   # Axe central
    pygame.draw.circle(screen, WHITE, (cx, cy), 18, 2)       # Contour de l’axe

    L = R_DISK_PX - 20              # Longueur du rayon tournant

    x2 = cx + L * math.cos(angle_rad)  # Coordonnée x du bout du rayon
    y2 = cy + L * math.sin(angle_rad)  # Coordonnée y du bout du rayon

    pygame.draw.line(screen, WHITE, (cx, cy), (int(x2), int(y2)), 4)  # Rayon tournant
    pygame.draw.circle(screen, WHITE, (int(x2), int(y2)), 7)          # Point au bout

# =========================================================
# DESSIN DU PION
# =========================================================
def draw_pion(r_val):
    cx, cy = CENTER                # Centre du disque
    xw, yw = pion_world_pos(r_val) # Position du pion

    pygame.draw.line(screen, (220, 220, 220), (cx, cy), (int(xw), int(yw)), 4)  # Bras gris
    pygame.draw.line(screen, BLUE, (cx, cy + 6), (int(xw), int(yw + 6)), 2)     # Bras bleu

    pygame.draw.circle(screen, (0, 0, 0), (int(xw + 4), int(yw + 5)), 15)   # Ombre du pion
    pygame.draw.circle(screen, CARBON, (int(xw), int(yw)), 16)              # Pion carbone
    pygame.draw.circle(screen, (100, 100, 100), (int(xw), int(yw)), 16, 3)  # Contour
    pygame.draw.circle(screen, WHITE, (int(xw - 5), int(yw - 5)), 4)        # Reflet

# =========================================================
# TRACE ET HEATMAP
# =========================================================
def update_trace(r_val):
    xw, yw = pion_world_pos(r_val)  # Position du pion

    pygame.draw.circle(trace_surf, (255, 255, 255, 45), (int(xw), int(yw)), 3)  # Trace blanche

    gx, gy = int(xw // 5), int(yw // 5)  # Réduction de résolution pour la heatmap
    key = (gx, gy)                       # Case visitée

    visit[key] = visit.get(key, 0) + 1   # Incrémente le nombre de passages

    alpha = min(210, 15 + visit[key] * 4) # Intensité rouge selon le nombre de passages

    pygame.draw.rect(
        heat_surf,
        (255, 60, 60, alpha),
        pygame.Rect(gx * 5, gy * 5, 5, 5)
    )

# =========================================================
# PANNEAU D’INFORMATIONS
# =========================================================
def draw_hud(r_val, omega_val, nbp_val):
    rayon_cm = px_to_cm(r_val)          # Conversion du rayon en cm
    v_tan_cm_s = omega_val * rayon_cm  # Calcul de la vitesse tangentielle

    panel_x = 860                       # Position x du panneau décalée
    panel_y = 30                        # Position y du panneau
    panel_w = 500                       # Largeur du panneau augmentée
    panel_h = 390                       # Hauteur du panneau

    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    pygame.draw.rect(screen, PANEL_BG, panel_rect, border_radius=18)        # Fond du panneau
    pygame.draw.rect(screen, (20, 40, 80), panel_rect, 4, border_radius=18) # Bordure

    title = FONT_BIG.render("BANC SLICE", True, (10, 25, 60))  # Titre
    screen.blit(title, (panel_x + 55, panel_y + 40))           # Affichage du titre

    subtitle = FONT_SMALL.render("Grandeurs en cm", True, GRAY) # Sous-titre
    screen.blit(subtitle, (panel_x + 55, panel_y + 100))         # Affichage sous-titre

    lines = [
        f"Nbp        : {nbp_val}",
        f"Rayon      : {rayon_cm:.2f} cm",
        f"Vitesse angulaire : {omega_val:.3f} rad/s",
        f"Vt reelle  : {v_tan_cm_s:.2f} cm/s",
        f"V0 cible   : {V0_CM_S:.1f} cm/s"
    ]
    y = panel_y + 145                 # Position verticale du premier texte
    for s in lines:                   # Affichage ligne par ligne
        surf = FONT.render(s, True, BLACK)
        screen.blit(surf, (panel_x + 55, y))
        y += 40

    pygame.draw.line(screen, (20, 40, 80), (panel_x + 40, panel_y + 330),
                     (panel_x + panel_w - 40, panel_y + 330), 2)  # Séparation

    commandes = [
        "ESPACE : Pause",
        "UP/DOWN: Modifier Nbp",
        "ESC    : Quitter"
    ]
    y = panel_y + 345                 # Position des commandes
    for cmd in commandes:             # Affichage des commandes
        surf = FONT_SMALL.render(cmd, True, (120, 40, 20))
        screen.blit(surf, (panel_x + 55, y))
        y += 22

# =========================================================
# BARRE DE VITESSE ANGULAIRE
# =========================================================
def draw_speed_bar(omega_val):
    bar_x = 860                       # Position x de la barre décalée
    bar_y = 455                       # Position y de la barre
    bar_w = 500                       # Largeur de la barre augmentée
    bar_h = 38                        # Hauteur

    value = min(1.0, omega_val / 10)  # Normalisation pour la largeur de la barre

    txt = FONT_SMALL.render("Niveau de vitesse angulaire", True, WHITE)
    screen.blit(txt, (bar_x, bar_y - 32))

    pygame.draw.rect(screen, PANEL_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=15)
    pygame.draw.rect(screen, (20, 40, 80), (bar_x, bar_y, bar_w, bar_h), 3, border_radius=15)

    pygame.draw.rect(
        screen,
        BLUE,
        (bar_x + 4, bar_y + 4, int((bar_w - 8) * value), bar_h - 8),
        border_radius=12
    )

# =========================================================
# GRAPHIQUE DES COURBES
# =========================================================
def draw_graph():
    graph_x = 860                     # Position x du graphe décalée
    graph_y = 535                     # Position y du graphe
    graph_w = 500                     # Largeur du graphe augmentée
    graph_h = 320                     # Hauteur du graphe

    pygame.draw.rect(screen, PANEL_BG, (graph_x, graph_y, graph_w, graph_h), border_radius=15)
    pygame.draw.rect(screen, (20, 40, 80), (graph_x, graph_y, graph_w, graph_h), 3, border_radius=15)

    title = FONT_SMALL.render("Courbes en temps reel", True, BLACK)
    screen.blit(title, (graph_x + 18, graph_y + 12))
    legend_y = graph_y + 42           # Position de la légende
    pygame.draw.circle(screen, RED, (graph_x + 22, legend_y), 6)
    screen.blit(FONT_SMALL.render("Rayon", True, BLACK), (graph_x + 35, legend_y - 9))

    pygame.draw.circle(screen, BLUE, (graph_x + 135, legend_y), 6)
    screen.blit(FONT_SMALL.render("Vitesse angulaire", True, BLACK), (graph_x + 148, legend_y - 9))

    pygame.draw.circle(screen, GREEN, (graph_x + 255, legend_y), 6)
    screen.blit(FONT_SMALL.render("Vt", True, BLACK), (graph_x + 268, legend_y - 9))

    plot_x = graph_x + 60             # Début x de la zone de tracé décalé à l’intérieur
    plot_y = graph_y + 75             # Début y de la zone de tracé
    plot_w = graph_w - 100            # Largeur zone de tracé ajustée
    plot_h = graph_h - 110            # Hauteur zone de tracé

    pygame.draw.line(screen, BLACK, (plot_x, plot_y + plot_h),
                     (plot_x + plot_w, plot_y + plot_h), 2)  # Axe horizontal
    pygame.draw.line(screen, BLACK, (plot_x, plot_y),
                     (plot_x, plot_y + plot_h), 2)           # Axe vertical

    for i in range(1, 5):             # Grille horizontale
        y = plot_y + int(i * plot_h / 5)
        pygame.draw.line(screen, (200, 200, 200), (plot_x, y), (plot_x + plot_w, y), 1)

    def scale_points(data, min_val, max_val):
        points = []                   # Liste des points convertis

        if len(data) < 2:             # Il faut au moins deux points
            return points

        for i, val in enumerate(data):
            x = plot_x + int(i * plot_w / (MAX_POINTS - 1))
            y = plot_y + plot_h - int((val - min_val) * plot_h / (max_val - min_val))
            y = max(plot_y, min(plot_y + plot_h, y))
            points.append((x, y))
        return points

    if len(rayon_data) > 2:           # Tracé seulement si assez de points
        points_rayon = scale_points(rayon_data, RAYON_MIN_CM, RAYON_MAX_CM)
        points_omega = scale_points(omega_data, 0, 20)
        points_vt = scale_points(vt_data, 0, V0_CM_S * 1.2)

        pygame.draw.lines(screen, RED, False, points_rayon, 2)
        pygame.draw.lines(screen, BLUE, False, points_omega, 2)
        pygame.draw.lines(screen, GREEN, False, points_vt, 2)

# =========================================================
# BOUCLE PRINCIPALE
# =========================================================
while True:
    dt = clock.tick(FPS) / 1000.0     # Temps écoulé entre deux images
    for event in pygame.event.get():  # Lecture des événements
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE:
                paused = not paused

    keys = pygame.key.get_pressed()   # Lecture continue du clavier
    if keys[pygame.K_UP]:
        Nbp += 1                      # Augmente Nbp
    if keys[pygame.K_DOWN]:
        Nbp = max(1, Nbp - 1)         # Diminue Nbp sans descendre sous 1
    dx = (Nbp * Rp) / 360             # Vitesse radiale du pion

    if not paused:
        r_px += r_dir * dx * dt       # Déplacement du pion
        if r_px >= r_max_px:
            r_px = float(r_max_px)
            r_dir = -1.0
        elif r_px <= r_min_px:
            r_px = float(r_min_px)
            r_dir = 1.0
        rayon_cm = px_to_cm(r_px)     # Rayon actuel en cm
        omega = V0_CM_S / max(rayon_cm, 1e-6)  # Omega = Vt / r
        vt = omega * rayon_cm         # Vitesse tangentielle réelle
        theta = (theta + omega * dt) % (2 * math.pi)  # Rotation du disque
        update_trace(r_px)            # Mise à jour de la trace
        rayon_data.append(rayon_cm)   # Ajout du rayon dans la courbe
        omega_data.append(omega)      # Ajout de omega
        vt_data.append(vt)            # Ajout de Vt

        if len(rayon_data) > MAX_POINTS:
            rayon_data.pop(0)
            omega_data.pop(0)
            vt_data.pop(0)
    else:
        rayon_cm = px_to_cm(r_px)
        omega = V0_CM_S / max(rayon_cm, 1e-6)

    draw_background()                 # Dessin du fond
    screen.blit(heat_surf, (0, 0))    # Affichage heatmap
    screen.blit(trace_surf, (0, 0))   # Affichage trace
    draw_disk(theta)                  # Dessin disque
    draw_pion(r_px)                   # Dessin pion
    draw_hud(r_px, omega, Nbp)        # Affichage informations
    draw_speed_bar(omega)             # Barre vitesse angulaire
    draw_graph()                      # Courbes

    if paused:
        pause_text = FONT_BIG.render("PAUSE", True, YELLOW)
        screen.blit(pause_text, (WIDTH // 2 - 60, HEIGHT - 80))
    pygame.display.flip()             # Rafraîchissement écran