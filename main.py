import pygame
import sys
import random

# --- CONFIGURACIÓN ---
pygame.init()
pygame.joystick.init()

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("IHC: Lunar Lander Pro")
reloj = pygame.time.Clock()

# Hardware
if pygame.joystick.get_count() == 0:
    sys.exit()
mi_joystick = pygame.joystick.Joystick(0)
mi_joystick.init()

# --- COLORES ESTILIZADOS ---
FONDO = (5, 5, 15)       # Espacio profundo
NAVE_CUERPO = (200, 200, 200)
NAVE_DETALLE = (150, 150, 150)
FUEGO = (255, 100, 0)
LUNA = (100, 100, 105)
LUNA_SOMBRA = (80, 80, 85)
PLATAFORMA_COLOR = (50, 255, 50)

# Generar cráteres aleatorios para la Luna (estilo visual)
crateres = []
for i in range(15):
    cx = random.randint(0, ANCHO)
    cy = random.randint(ALTO - 40, ALTO)
    crateres.append((cx, cy, random.randint(5, 15)))

def reiniciar_juego():
    return {
        "pos": [ANCHO // 2, 50],
        "vel": [0, 0],
        "terminado": False,
        "mensaje": "",
        "color_msg": (255, 255, 255)
    }

estado = reiniciar_juego()

def dibujar_nave(surface, x, y, encendido):
    # Cuerpo de la cápsula (Triángulo/Trapecio)
    puntos = [(x, y - 20), (x - 15, y + 10), (x + 15, y + 10)]
    pygame.draw.polygon(surface, NAVE_CUERPO, puntos)
    # Base/Patas
    pygame.draw.line(surface, NAVE_DETALLE, (x - 15, y + 10), (x - 20, y + 20), 3)
    pygame.draw.line(surface, NAVE_DETALLE, (x + 15, y + 10), (x + 20, y + 20), 3)
    # Fuego del motor
    if encendido:
        puntos_fuego = [(x - 8, y + 12), (x, y + 30 + random.randint(0, 10)), (x + 8, y + 12)]
        pygame.draw.polygon(surface, FUEGO, puntos_fuego)

def dibujar_luna(surface):
    # Superficie base
    pygame.draw.rect(surface, LUNA, (0, ALTO - 50, ANCHO, 50))
    # Cráteres
    for c in crateres:
        pygame.draw.circle(surface, LUNA_SOMBRA, (c[0], c[1]), c[2])
    # Plataforma de aterrizaje (Neón)
    pygame.draw.rect(surface, PLATAFORMA_COLOR, (ANCHO // 2 - 50, ALTO - 55, 100, 10), border_radius=3)

corriendo = True
while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: corriendo = False

    # Entradas
    eje_x = mi_joystick.get_axis(0)
    gatillo = mi_joystick.get_button(0)
    if mi_joystick.get_button(1): estado = reiniciar_juego()

    # Física
    if not estado["terminado"]:
        estado["vel"][1] += 0.12 # Menos gravedad para mejor estilo
        if gatillo: estado["vel"][1] -= 0.35
        if abs(eje_x) > 0.15: estado["vel"][0] += eje_x * 0.15
        
        estado["vel"][0] *= 0.98
        estado["pos"][0] += estado["vel"][0]
        estado["pos"][1] += estado["vel"][1]

        # Colisión
        nave_rect = pygame.Rect(estado["pos"][0] - 15, estado["pos"][1] - 20, 30, 40)
        plat_rect = pygame.Rect(ANCHO // 2 - 50, ALTO - 55, 100, 10)
        
        if nave_rect.colliderect(plat_rect):
            estado["terminado"] = True
            if estado["vel"][1] < 2.5:
                estado["mensaje"], estado["color_msg"] = "ATERRIZAJE PERFECTO", (0, 255, 0)
            else:
                estado["mensaje"], estado["color_msg"] = "CÁPSULA DESTRUIDA", (255, 50, 50)
            estado["vel"] = [0, 0]
        elif estado["pos"][1] > ALTO - 30:
            estado["terminado"] = True
            estado["mensaje"], estado["color_msg"] = "CRASH EN LA SUPERFICIE", (255, 50, 50)

    # 4. RENDERIZADO
    pantalla.fill(FONDO)
    dibujar_luna(pantalla)
    dibujar_nave(pantalla, estado['pos'][0], estado['pos'][1], gatillo)
    
    # UI con estilo (Corregido con comillas simples)
    fuente = pygame.font.SysFont("Courier New", 20, bold=True)
    color_vel = (0, 255, 0) if estado['vel'][1] < 2.5 else (255, 255, 255)
    
    # Aquí estaba el error: usamos 'vel' con comillas simples
    txt_vel = fuente.render(f"VELOCIDAD VERTICAL: {estado['vel'][1]:.2f}", True, color_vel)
    pantalla.blit(txt_vel, (20, 20))
    
    if estado['mensaje']:
        fuente_msg = pygame.font.SysFont("Courier New", 40, bold=True)
        txt_msg = fuente_msg.render(estado['mensaje'], True, estado['color_msg'])
        rect_msg = txt_msg.get_rect(center=(ANCHO // 2, ALTO // 2))
        pantalla.blit(txt_msg, rect_msg)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()