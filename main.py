import pygame
import sys
import random
import time

# --- CONFIGURACIÓN ---
pygame.init()
pygame.joystick.init()

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("IHC Lab: Lunar Lander Pro + Niveles")
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
AZUL = (100, 200, 255)
NARANJA = (255, 165, 0)

# Generar cráteres aleatorios fijos
crateres = [(random.randint(0, ANCHO), random.randint(ALTO - 40, ALTO), random.randint(5, 15)) for _ in range(15)]

# --- FUNCIONES DE IHC ---
def registrar_resultado(nivel, resultado, vel_final, fuel_gastado):
    """Registro de telemetría para análisis de usabilidad"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("resultados_ihc.txt", "a") as f:
        f.write(f"[{timestamp}] Nivel: {nivel} | Res: {resultado} | Vel: {vel_final:.2f} | Fuel: {fuel_gastado:.1f}%\n")

def iniciar_nivel(nivel):
    """Genera dificultad progresiva (IHC: Curva de Aprendizaje)"""
    # La plataforma se hace más estrecha
    plat_ancho = max(30, 100 - (nivel - 1) * 15)
    # El viento aumenta y es aleatorio a partir del nivel 2
    viento = 0.0 if nivel == 1 else random.uniform(-0.03, 0.03) * nivel
    # La gravedad aumenta ligeramente
    gravedad = 0.12 + (nivel - 1) * 0.005
    # El combustible inicial disminuye
    max_fuel = max(40, 100 - (nivel - 1) * 10)
    
    return {
        "nivel": nivel,
        "pos": [ANCHO // 2, 50],
        "vel": [0, 0],
        "combustible": max_fuel,
        "max_combustible": max_fuel,
        "terminado": False,
        "exito": False,
        "mensaje": "",
        "color_msg": (255, 255, 255),
        "log_guardado": False,
        "plat_ancho": plat_ancho,
        "viento": viento,
        "gravedad": gravedad
    }

estado = iniciar_nivel(1)

# --- FUNCIONES DE DIBUJO ---
def dibujar_nave(surface, x, y, encendido):
    puntos = [(x, y - 20), (x - 15, y + 10), (x + 15, y + 10)]
    pygame.draw.polygon(surface, NAVE_CUERPO, puntos)
    pygame.draw.line(surface, NAVE_DETALLE, (x - 15, y + 10), (x - 20, y + 20), 3)
    pygame.draw.line(surface, NAVE_DETALLE, (x + 15, y + 10), (x + 20, y + 20), 3)
    
    if encendido:
        puntos_fuego = [(x - 8, y + 12), (x, y + 30 + random.randint(0, 10)), (x + 8, y + 12)]
        pygame.draw.polygon(surface, FUEGO, puntos_fuego)

def dibujar_luna(surface, plat_ancho):
    pygame.draw.rect(surface, LUNA, (0, ALTO - 50, ANCHO, 50))
    for c in crateres:
        pygame.draw.circle(surface, LUNA_SOMBRA, (c[0], c[1]), c[2])
    # Plataforma centrada y dinámica
    plat_x = ANCHO // 2 - plat_ancho // 2
    pygame.draw.rect(surface, PLATAFORMA_COLOR, (plat_x, ALTO - 55, plat_ancho, 10), border_radius=3)

# --- BUCLE PRINCIPAL ---
corriendo = True
while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: corriendo = False

    eje_x = mi_joystick.get_axis(0)
    gatillo = mi_joystick.get_button(0)
    
    # IHC: Control de flujo. Avanza de nivel o repite según el éxito.
    if mi_joystick.get_button(1): 
        if estado['exito']:
            estado = iniciar_nivel(estado['nivel'] + 1)
        else:
            estado = iniciar_nivel(estado['nivel'])

    # Lógica y Física
    if not estado['terminado']:
        estado['vel'][1] += estado['gravedad']
        estado['vel'][0] += estado['viento'] # Aplicar viento lateral
        
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
        plat_x = ANCHO // 2 - estado['plat_ancho'] // 2
        plat_rect = pygame.Rect(plat_x, ALTO - 55, estado['plat_ancho'], 10)
        
        if nave_rect.colliderect(plat_rect):
            estado['terminado'] = True
            if estado['vel'][1] < 2.5:
                estado['mensaje'], estado['color_msg'] = "ATERRIZAJE PERFECTO", VERDE
                estado['exito'] = True
            else:
                estado["mensaje"], estado["color_msg"] = "CÁPSULA DESTRUIDA", ROJO
        elif estado['pos'][1] > ALTO - 30 or estado['pos'][0] < 0 or estado['pos'][0] > ANCHO:
            estado['terminado'] = True
            estado['mensaje'], estado['color_msg'] = "CRASH / FUERA DE RUTA", ROJO

    # Guardar datos al terminar
    if estado['terminado'] and not estado['log_guardado']:
        fuel_usado = estado['max_combustible'] - estado['combustible']
        registrar_resultado(estado['nivel'], estado['mensaje'], estado['vel'][1], fuel_usado)
        estado['log_guardado'] = True

    # --- RENDERIZADO VISUAL ---
    pantalla.fill(FONDO)
    dibujar_luna(pantalla, estado['plat_ancho'])
    
    motor_activo = gatillo and estado['combustible'] > 0 and not estado['terminado']
    dibujar_nave(pantalla, estado['pos'][0], estado['pos'][1], motor_activo)
    
    # --- INTERFAZ (UI) ESTILIZADA ---
    fuente = pygame.font.SysFont("Courier New", 18, bold=True)
    
    # Barra de combustible dinámica
    porcentaje_fuel = estado['combustible'] / estado['max_combustible']
    color_bar = VERDE if porcentaje_fuel > 0.3 else ROJO
    pygame.draw.rect(pantalla, (50, 50, 50), (20, 50, 200, 20))
    pygame.draw.rect(pantalla, color_bar, (20, 50, porcentaje_fuel * 200, 20))
    pantalla.blit(fuente.render(f"FUEL: {estado['combustible']:.0f}/{estado['max_combustible']}", True, (255, 255, 255)), (20, 75))
    
    # Velocímetro
    color_vel = VERDE if estado['vel'][1] < 2.5 else (255, 255, 255)
    txt_vel = fuente.render(f"VELOCIDAD: {estado['vel'][1]:.2f}", True, color_vel)
    pantalla.blit(txt_vel, (20, 20))

    # IHC: Visibilidad del Estado del Sistema (Nivel y Viento)
    txt_nivel = fuente.render(f"NIVEL: {estado['nivel']}", True, AZUL)
    pantalla.blit(txt_nivel, (ANCHO - 120, 20))
    
    if estado['viento'] != 0:
        dir_viento = "->" if estado['viento'] > 0 else "<-"
        txt_viento = fuente.render(f"VIENTO: {dir_viento} {abs(estado['viento']):.3f}", True, NARANJA)
        pantalla.blit(txt_viento, (ANCHO - 180, 50))

    # Mensaje final e instrucciones guiadas
    if estado['mensaje']:
        fuente_msg = pygame.font.SysFont("Courier New", 40, bold=True)
        txt_msg = fuente_msg.render(estado['mensaje'], True, estado['color_msg'])
        rect_msg = txt_msg.get_rect(center=(ANCHO // 2, ALTO // 2 - 30))
        pantalla.blit(txt_msg, rect_msg)
        
        # Retroalimentación clara de qué hacer a continuación
        instruccion = "Botón 1 -> SIGUIENTE NIVEL" if estado['exito'] else "Botón 1 -> REINTENTAR"
        txt_inst = fuente.render(instruccion, True, (200, 200, 200))
        rect_inst = txt_inst.get_rect(center=(ANCHO // 2, ALTO // 2 + 30))
        pantalla.blit(txt_inst, rect_inst)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()