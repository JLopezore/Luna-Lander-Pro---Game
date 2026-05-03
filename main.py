import pygame
import sys
import random
import time
import os
import wave
import math
import struct

# --- IHC: GENERACIÓN SINTÉTICA DE AUDIO MEJORADA ---
def crear_archivos_de_sonido():
    # 1. Propulsor (Se mantiene igual)
    if not os.path.exists("propulsor.wav"):
        with wave.open("propulsor.wav", "w") as f:
            f.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
            for i in range(int(44100 * 0.2)): 
                val = int(4000 * random.uniform(-1.0, 1.0))
                f.writeframes(struct.pack('<h', val))
                
    # 2. Choque V2 (Más largo, más fuerte y con efecto de retumbar "rumble")
    if not os.path.exists("choque_v2.wav"):
        with wave.open("choque_v2.wav", "w") as f:
            f.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
            for i in range(int(44100 * 1.5)): # Aumentado a 1.5 segundos
                volumen = 1.0 - (i / (44100 * 1.5))
                # Añadimos un oscilador de baja frecuencia (15Hz) para hacer que el ruido "tiemble"
                modulador = math.sin(2 * math.pi * 15 * (i / 44100.0))
                val = int(22000 * volumen * random.uniform(-1.0, 1.0) * (0.5 + 0.5 * modulador))
                f.writeframes(struct.pack('<h', val))

    # 3. Éxito V2 (Acorde de Do Mayor para sensación de triunfo)
    if not os.path.exists("exito_v2.wav"):
        with wave.open("exito_v2.wav", "w") as f:
            f.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
            for i in range(int(44100 * 2.0)): # Aumentado a 2.0 segundos
                volumen = 1.0 - (i / (44100 * 2.0))
                # Mezclamos tres frecuencias (C5, E5, G5)
                onda1 = math.sin(2 * math.pi * 523.25 * (i / 44100.0))
                onda2 = math.sin(2 * math.pi * 659.25 * (i / 44100.0))
                onda3 = math.sin(2 * math.pi * 783.99 * (i / 44100.0))
                val = int(8000 * volumen * (onda1 + onda2 + onda3) / 3)
                f.writeframes(struct.pack('<h', val))

crear_archivos_de_sonido()

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.joystick.init()

try:
    pygame.mixer.init()
    snd_prop = pygame.mixer.Sound("propulsor.wav")
    snd_choque = pygame.mixer.Sound("choque_v2.wav")
    snd_exito = pygame.mixer.Sound("exito_v2.wav")
    snd_prop.set_volume(0.3)
    snd_choque.set_volume(0.8) # Más volumen al choque
    snd_exito.set_volume(0.5)
    
    canal_motor = pygame.mixer.Channel(0) 
    audio_on = True
except Exception as e:
    print(f"Advertencia de Audio: {e}")
    audio_on = False

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pantalla_virtual = pygame.Surface((ANCHO, ALTO)) # Nueva superficie para el Screen Shake
pygame.display.set_caption("IHC Lab: Lunar Lander + Shake & Audio")
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

# --- PANTALLA DE DETECCIÓN ---
usar_joystick = False
tiempo_inicio = pygame.time.get_ticks()
fuente_espera = pygame.font.SysFont("Courier New", 24, bold=True)

while True:
    pantalla.fill(FONDO)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.joystick.quit()
    pygame.joystick.init()

    if pygame.joystick.get_count() > 0:
        mi_joystick = pygame.joystick.Joystick(0)
        mi_joystick.init()
        usar_joystick = True
        break

    tiempo_actual = pygame.time.get_ticks()
    tiempo_restante = 10 - (tiempo_actual - tiempo_inicio) // 1000
    if tiempo_restante <= 0: break

    txt_buscando = fuente_espera.render(f"Buscando Joystick... {tiempo_restante}s", True, NARANJA)
    txt_skip = fuente_espera.render("Presiona [ENTER] para usar TECLADO", True, (150, 150, 150))
    pantalla.blit(txt_buscando, txt_buscando.get_rect(center=(ANCHO // 2, ALTO // 2 - 20)))
    pantalla.blit(txt_skip, txt_skip.get_rect(center=(ANCHO // 2, ALTO // 2 + 30)))
    
    if pygame.key.get_pressed()[pygame.K_RETURN]: break

    pygame.display.flip()
    reloj.tick(30)

# --- GENERACIÓN DE AMBIENTE ---
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

def registrar_resultado(nivel, resultado, vel_final, fuel_gastado):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("resultados_ihc.txt", "a") as f:
        f.write(f"[{timestamp}] Nivel: {nivel} | Res: {resultado} | Vel: {vel_final:.2f} | Fuel: {fuel_gastado:.1f}%\n")

def iniciar_nivel(nivel):
    plat_ancho = max(30, 100 - (nivel - 1) * 15)
    viento = 0.0 if nivel == 1 else random.uniform(-0.03, 0.03) * nivel
    gravedad = 0.12 + (nivel - 1) * 0.005
    max_fuel = max(40, 100 - (nivel - 1) * 10)
    
    if audio_on and canal_motor.get_busy(): canal_motor.stop() 
    
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
        'gravedad': gravedad,
        'temblor': 0  # <--- Agregamos la variable de Screen Shake
    }

estado = iniciar_nivel(1)

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
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: 
            corriendo = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN or evento.key == pygame.K_r:
                if estado['exito']: estado = iniciar_nivel(estado['nivel'] + 1)
                else: estado = iniciar_nivel(estado['nivel'])
        if evento.type == pygame.JOYBUTTONDOWN and usar_joystick:
            if evento.button == 1:
                if estado['exito']: estado = iniciar_nivel(estado['nivel'] + 1)
                else: estado = iniciar_nivel(estado['nivel'])

    eje_x = 0.0
    gatillo = False
    teclas = pygame.key.get_pressed()

    if usar_joystick:
        eje_x = mi_joystick.get_axis(0)
        gatillo = mi_joystick.get_button(0)

    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: eje_x = -1.0
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: eje_x = 1.0
    if teclas[pygame.K_UP] or teclas[pygame.K_SPACE] or teclas[pygame.K_w]: gatillo = True

    motor_activo = gatillo and estado['combustible'] > 0 and not estado['terminado']
    
    if audio_on:
        if motor_activo:
            if not canal_motor.get_busy():
                canal_motor.play(snd_prop, loops=-1) 
        else:
            if canal_motor.get_busy():
                canal_motor.stop() 

    if not estado['terminado']:
        estado['vel'][1] += estado['gravedad']
        estado['vel'][0] += estado['viento']
        
        if motor_activo:
            estado['vel'][1] -= 0.35
            estado['combustible'] -= 0.5
            
        if abs(eje_x) > 0.15: 
            estado['vel'][0] += eje_x * 0.15
        
        estado['vel'][0] *= 0.98
        estado['pos'][0] += estado['vel'][0]
        estado['pos'][1] += estado['vel'][1]

        nave_rect = pygame.Rect(estado['pos'][0] - 15, estado['pos'][1] - 20, 30, 40)
        plat_x = ANCHO // 2 - estado['plat_ancho'] // 2
        plat_rect = pygame.Rect(plat_x, ALTO - 55, estado['plat_ancho'], 10)
        
        if nave_rect.colliderect(plat_rect):
            estado['terminado'] = True
            if canal_motor.get_busy(): canal_motor.stop()
            
            if estado['vel'][1] < 2.5:
                estado['mensaje'], estado['color_msg'] = "ATERRIZAJE PERFECTO", VERDE
                estado['exito'] = True
                if audio_on: snd_exito.play()
            else:
                estado['mensaje'], estado['color_msg'] = "CÁPSULA DESTRUIDA", ROJO
                estado['temblor'] = 30 # <--- Activamos el temblor de pantalla (30 frames)
                if audio_on: snd_choque.play()
                
        elif estado['pos'][1] > ALTO - 30 or estado['pos'][0] < 0 or estado['pos'][0] > ANCHO:
            estado['terminado'] = True
            estado['mensaje'], estado['color_msg'] = "CRASH / FUERA DE RUTA", ROJO
            estado['temblor'] = 30 # <--- Activamos el temblor de pantalla
            if canal_motor.get_busy(): canal_motor.stop()
            if audio_on: snd_choque.play()

    if estado['terminado'] and not estado['log_guardado']:
        fuel_usado = estado['max_combustible'] - estado['combustible']
        registrar_resultado(estado['nivel'], estado['mensaje'], estado['vel'][1], fuel_usado)
        estado['log_guardado'] = True

    # --- RENDERIZADO VISUAL (AHORA SOBRE PANTALLA VIRTUAL) ---
    dibujar_fondo(pantalla_virtual)
    dibujar_luna(pantalla_virtual, estado['plat_ancho'])
    dibujar_nave(pantalla_virtual, estado['pos'][0], estado['pos'][1], motor_activo)
    
    fuente = pygame.font.SysFont("Courier New", 18, bold=True)
    
    porcentaje_fuel = estado['combustible'] / estado['max_combustible']
    color_bar = VERDE if porcentaje_fuel > 0.3 else ROJO
    pygame.draw.rect(pantalla_virtual, (50, 50, 50), (20, 50, 200, 20))
    pygame.draw.rect(pantalla_virtual, color_bar, (20, 50, porcentaje_fuel * 200, 20))
    pantalla_virtual.blit(fuente.render(f"FUEL: {estado['combustible']:.0f}/{estado['max_combustible']}", True, (255, 255, 255)), (20, 75))
    
    color_vel = VERDE if estado['vel'][1] < 2.5 else (255, 255, 255)
    txt_vel = fuente.render(f"VELOCIDAD: {estado['vel'][1]:.2f}", True, color_vel)
    pantalla_virtual.blit(txt_vel, (20, 20))

    txt_control = fuente.render("MODO: JOYSTICK" if usar_joystick else "MODO: TECLADO", True, (150, 150, 150))
    pantalla_virtual.blit(txt_control, (20, ALTO - 30))

    txt_nivel = fuente.render(f"NIVEL: {estado['nivel']}", True, AZUL)
    pantalla_virtual.blit(txt_nivel, (ANCHO - 120, 20))
    
    if estado['viento'] != 0:
        dir_viento = "->" if estado['viento'] > 0 else "<-"
        txt_viento = fuente.render(f"VIENTO: {dir_viento} {abs(estado['viento']):.3f}", True, NARANJA)
        pantalla_virtual.blit(txt_viento, (ANCHO - 180, 50))

    if estado['mensaje']:
        fuente_msg = pygame.font.SysFont("Courier New", 40, bold=True)
        txt_msg = fuente_msg.render(estado['mensaje'], True, estado['color_msg'])
        rect_msg = txt_msg.get_rect(center=(ANCHO // 2, ALTO // 2 - 30))
        pantalla_virtual.blit(txt_msg, rect_msg)
        
        instruccion = "Presiona [ENTER] o Botón 1 -> SIGUIENTE NIVEL" if estado['exito'] else "Presiona [ENTER] o Botón 1 -> REINTENTAR"
        txt_inst = fuente.render(instruccion, True, (200, 200, 200))
        rect_inst = txt_inst.get_rect(center=(ANCHO // 2, ALTO // 2 + 30))
        pantalla_virtual.blit(txt_inst, rect_inst)

    # --- LÓGICA DE SCREEN SHAKE ---
    offset_x, offset_y = 0, 0
    if estado['temblor'] > 0:
        intensidad = estado['temblor'] // 2
        offset_x = random.randint(-intensidad, intensidad)
        offset_y = random.randint(-intensidad, intensidad)
        estado['temblor'] -= 1

    # Plasmar la pantalla virtual en la pantalla real con el desfase
    pantalla.fill((0, 0, 0)) 
    pantalla.blit(pantalla_virtual, (offset_x, offset_y))

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()