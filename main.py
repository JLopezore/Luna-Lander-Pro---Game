import pygame
import sys
import random
import time

# --- CONFIGURACIÓN ---
pygame.init()
pygame.joystick.init()

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("IHC Lab: Lunar Lander Pro + Ambiente")
reloj = pygame.time.Clock()

# --- COLORES ESTILIZADOS ---
FONDO = (5, 5, 20)
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

# --- IHC: TOLERANCIA A FALLOS (PANTALLA DE DETECCIÓN) ---
usar_joystick = False
tiempo_inicio = pygame.time.get_ticks()
fuente_espera = pygame.font.SysFont("Courier New", 24, bold=True)

while True:
    pantalla.fill(FONDO)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Refrescar la búsqueda de hardware
    pygame.joystick.quit()
    pygame.joystick.init()

    # Si detecta el joystick, salimos del bucle de espera inmediatamente
    if pygame.joystick.get_count() > 0:
        mi_joystick = pygame.joystick.Joystick(0)
        mi_joystick.init()
        usar_joystick = True
        break

    # Calcular tiempo restante
    tiempo_actual = pygame.time.get_ticks()
    tiempo_restante = 10 - (tiempo_actual - tiempo_inicio) // 1000

    # Si se acaba el tiempo, salimos y el juego usa el teclado
    if tiempo_restante <= 0:
        break

    # Renderizar UI de espera
    txt_buscando = fuente_espera.render(f"Buscando Joystick... {tiempo_restante}s", True, NARANJA)
    txt_skip = fuente_espera.render("Presiona [ENTER] para omitir y usar TECLADO", True, (150, 150, 150))
    pantalla.blit(txt_buscando, txt_buscando.get_rect(center=(ANCHO // 2, ALTO // 2 - 20)))
    pantalla.blit(txt_skip, txt_skip.get_rect(center=(ANCHO // 2, ALTO // 2 + 30)))
    
    # Permitir omitir la espera manualmente con Enter
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_RETURN]:
        break

    pygame.display.flip()
    reloj.tick(30)


# --- GENERACIÓN DE AMBIENTE (ESTRELLAS Y METEOROS) ---
crateres = [(random.randint(0, ANCHO), random.randint(ALTO - 40, ALTO), random.randint(5, 15)) for _ in range(15)]
estrellas = [(random.randint(0, ANCHO), random.randint(0, ALTO), random.randint(1, 2), random.randint(100, 255)) for _ in range(100)]

def crear_meteoro():
    return {
        'x': random.randint(ANCHO, ANCHO + 800), 
        'y': random.randint(-400, 0),          
        'vx': random.uniform(-8, -4),          
        'vy': random.uniform(4, 8),            
        'largo': random.randint(15, 40)        
    }

meteoros = [crear_meteoro() for _ in range(3)]

# --- FUNCIONES DE IHC ---
def registrar_resultado(nivel, resultado, vel_final, fuel_gastado):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("resultados_ihc.txt", "a") as f:
        f.write(f"[{timestamp}] Nivel: {nivel} | Res: {resultado} | Vel: {vel_final:.2f} | Fuel: {fuel_gastado:.1f}%\n")

def iniciar_nivel(nivel):
    plat_ancho = max(30, 100 - (nivel - 1) * 15)
    viento = 0.0 if nivel == 1 else random.uniform(-0.03, 0.03) * nivel
    gravedad = 0.12 + (nivel - 1) * 0.005
    max_fuel = max(40, 100 - (nivel - 1) * 10)
    
    return {
        'nivel': nivel,
        'pos': [ANCHO // 2, 50],
        'vel': [0, 0],
        'combustible': max_fuel,
        'max_combustible': max_fuel,
        'terminado': False,
        'exito': False,
        'mensaje': "",
        'color_msg': (255, 255, 255),
        'log_guardado': False,
        'plat_ancho': plat_ancho,
        'viento': viento,
        'gravedad': gravedad
    }

estado = iniciar_nivel(1)

# --- FUNCIONES DE DIBUJO ---
def dibujar_fondo(surface):
    surface.fill(FONDO)
    for e in estrellas:
        pygame.draw.circle(surface, (e[3], e[3], e[3]), (e[0], e[1]), e[2])
        
    for m in meteoros:
        m['x'] += m['vx']
        m['y'] += m['vy']
        pygame.draw.line(surface, (150, 150, 200), (m['x'], m['y']), (m['x'] - m['vx'] * 1.5, m['y'] - m['vy'] * 1.5), 2)
        pygame.draw.circle(surface, (200, 200, 255), (int(m['x']), int(m['y'])), 2)
        if m['x'] < -50 or m['y'] > ALTO + 50:
            m.update(crear_meteoro())

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
    plat_x = ANCHO // 2 - plat_ancho // 2
    pygame.draw.rect(surface, PLATAFORMA_COLOR, (plat_x, ALTO - 55, plat_ancho, 10), border_radius=3)

# --- BUCLE PRINCIPAL ---
corriendo = True
while corriendo:
    # --- PROCESAMIENTO DE EVENTOS ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: 
            corriendo = False
            
        # Sistema de reinicio optimizado (Evita que salte varios niveles de golpe)
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN or evento.key == pygame.K_r:
                if estado['exito']: estado = iniciar_nivel(estado['nivel'] + 1)
                else: estado = iniciar_nivel(estado['nivel'])
                
        if evento.type == pygame.JOYBUTTONDOWN and usar_joystick:
            if evento.button == 1:
                if estado['exito']: estado = iniciar_nivel(estado['nivel'] + 1)
                else: estado = iniciar_nivel(estado['nivel'])

    # --- LECTURA HÍBRIDA DE CONTROLES (Joystick + Teclado) ---
    eje_x = 0.0
    gatillo = False
    teclas = pygame.key.get_pressed()

    # 1. Leer hardware si está activo
    if usar_joystick:
        eje_x = mi_joystick.get_axis(0)
        gatillo = mi_joystick.get_button(0)

    # 2. Leer teclado (Sobrescribe o complementa al joystick)
    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        eje_x = -1.0
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        eje_x = 1.0
    if teclas[pygame.K_UP] or teclas[pygame.K_SPACE] or teclas[pygame.K_w]:
        gatillo = True

    # --- LÓGICA Y FÍSICA ---
    if not estado['terminado']:
        estado['vel'][1] += estado['gravedad']
        estado['vel'][0] += estado['viento']
        
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
                estado['mensaje'], estado['color_msg'] = "CÁPSULA DESTRUIDA", ROJO
        elif estado['pos'][1] > ALTO - 30 or estado['pos'][0] < 0 or estado['pos'][0] > ANCHO:
            estado['terminado'] = True
            estado['mensaje'], estado['color_msg'] = "CRASH / FUERA DE RUTA", ROJO

    # Guardar datos
    if estado['terminado'] and not estado['log_guardado']:
        fuel_usado = estado['max_combustible'] - estado['combustible']
        registrar_resultado(estado['nivel'], estado['mensaje'], estado['vel'][1], fuel_usado)
        estado['log_guardado'] = True

    # --- RENDERIZADO VISUAL ---
    dibujar_fondo(pantalla)
    dibujar_luna(pantalla, estado['plat_ancho'])
    
    motor_activo = gatillo and estado['combustible'] > 0 and not estado['terminado']
    dibujar_nave(pantalla, estado['pos'][0], estado['pos'][1], motor_activo)
    
    # --- INTERFAZ (UI) ESTILIZADA ---
    fuente = pygame.font.SysFont("Courier New", 18, bold=True)
    
    porcentaje_fuel = estado['combustible'] / estado['max_combustible']
    color_bar = VERDE if porcentaje_fuel > 0.3 else ROJO
    pygame.draw.rect(pantalla, (50, 50, 50), (20, 50, 200, 20))
    pygame.draw.rect(pantalla, color_bar, (20, 50, porcentaje_fuel * 200, 20))
    pantalla.blit(fuente.render(f"FUEL: {estado['combustible']:.0f}/{estado['max_combustible']}", True, (255, 255, 255)), (20, 75))
    
    color_vel = VERDE if estado['vel'][1] < 2.5 else (255, 255, 255)
    txt_vel = fuente.render(f"VELOCIDAD: {estado['vel'][1]:.2f}", True, color_vel)
    pantalla.blit(txt_vel, (20, 20))

    # Indicador de Método de Entrada
    txt_control = fuente.render("MODO: JOYSTICK" if usar_joystick else "MODO: TECLADO", True, (150, 150, 150))
    pantalla.blit(txt_control, (20, ALTO - 30))

    txt_nivel = fuente.render(f"NIVEL: {estado['nivel']}", True, AZUL)
    pantalla.blit(txt_nivel, (ANCHO - 120, 20))
    
    if estado['viento'] != 0:
        dir_viento = "->" if estado['viento'] > 0 else "<-"
        txt_viento = fuente.render(f"VIENTO: {dir_viento} {abs(estado['viento']):.3f}", True, NARANJA)
        pantalla.blit(txt_viento, (ANCHO - 180, 50))

    if estado['mensaje']:
        fuente_msg = pygame.font.SysFont("Courier New", 40, bold=True)
        txt_msg = fuente_msg.render(estado['mensaje'], True, estado['color_msg'])
        rect_msg = txt_msg.get_rect(center=(ANCHO // 2, ALTO // 2 - 30))
        pantalla.blit(txt_msg, rect_msg)
        
        instruccion = "Presiona [ENTER] o Botón 1 -> SIGUIENTE NIVEL" if estado['exito'] else "Presiona [ENTER] o Botón 1 -> REINTENTAR"
        txt_inst = fuente.render(instruccion, True, (200, 200, 200))
        rect_inst = txt_inst.get_rect(center=(ANCHO // 2, ALTO // 2 + 30))
        pantalla.blit(txt_inst, rect_inst)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()