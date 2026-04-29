import pygame
import sys
import random
import time
import os
import wave
import math
import struct

# --- IHC: GENERADOR DE AUDIO SINTÉTICO ---
def crear_archivos_de_sonido():
    if not os.path.exists("laser.wav"):
        with wave.open("laser.wav", "w") as f:
            f.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
            for i in range(int(44100 * 0.15)):
                freq = 1200 - (i / (44100 * 0.15)) * 800
                val = int(8000 * math.sin(2 * math.pi * freq * (i / 44100.0)))
                f.writeframes(struct.pack('<h', val))
                
    if not os.path.exists("choque.wav"):
        with wave.open("choque.wav", "w") as f:
            f.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
            for i in range(int(44100 * 0.6)):
                volumen = 1.0 - (i / (44100 * 0.6))
                val = int(15000 * volumen * random.uniform(-1.0, 1.0))
                f.writeframes(struct.pack('<h', val))

crear_archivos_de_sonido()

# --- OPTIMIZACIÓN DE AUDIO ---
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.joystick.init()

try:
    pygame.mixer.init()
    snd_laser = pygame.mixer.Sound("laser.wav")
    snd_choque = pygame.mixer.Sound("choque.wav")
    snd_laser.set_volume(0.3)
    snd_choque.set_volume(0.7)
    audio_on = True
except Exception as e:
    audio_on = False

# --- CONFIGURACIÓN DE PANTALLA REESCALADA ---
ANCHO, ALTO = 1024, 768  # Resolución aumentada para mejor visibilidad
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pantalla_virtual = pygame.Surface((ANCHO, ALTO))
pygame.display.set_caption("UNSIS Space Lab: Edición de Alta Resolución")
reloj = pygame.time.Clock()

if pygame.joystick.get_count() == 0:
    print("Error: Conecta el joystick Acteck.")
    sys.exit()
mi_joystick = pygame.joystick.Joystick(0)
mi_joystick.init()

# --- COLORES ---
FONDO = (10, 5, 25)
NAVE = (255, 255, 255)
NAVE_PROPULSOR = (255, 100, 0)
ASTEROIDE = (130, 120, 110)
ASTEROIDE_BORDE = (100, 90, 80)
LASER = (255, 50, 50)
BLANCO = (255, 255, 255)
DORADO = (255, 215, 0)
VINO_CLARO = (180, 50, 80)

# --- CARGAR LOGO DE LA UNSIS (Aumentado para la nueva resolución) ---
try:
    logo_unsis = pygame.image.load("unsis.png").convert_alpha()
    # Aumentamos el tamaño del logo a 50x50 para la nueva resolución
    logo_unsis = pygame.transform.scale(logo_unsis, (50, 50))
    usar_logo = True
except Exception as e:
    usar_logo = False

# --- SISTEMA DE LOGS Y RÉCORDS ---
def registrar_carrera(distancia, esquivados, destruidos):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("resultados_combate_ihc.txt", "a") as f:
        f.write(f"[{timestamp}] Distancia: {distancia:.0f}m | Esquivados: {esquivados} | Destruidos: {destruidos}\n")

def cargar_record():
    if os.path.exists("record_ihc.txt"):
        try:
            with open("record_ihc.txt", "r") as f: return float(f.read().strip())
        except: return 0.0
    return 0.0

def guardar_record(nuevo_record):
    with open("record_ihc.txt", "w") as f: f.write(str(nuevo_record))

record_historico = cargar_record()
estrellas = [(random.randint(0, ANCHO), random.randint(0, ALTO), random.uniform(1, 3)) for _ in range(150)]

def reiniciar_carrera():
    return {
        'pos': [ANCHO // 2, ALTO - 120],
        'asteroides': [],
        'disparos': [],
        'cooldown_arma': 0,
        'velocidad_base': 5.0,
        'distancia': 0,
        'esquivados': 0,
        'destruidos': 0,
        'chocado': False,
        'log_guardado': False,
        'nuevo_record': False,
        'temblor': 0,
        'flash_rojo': False
    }

def crear_asteroide(velocidad_base):
    return {
        'x': random.randint(30, ANCHO - 30),
        'y': -60,
        'radio': random.randint(25, 55), # Asteroides ligeramente más grandes
        'vx': random.uniform(-1.5, 1.5), 
        'vy': velocidad_base + random.uniform(1, 3) 
    }

estado = reiniciar_carrera()

# --- BUCLE PRINCIPAL ---
corriendo = True
while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: corriendo = False

    eje_x_crudo = mi_joystick.get_axis(0)
    eje_y_crudo = mi_joystick.get_axis(1)
    gatillo_disparo = mi_joystick.get_button(0)
    
    if mi_joystick.get_button(1): 
        estado = reiniciar_carrera()

    if not estado['chocado']:
        # FILTRO ASIMÉTRICO (Ajustado para el Acteck)
        eje_x, eje_y = 0.0, 0.0
        if eje_x_crudo < -0.15: eje_x = (eje_x_crudo + 0.15) / 0.85 
        elif eje_x_crudo > 0.15: eje_x = min(1.0, (eje_x_crudo - 0.15) / 0.45) 
        if abs(eje_y_crudo) > 0.15: eje_y = eje_y_crudo  

        # MOVIMIENTO (Escalado a la nueva resolución)
        estado['pos'][0] += eje_x * 9 # Un poco más rápido por el ancho extra
        estado['pos'][1] += eje_y * 7

        estado['pos'][0] = max(30, min(ANCHO - 30, estado['pos'][0]))
        estado['pos'][1] = max(60, min(ALTO - 60, estado['pos'][1]))

        if gatillo_disparo and estado['cooldown_arma'] == 0:
            estado['disparos'].append({'x': estado['pos'][0], 'y': estado['pos'][1] - 30, 'vy': -18})
            estado['cooldown_arma'] = 12
            estado['temblor'] = 4 
            if audio_on: snd_laser.play() 

        if estado['cooldown_arma'] > 0: estado['cooldown_arma'] -= 1

        estado['distancia'] += estado['velocidad_base'] / 10
        estado['velocidad_base'] = 5.0 + (estado['distancia'] / 150) # Dificultad escala más lento por el tamaño

        if random.random() < (0.025 + (estado['velocidad_base'] / 500)):
            estado['asteroides'].append(crear_asteroide(estado['velocidad_base']))

        for i in range(len(estrellas)):
            efecto_velocidad = estado['velocidad_base'] - (eje_y * 3) 
            estrellas[i] = (estrellas[i][0], estrellas[i][1] + estrellas[i][2] + (efecto_velocidad/2), estrellas[i][2])
            if estrellas[i][1] > ALTO: estrellas[i] = (random.randint(0, ANCHO), 0, estrellas[i][2])

        for disparo in estado['disparos'][:]:
            disparo['y'] += disparo['vy']
            if disparo['y'] < -20:
                estado['disparos'].remove(disparo)
                continue
            for ast in estado['asteroides'][:]:
                if ((disparo['x'] - ast['x'])**2 + (disparo['y'] - ast['y'])**2)**0.5 < ast['radio']:
                    estado['asteroides'].remove(ast)
                    if disparo in estado['disparos']: estado['disparos'].remove(disparo)
                    estado['destruidos'] += 1
                    break

        for ast in estado['asteroides'][:]:
            ast['x'] += ast['vx']
            ast['y'] += ast['vy'] - (eje_y * 2) 
            # Colisión con la nave circular
            RADIO_COLISION = 28
            if ((estado['pos'][0] - ast['x'])**2 + (estado['pos'][1] - ast['y'])**2)**0.5 < ast['radio'] + RADIO_COLISION: 
                estado['chocado'] = True
                estado['temblor'] = 40       
                estado['flash_rojo'] = True  
                if audio_on: snd_choque.play()

            if ast['y'] > ALTO + 60:
                estado['asteroides'].remove(ast)
                estado['esquivados'] += 1

    if estado['chocado'] and not estado['log_guardado']:
        registrar_carrera(estado['distancia'], estado['esquivados'], estado['destruidos'])
        if estado['distancia'] > record_historico:
            record_historico = estado['distancia']
            guardar_record(record_historico)
            estado['nuevo_record'] = True
        estado['log_guardado'] = True

    # --- RENDERIZADO VISUAL ---
    pantalla_virtual.fill((150, 0, 0) if estado['flash_rojo'] else FONDO)
    estado['flash_rojo'] = False

    for e in estrellas: pygame.draw.circle(pantalla_virtual, BLANCO, (int(e[0]), int(e[1])), int(e[2]))

    for d in estado['disparos']:
        pygame.draw.rect(pantalla_virtual, LASER, (int(d['x'] - 3), int(d['y']), 6, 20))

    for ast in estado['asteroides']:
        pygame.draw.circle(pantalla_virtual, ASTEROIDE, (int(ast['x']), int(ast['y'])), ast['radio'])
        pygame.draw.circle(pantalla_virtual, ASTEROIDE_BORDE, (int(ast['x']), int(ast['y'])), ast['radio'], 3)

    # DIBUJO DE LA NAVE REESCALADA
    nx, ny = estado['pos'][0], estado['pos'][1]
    if usar_logo:
        RADIO_NAVE = 28 # Más grande para mayor visibilidad del logo
        pygame.draw.circle(pantalla_virtual, BLANCO, (int(nx), int(ny)), RADIO_NAVE)
        pygame.draw.circle(pantalla_virtual, VINO_CLARO, (int(nx), int(ny)), RADIO_NAVE, 4)
        rect_logo = logo_unsis.get_rect(center=(int(nx), int(ny)))
        pantalla_virtual.blit(logo_unsis, rect_logo)
    
    if not estado['chocado']:
        largo_fuego = 45 if eje_y < -0.15 else (7 if eje_y > 0.15 else 20)
        puntos_fuego = [(nx - 15, ny + 20), (nx, ny + 20 + largo_fuego + random.randint(0, 5)), (nx + 15, ny + 20)]
        pygame.draw.polygon(pantalla_virtual, NAVE_PROPULSOR, puntos_fuego)

    # UI REUBICADA
    fuente = pygame.font.SysFont("Courier New", 24, bold=True)
    pantalla_virtual.blit(fuente.render(f"DIST: {estado['distancia']:.0f}m", True, BLANCO), (30, 30))
    pantalla_virtual.blit(fuente.render(f"CAZA: {estado['destruidos']}", True, (255, 100, 100)), (ANCHO - 200, 30))
    pantalla_virtual.blit(fuente.render(f"RÉCORD: {record_historico:.0f}m", True, DORADO), (ANCHO // 2 - 100, 30))

    if estado['chocado']:
        fuente_grande = pygame.font.SysFont("Courier New", 60, bold=True)
        msg_fin = fuente_grande.render("¡NAVE DESTRUIDA!", True, (255, 50, 50))
        pantalla_virtual.blit(msg_fin, msg_fin.get_rect(center=(ANCHO//2, ALTO//2 - 80)))
        if estado['nuevo_record']:
            msg_rec = fuente_grande.render("¡NUEVO RÉCORD!", True, DORADO)
            pantalla_virtual.blit(msg_rec, msg_rec.get_rect(center=(ANCHO//2, ALTO//2)))

    # SCREEN SHAKE
    offset_x, offset_y = 0, 0
    if estado['temblor'] > 0:
        intensidad = estado['temblor'] // 2
        offset_x = random.randint(-intensidad, intensidad)
        offset_y = random.randint(-intensidad, intensidad)
        estado['temblor'] -= 1

    pantalla.fill((0, 0, 0)) 
    pantalla.blit(pantalla_virtual, (offset_x, offset_y))
    pygame.display.flip()
    reloj.tick(60)

pygame.quit()