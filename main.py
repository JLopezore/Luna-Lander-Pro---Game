import pygame
import sys
import random
import time

# --- CONFIGURACIÓN ---
pygame.init()
pygame.joystick.init()

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("IHC Lab: Carrera Espacial de Reacción")
reloj = pygame.time.Clock()

# Hardware
if pygame.joystick.get_count() == 0:
    print("Conecta el joystick.")
    sys.exit()
mi_joystick = pygame.joystick.Joystick(0)
mi_joystick.init()

# --- COLORES ---
FONDO = (10, 5, 25)
NAVE = (100, 200, 255)
NAVE_PROPULSOR = (255, 100, 0)
ASTEROIDE = (130, 120, 110)
ASTEROIDE_BORDE = (100, 90, 80)
BLANCO = (255, 255, 255)

# --- SISTEMA DE LOGS (IHC) ---
def registrar_carrera(distancia, asteroides_esquivados):
    """Guarda el desempeño para analizar el tiempo de reacción del usuario"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("resultados_carrera_ihc.txt", "a") as f:
        f.write(f"[{timestamp}] Distancia: {distancia:.0f}m | Esquivados: {asteroides_esquivados}\n")

# --- GENERACIÓN DE ENTORNO ---
estrellas = [(random.randint(0, ANCHO), random.randint(0, ALTO), random.uniform(1, 3)) for _ in range(100)]

def reiniciar_carrera():
    return {
        'pos': [ANCHO // 2, ALTO - 100], # Inicia abajo al centro
        'asteroides': [],
        'velocidad_base': 5.0, # Velocidad inicial del scroll
        'distancia': 0,
        'esquivados': 0,
        'chocado': False,
        'log_guardado': False
    }

def crear_asteroide(velocidad_base):
    # Aparecen arriba de la pantalla, en una posición X aleatoria
    return {
        'x': random.randint(20, ANCHO - 20),
        'y': -50,
        'radio': random.randint(20, 45),
        'vx': random.uniform(-1, 1), # Ligero movimiento lateral
        'vy': velocidad_base + random.uniform(1, 3) # Caen a la velocidad de la nave + extra
    }

estado = reiniciar_carrera()

# --- BUCLE PRINCIPAL ---
corriendo = True
while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: corriendo = False

    # 1. ENTRADAS (IHC: Mapeo de 2 ejes)
    eje_x = mi_joystick.get_axis(0) # Izquierda/Derecha
    eje_y = mi_joystick.get_axis(1) # Arriba (Acelerar) / Abajo (Frenar)
    
    # Botón 1 para reiniciar
    if mi_joystick.get_button(1): 
        estado = reiniciar_carrera()

    # 2. LÓGICA DE JUEGO Y FÍSICA
    if not estado['chocado']:
        # Mover la nave con el joystick (Sensibilidad analógica)
        if abs(eje_x) > 0.15:
            estado['pos'][0] += eje_x * 8
        if abs(eje_y) > 0.15:
            estado['pos'][1] += eje_y * 6

        # Límites de la pantalla (Para no escapar)
        estado['pos'][0] = max(20, min(ANCHO - 20, estado['pos'][0]))
        estado['pos'][1] = max(50, min(ALTO - 50, estado['pos'][1]))

        # Progresión de dificultad (IHC: Carga Cognitiva y Tiempo de Reacción)
        # Cada frame se suma distancia. A más distancia, más rápido va todo.
        estado['distancia'] += estado['velocidad_base'] / 10
        estado['velocidad_base'] = 5.0 + (estado['distancia'] / 100) # Sube la velocidad gradualmente

        # Generador de asteroides (Frecuencia depende de la velocidad)
        probabilidad_spawn = 0.02 + (estado['velocidad_base'] / 500)
        if random.random() < probabilidad_spawn:
            estado['asteroides'].append(crear_asteroide(estado['velocidad_base']))

        # Actualizar estrellas (Efecto de velocidad)
        for i in range(len(estrellas)):
            # El eje Y afecta qué tan rápido parece que nos movemos (Frenar vs Acelerar)
            efecto_velocidad = estado['velocidad_base'] - (eje_y * 3) 
            estrellas[i] = (estrellas[i][0], estrellas[i][1] + estrellas[i][2] + (efecto_velocidad/2), estrellas[i][2])
            if estrellas[i][1] > ALTO:
                estrellas[i] = (random.randint(0, ANCHO), 0, estrellas[i][2])

        # Actualizar asteroides y detectar colisiones
        rect_nave = pygame.Rect(estado['pos'][0] - 15, estado['pos'][1] - 20, 30, 40)
        
        for ast in estado['asteroides'][:]:
            # Mover asteroide (sufren el mismo efecto visual de acelerar/frenar)
            ast['x'] += ast['vx']
            ast['y'] += ast['vy'] - (eje_y * 2) 

            # Colisión circular simplificada (Punto central vs Radio)
            distancia_colision = ((estado['pos'][0] - ast['x'])**2 + (estado['pos'][1] - ast['y'])**2)**0.5
            if distancia_colision < ast['radio'] + 15: # 15 es un aprox del radio de la nave
                estado['chocado'] = True

            # Asteroide esquivado (sale por abajo)
            if ast['y'] > ALTO + 50:
                estado['asteroides'].remove(ast)
                estado['esquivados'] += 1

    # Guardar telemetría al chocar
    if estado['chocado'] and not estado['log_guardado']:
        registrar_carrera(estado['distancia'], estado['esquivados'])
        estado['log_guardado'] = True

    # 3. RENDERIZADO VISUAL
    pantalla.fill(FONDO)
    
    # Dibujar estrellas (Scrolling de fondo)
    for e in estrellas:
        pygame.draw.circle(pantalla, BLANCO, (int(e[0]), int(e[1])), int(e[2]))

    # Dibujar Asteroides
    for ast in estado['asteroides']:
        pygame.draw.circle(pantalla, ASTEROIDE, (int(ast['x']), int(ast['y'])), ast['radio'])
        pygame.draw.circle(pantalla, ASTEROIDE_BORDE, (int(ast['x']), int(ast['y'])), ast['radio'], 3)
        # Cráteres falsos en el asteroide para darle textura
        pygame.draw.circle(pantalla, ASTEROIDE_BORDE, (int(ast['x'] - ast['radio']/3), int(ast['y'] - ast['radio']/3)), int(ast['radio']/4))

    # Dibujar Nave (Forma de Flecha)
    nx, ny = estado['pos'][0], estado['pos'][1]
    puntos_nave = [(nx, ny - 25), (nx - 20, ny + 15), (nx, ny + 5), (nx + 20, ny + 15)]
    pygame.draw.polygon(pantalla, NAVE, puntos_nave)
    
    # Fuego propulsor dinámico (Crece si empujas la palanca hacia adelante/arriba)
    largo_fuego = 15
    if eje_y < -0.15: largo_fuego = 35 # Acelerando
    elif eje_y > 0.15: largo_fuego = 5 # Frenando
    
    if not estado['chocado']:
        puntos_fuego = [(nx - 10, ny + 10), (nx, ny + 10 + largo_fuego + random.randint(0, 5)), (nx + 10, ny + 10)]
        pygame.draw.polygon(pantalla, NAVE_PROPULSOR, puntos_fuego)

    # 4. INTERFAZ Y TEXTOS
    fuente = pygame.font.SysFont("Courier New", 22, bold=True)
    
    # HUD Superior
    txt_dist = fuente.render(f"DISTANCIA: {estado['distancia']:.0f} m", True, BLANCO)
    txt_vel = fuente.render(f"VELOCIDAD: {estado['velocidad_base']*10:.0f} km/h", True, (150, 255, 150))
    pantalla.blit(txt_dist, (20, 20))
    pantalla.blit(txt_vel, (ANCHO - 280, 20))

    if estado['chocado']:
        fuente_grande = pygame.font.SysFont("Courier New", 50, bold=True)
        txt_fin = fuente_grande.render("¡COLISIÓN!", True, (255, 50, 50))
        txt_res = fuente.render(f"Esquivaste {estado['esquivados']} asteroides.", True, BLANCO)
        txt_inst = fuente.render("Presiona Botón 1 para reintentar", True, (150, 150, 150))
        
        pantalla.blit(txt_fin, txt_fin.get_rect(center=(ANCHO//2, ALTO//2 - 40)))
        pantalla.blit(txt_res, txt_res.get_rect(center=(ANCHO//2, ALTO//2 + 10)))
        pantalla.blit(txt_inst, txt_inst.get_rect(center=(ANCHO//2, ALTO//2 + 50)))

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()