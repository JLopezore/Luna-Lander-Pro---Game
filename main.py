import pygame
import sys
import random
import time
import os

# --- CONFIGURACIÓN ---
pygame.init()
pygame.joystick.init()

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("IHC Lab: Supervivencia Háptica")
reloj = pygame.time.Clock()

# Hardware
if pygame.joystick.get_count() == 0:
    print("Conecta el joystick Acteck.")
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
            with open("record_ihc.txt", "r") as f:
                return float(f.read().strip())
        except:
            return 0.0
    return 0.0

def guardar_record(nuevo_record):
    with open("record_ihc.txt", "w") as f:
        f.write(str(nuevo_record))

record_historico = cargar_record()

# --- ESTADO DEL JUEGO ---
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
        'nuevo_record': False
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

    # 1. ENTRADAS (Joystick)
    eje_x = mi_joystick.get_axis(0)
    eje_y = mi_joystick.get_axis(1)
    gatillo_disparo = mi_joystick.get_button(0)
    boton_reinicio = mi_joystick.get_button(1)
    
    if boton_reinicio: 
        # Detener cualquier vibración residual si reinicia rápido
        try: mi_joystick.stop_rumble() 
        except: pass
        estado = reiniciar_carrera()

    # 2. LÓGICA Y FÍSICA
    if not estado['chocado']:
        # Movimiento
        if abs(eje_x) > 0.15: estado['pos'][0] += eje_x * 8
        if abs(eje_y) > 0.15: estado['pos'][1] += eje_y * 6

        estado['pos'][0] = max(20, min(ANCHO - 20, estado['pos'][0]))
        estado['pos'][1] = max(50, min(ALTO - 50, estado['pos'][1]))

        # Disparos y Micro-Vibración
        if gatillo_disparo and estado['cooldown_arma'] == 0:
            estado['disparos'].append({'x': estado['pos'][0], 'y': estado['pos'][1] - 25, 'vy': -15})
            estado['cooldown_arma'] = 12
            
            # IHC: Micro-retroceso al disparar (Baja frec, Alta frec, Duración ms)
            try: mi_joystick.rumble(0.0, 0.3, 50) 
            except: pass

        if estado['cooldown_arma'] > 0:
            estado['cooldown_arma'] -= 1

        # Progresión
        estado['distancia'] += estado['velocidad_base'] / 10
        estado['velocidad_base'] = 5.0 + (estado['distancia'] / 100)

        # Generar asteroides
        if random.random() < (0.02 + (estado['velocidad_base'] / 500)):
            estado['asteroides'].append(crear_asteroide(estado['velocidad_base']))

        # Estrellas (Fondo)
        for i in range(len(estrellas)):
            efecto_velocidad = estado['velocidad_base'] - (eje_y * 3) 
            estrellas[i] = (estrellas[i][0], estrellas[i][1] + estrellas[i][2] + (efecto_velocidad/2), estrellas[i][2])
            if estrellas[i][1] > ALTO:
                estrellas[i] = (random.randint(0, ANCHO), 0, estrellas[i][2])

        # Láseres y destrucción
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

        # Asteroides y Colisión (Game Over)
        for ast in estado['asteroides'][:]:
            ast['x'] += ast['vx']
            ast['y'] += ast['vy'] - (eje_y * 2) 

            # Detección de impacto fatal
            if ((estado['pos'][0] - ast['x'])**2 + (estado['pos'][1] - ast['y'])**2)**0.5 < ast['radio'] + 15: 
                if not estado['chocado']: # Solo ejecutar esto una vez al chocar
                    estado['chocado'] = True
                    # IHC: Feedback de impacto masivo (Motores al 100% por 800ms)
                    try: mi_joystick.rumble(1.0, 1.0, 800)
                    except: pass

            if ast['y'] > ALTO + 50:
                estado['asteroides'].remove(ast)
                estado['esquivados'] += 1

    # Procesar Récord al perder
    if estado['chocado'] and not estado['log_guardado']:
        registrar_carrera(estado['distancia'], estado['esquivados'], estado['destruidos'])
        
        if estado['distancia'] > record_historico:
            record_historico = estado['distancia']
            guardar_record(record_historico)
            estado['nuevo_record'] = True
            
        estado['log_guardado'] = True

    # 3. RENDERIZADO VISUAL
    pantalla.fill(FONDO)
    
    for e in estrellas:
        pygame.draw.circle(pantalla, BLANCO, (int(e[0]), int(e[1])), int(e[2]))

    for disparo in estado['disparos']:
        pygame.draw.rect(pantalla, LASER, (int(disparo['x'] - 2), int(disparo['y']), 4, 15))
        pygame.draw.rect(pantalla, (255, 150, 150), (int(disparo['x'] - 1), int(disparo['y'] + 2), 2, 11))

    for ast in estado['asteroides']:
        pygame.draw.circle(pantalla, ASTEROIDE, (int(ast['x']), int(ast['y'])), ast['radio'])
        pygame.draw.circle(pantalla, ASTEROIDE_BORDE, (int(ast['x']), int(ast['y'])), ast['radio'], 3)
        pygame.draw.circle(pantalla, ASTEROIDE_BORDE, (int(ast['x'] - ast['radio']/3), int(ast['y'] - ast['radio']/3)), int(ast['radio']/4))

    nx, ny = estado['pos'][0], estado['pos'][1]
    puntos_nave = [(nx, ny - 25), (nx - 20, ny + 15), (nx, ny + 5), (nx + 20, ny + 15)]
    pygame.draw.polygon(pantalla, NAVE, puntos_nave)
    
    largo_fuego = 15
    if eje_y < -0.15: largo_fuego = 35 
    elif eje_y > 0.15: largo_fuego = 5 
    
    if not estado['chocado']:
        puntos_fuego = [(nx - 10, ny + 10), (nx, ny + 10 + largo_fuego + random.randint(0, 5)), (nx + 10, ny + 10)]
        pygame.draw.polygon(pantalla, NAVE_PROPULSOR, puntos_fuego)

    # 4. INTERFAZ (HUD) Y TEXTOS
    fuente = pygame.font.SysFont("Courier New", 20, bold=True)
    
    txt_dist = fuente.render(f"DIST: {estado['distancia']:.0f}m", True, BLANCO)
    txt_dest = fuente.render(f"CAZA: {estado['destruidos']}", True, (255, 100, 100))
    txt_record = fuente.render(f"RÉCORD: {record_historico:.0f}m", True, DORADO)
    
    pantalla.blit(txt_dist, (20, 20))
    pantalla.blit(txt_dest, (ANCHO - 150, 20))
    pantalla.blit(txt_record, (ANCHO // 2 - 80, 20))

    if estado['chocado']:
        fuente_grande = pygame.font.SysFont("Courier New", 50, bold=True)
        txt_fin = fuente_grande.render("¡NAVE DESTRUIDA!", True, (255, 50, 50))
        txt_res = fuente.render(f"Distancia: {estado['distancia']:.0f}m | Destruidos: {estado['destruidos']}", True, BLANCO)
        txt_inst = fuente.render("Presiona Botón 1 para reintentar", True, (150, 150, 150))
        
        pantalla.blit(txt_fin, txt_fin.get_rect(center=(ANCHO//2, ALTO//2 - 60)))
        
        if estado['nuevo_record']:
            txt_nuevo_record = fuente_grande.render("¡NUEVO RÉCORD!", True, DORADO)
            pantalla.blit(txt_nuevo_record, txt_nuevo_record.get_rect(center=(ANCHO//2, ALTO//2 - 10)))
            pantalla.blit(txt_res, txt_res.get_rect(center=(ANCHO//2, ALTO//2 + 40)))
            pantalla.blit(txt_inst, txt_inst.get_rect(center=(ANCHO//2, ALTO//2 + 80)))
        else:
            pantalla.blit(txt_res, txt_res.get_rect(center=(ANCHO//2, ALTO//2 + 10)))
            pantalla.blit(txt_inst, txt_inst.get_rect(center=(ANCHO//2, ALTO//2 + 50)))

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()