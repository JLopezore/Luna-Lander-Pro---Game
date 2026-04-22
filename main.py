import pygame
import sys
import random
import time

# --- CONFIGURACIÓN ---
pygame.init()
pygame.joystick.init()

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("IHC Lab: Lunar Lander Pro + Datos")
reloj = pygame.time.Clock()

# Hardware
if pygame.joystick.get_count() == 0:
    sys.exit()
mi_joystick = pygame.joystick.Joystick(0)
mi_joystick.init()

# --- COLORES ESTILIZADOS ---
FONDO = (5, 5, 15)
NAVE_CUERPO = (200, 200, 200)
NAVE_DETALLE = (150, 150, 150)
FUEGO = (255, 100, 0)
LUNA = (100, 100, 105)
LUNA_SOMBRA = (80, 80, 85)
PLATAFORMA_COLOR = (50, 255, 50)
ROJO = (255, 50, 50)
VERDE = (0, 255, 0)

# Generar cráteres aleatorios
crateres = []
for i in range(15):
    crateres.append((random.randint(0, ANCHO), random.randint(ALTO - 40, ALTO), random.randint(5, 15)))

# --- FUNCIONES DE IHC ---
def registrar_resultado(resultado, vel_final, fuel_gastado):
    """Guarda los datos de la prueba para análisis de interfaz"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("resultados_ihc.txt", "a") as f:
        f.write(f"[{timestamp}] Res: {resultado} | Vel: {vel_final:.2f} | Fuel: {fuel_gastado:.1f}%\n")

def reiniciar_juego():
    return {
        "pos": [ANCHO // 2, 50],
        "vel": [0, 0],
        "combustible": 100.0,
        "terminado": False,
        "mensaje": "",
        "color_msg": (255, 255, 255),
        "log_guardado": False
    }

estado = reiniciar_juego()

# --- FUNCIONES DE DIBUJO CON ESTILO ---
def dibujar_nave(surface, x, y, encendido):
    puntos = [(x, y - 20), (x - 15, y + 10), (x + 15, y + 10)]
    pygame.draw.polygon(surface, NAVE_CUERPO, puntos)
    pygame.draw.line(surface, NAVE_DETALLE, (x - 15, y + 10), (x - 20, y + 20), 3)
    pygame.draw.line(surface, NAVE_DETALLE, (x + 15, y + 10), (x + 20, y + 20), 3)
    
    if encendido:
        puntos_fuego = [(x - 8, y + 12), (x, y + 30 + random.randint(0, 10)), (x + 8, y + 12)]
        pygame.draw.polygon(surface, FUEGO, puntos_fuego)

def dibujar_luna(surface):
    pygame.draw.rect(surface, LUNA, (0, ALTO - 50, ANCHO, 50))
    for c in crateres:
        pygame.draw.circle(surface, LUNA_SOMBRA, (c[0], c[1]), c[2])
    pygame.draw.rect(surface, PLATAFORMA_COLOR, (ANCHO // 2 - 50, ALTO - 55, 100, 10), border_radius=3)

# --- BUCLE PRINCIPAL ---
corriendo = True
while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: corriendo = False

    eje_x = mi_joystick.get_axis(0)
    gatillo = mi_joystick.get_button(0)
    if mi_joystick.get_button(1): estado = reiniciar_juego()

    # Lógica y Física
    if not estado['terminado']:
        estado['vel'][1] += 0.12 # Gravedad
        
        # Consumo de combustible y propulsión
        if gatillo and estado['combustible'] > 0:
            estado['vel'][1] -= 0.35
            estado['combustible'] -= 0.5
            
        if abs(eje_x) > 0.15: 
            estado['vel'][0] += eje_x * 0.15
        
        estado['vel'][0] *= 0.98
        estado['pos'][0] += estado['vel'][0]
        estado['pos'][1] += estado['vel'][1]

        # Colisiones
        nave_rect = pygame.Rect(estado['pos'][0] - 15, estado['pos'][1] - 20, 30, 40)
        plat_rect = pygame.Rect(ANCHO // 2 - 50, ALTO - 55, 100, 10)
        
        if nave_rect.colliderect(plat_rect):
            estado['terminado'] = True
            if estado['vel'][1] < 2.5:
                estado['mensaje'], estado['color_msg'] = "ATERRIZAJE PERFECTO", VERDE
            else:
                estado["mensaje"], estado["color_msg"] = "CÁPSULA DESTRUIDA", ROJO
        elif estado['pos'][1] > ALTO - 30:
            estado['terminado'] = True
            estado['mensaje'], estado['color_msg'] = "CRASH EN LA SUPERFICIE", ROJO

    # Guardar datos al terminar (solo una vez)
    if estado['terminado'] and not estado['log_guardado']:
        registrar_resultado(estado['mensaje'], estado['vel'][1], 100 - estado['combustible'])
        estado['log_guardado'] = True

    # --- RENDERIZADO VISUAL ---
    pantalla.fill(FONDO)
    dibujar_luna(pantalla)
    
    # Motor activo solo si hay gatillo, hay gas, y no ha chocado
    motor_activo = gatillo and estado['combustible'] > 0 and not estado['terminado']
    dibujar_nave(pantalla, estado['pos'][0], estado['pos'][1], motor_activo)
    
    # --- INTERFAZ (UI) ESTILIZADA ---
    fuente = pygame.font.SysFont("Courier New", 18, bold=True)
    
    # Barra de combustible
    color_bar = VERDE if estado['combustible'] > 30 else ROJO
    pygame.draw.rect(pantalla, (50, 50, 50), (20, 50, 200, 20))
    pygame.draw.rect(pantalla, color_bar, (20, 50, estado['combustible'] * 2, 20))
    pantalla.blit(fuente.render(f"FUEL: {estado['combustible']:.0f}%", True, (255, 255, 255)), (20, 75))
    
    # Velocímetro (cambia a verde si vas a buena velocidad)
    color_vel = VERDE if estado['vel'][1] < 2.5 else (255, 255, 255)
    txt_vel = fuente.render(f"VELOCIDAD VERTICAL: {estado['vel'][1]:.2f}", True, color_vel)
    pantalla.blit(txt_vel, (20, 20))

    # Mensaje final
    if estado['mensaje']:
        fuente_msg = pygame.font.SysFont("Courier New", 40, bold=True)
        txt_msg = fuente_msg.render(estado['mensaje'], True, estado['color_msg'])
        rect_msg = txt_msg.get_rect(center=(ANCHO // 2, ALTO // 2))
        pantalla.blit(txt_msg, rect_msg)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()