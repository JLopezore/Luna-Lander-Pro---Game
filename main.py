import pygame
import sys
import random
import time
import os
import wave
import math
import struct

# --- IHC: GENERADOR DE AUDIO SINTÉTICO ---
# Creamos los sonidos por código para no depender de archivos externos
def crear_archivos_de_sonido():
    if not os.path.exists("laser.wav"):
        with wave.open("laser.wav", "w") as f:
            f.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
            for i in range(int(44100 * 0.15)): # Duración 0.15s
                freq = 1200 - (i / (44100 * 0.15)) * 800 # Frecuencia descendente (Pew!)
                val = int(8000 * math.sin(2 * math.pi * freq * (i / 44100.0)))
                f.writeframes(struct.pack('<h', val))
                
    if not os.path.exists("choque.wav"):
        with wave.open("choque.wav", "w") as f:
            f.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
            for i in range(int(44100 * 0.6)): # Duración 0.6s
                volumen = 1.0 - (i / (44100 * 0.6)) # Fade out
                val = int(15000 * volumen * random.uniform(-1.0, 1.0)) # Ruido blanco (Explosión)
                f.writeframes(struct.pack('<h', val))

crear_archivos_de_sonido()

# --- CONFIGURACIÓN ---
pygame.init()
pygame.joystick.init()

# Inicializar Audio con manejo de errores por si Docker bloquea la tarjeta de sonido
try:
    pygame.mixer.init()
    snd_laser = pygame.mixer.Sound("laser.wav")
    snd_choque = pygame.mixer.Sound("choque.wav")
    snd_laser.set_volume(0.3)
    snd_choque.set_volume(0.7)
    audio_on = True
except Exception as e:
    print(f"IHC Audio Warning: {e}")
    audio_on = False

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pantalla_virtual = pygame.Surface((ANCHO, ALTO))
pygame.display.set_caption("IHC Lab: Experiencia Audiovisual")
reloj = pygame.time.Clock()

# Hardware
if pygame.joystick.get_count() == 0:
    print("Error: Conecta el Acteck AGJ-4000.")
    sys.exit()
mi_joystick = pygame.joystick.Joystick(0)
mi_joystick.init()

# --- COLORES ---
FONDO = (10, 5, 25)
NAVE = (100, 200, 255)
NAVE_PROPULSOR = (255, 100, 0)
ASTEROIDE = (130, 120, 110)
ASTEROIDE_BORDE = (100, 90, 80)
LASER = (255, 50, 50)
BLANCO = (255, 255, 255)
DORADO = (255, 215, 0)

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
estrellas = [(random.randint(0, ANCHO), random.randint(0, ALTO), random.uniform(1, 3)) for _ in range(100)]

def reiniciar_carrera():
    return {
        'pos': [ANCHO // 2, ALTO - 100],
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
        'x': random.randint(20, ANCHO - 20),
        'y': -50,
        'radio': random.randint(20, 45),
        'vx': random.uniform(-1.5, 1.5), 
        'vy': velocidad_base + random.uniform(1, 3) 
    }

estado = reiniciar_carrera()

# --- BUCLE PRINCIPAL ---
corriendo = True
while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: corriendo = False

    eje_x = mi_joystick.get_axis(0)
    eje_y = mi_joystick.get_axis(1)
    gatillo_disparo = mi_joystick.get_button(0)
    
    if mi_joystick.get_button(1): 
        estado = reiniciar_carrera()

    if not estado['chocado']:
        if abs(eje_x) > 0.15: estado['pos'][0] += eje_x * 8
        if abs(eje_y) > 0.15: estado['pos'][1] += eje_y * 6

        estado['pos'][0] = max(20, min(ANCHO - 20, estado['pos'][0]))
        estado['pos'][1] = max(50, min(ALTO - 50, estado['pos'][1]))

        # Disparos y Efecto Auditivo
        if gatillo_disparo and estado['cooldown_arma'] == 0:
            estado['disparos'].append({'x': estado['pos'][0], 'y': estado['pos'][1] - 25, 'vy': -15})
            estado['cooldown_arma'] = 12
            estado['temblor'] = 3 
            if audio_on: snd_laser.play() # Reproducir sonido Pew!

        if estado['cooldown_arma'] > 0: estado['cooldown_arma'] -= 1

        estado['distancia'] += estado['velocidad_base'] / 10
        estado['velocidad_base'] = 5.0 + (estado['distancia'] / 100)

        if random.random() < (0.02 + (estado['velocidad_base'] / 500)):
            estado['asteroides'].append(crear_asteroide(estado['velocidad_base']))

        for i in range(len(estrellas)):
            efecto_velocidad = estado['velocidad_base'] - (eje_y * 3) 
            estrellas[i] = (estrellas[i][0], estrellas[i][1] + estrellas[i][2] + (efecto_velocidad/2), estrellas[i][2])
            if estrellas[i][1] > ALTO: estrellas[i] = (random.randint(0, ANCHO), 0, estrellas[i][2])

        for disparo in estado['disparos'][:]:
            disparo['y'] += disparo['vy']
            if disparo['y'] < -10:
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

            # IMPACTO Y SONIDO DE EXPLOSIÓN
            if ((estado['pos'][0] - ast['x'])**2 + (estado['pos'][1] - ast['y'])**2)**0.5 < ast['radio'] + 15: 
                estado['chocado'] = True
                estado['temblor'] = 30       
                estado['flash_rojo'] = True  
                if audio_on: snd_choque.play() # Reproducir explosión

            if ast['y'] > ALTO + 50:
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

    for disparo in estado['disparos']:
        pygame.draw.rect(pantalla_virtual, LASER, (int(disparo['x'] - 2), int(disparo['y']), 4, 15))
        pygame.draw.rect(pantalla_virtual, (255, 150, 150), (int(disparo['x'] - 1), int(disparo['y'] + 2), 2, 11))

    for ast in estado['asteroides']:
        pygame.draw.circle(pantalla_virtual, ASTEROIDE, (int(ast['x']), int(ast['y'])), ast['radio'])
        pygame.draw.circle(pantalla_virtual, ASTEROIDE_BORDE, (int(ast['x']), int(ast['y'])), ast['radio'], 3)
        pygame.draw.circle(pantalla_virtual, ASTEROIDE_BORDE, (int(ast['x'] - ast['radio']/3), int(ast['y'] - ast['radio']/3)), int(ast['radio']/4))

    nx, ny = estado['pos'][0], estado['pos'][1]
    puntos_nave = [(nx, ny - 25), (nx - 20, ny + 15), (nx, ny + 5), (nx + 20, ny + 15)]
    pygame.draw.polygon(pantalla_virtual, NAVE, puntos_nave)
    
    if not estado['chocado']:
        largo_fuego = 35 if eje_y < -0.15 else (5 if eje_y > 0.15 else 15)
        puntos_fuego = [(nx - 10, ny + 10), (nx, ny + 10 + largo_fuego + random.randint(0, 5)), (nx + 10, ny + 10)]
        pygame.draw.polygon(pantalla_virtual, NAVE_PROPULSOR, puntos_fuego)

    fuente = pygame.font.SysFont("Courier New", 20, bold=True)
    pantalla_virtual.blit(fuente.render(f"DIST: {estado['distancia']:.0f}m", True, BLANCO), (20, 20))
    pantalla_virtual.blit(fuente.render(f"CAZA: {estado['destruidos']}", True, (255, 100, 100)), (ANCHO - 150, 20))
    pantalla_virtual.blit(fuente.render(f"RÉCORD: {record_historico:.0f}m", True, DORADO), (ANCHO // 2 - 80, 20))

    if estado['chocado']:
        fuente_grande = pygame.font.SysFont("Courier New", 50, bold=True)
        pantalla_virtual.blit(fuente_grande.render("¡NAVE DESTRUIDA!", True, (255, 50, 50)), (ANCHO//2 - 210, ALTO//2 - 60))
        if estado['nuevo_record']:
            pantalla_virtual.blit(fuente_grande.render("¡NUEVO RÉCORD!", True, DORADO), (ANCHO//2 - 180, ALTO//2 - 10))

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