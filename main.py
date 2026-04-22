import pygame
import sys

# --- CONFIGURACIÓN DE IHC ---
pygame.init()
pygame.joystick.init()

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("IHC Lab: Lunar Lander con Reinicio")
reloj = pygame.time.Clock()

# Detección de Joystick
if pygame.joystick.get_count() == 0:
    print("Error: Conecta el Acteck AGJ-4000.")
    sys.exit()

mi_joystick = pygame.joystick.Joystick(0)
mi_joystick.init()

# --- VARIABLES GLOBALES ---
BLANCO = (255, 255, 255)
GRIS = (30, 30, 30)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
plataforma = pygame.Rect(ANCHO // 2 - 50, ALTO - 50, 100, 20)

def reiniciar_juego():
    """Restablece el estado inicial del sistema (IHC: Recuperabilidad)"""
    return {
        "pos": [ANCHO // 2, 50],
        "vel": [0, 0],
        "terminado": False,
        "mensaje": "",
        "color_msg": BLANCO
    }

# Inicializar primer estado
estado = reiniciar_juego()

corriendo = True
while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

    # 1. ENTRADAS (Mapeo de hardware)
    eje_x = mi_joystick.get_axis(0)
    gatillo = mi_joystick.get_button(0)      # Propulsor
    boton_reset = mi_joystick.get_button(1)  # Botón de pulgar para reiniciar
    
    # Lógica de Reinicio (IHC: El usuario tiene el control)
    if boton_reset:
        estado = reiniciar_juego()

    # 2. FÍSICA (Solo si no ha terminado)
    if not estado["terminado"]:
        estado["vel"][1] += 0.1  # Gravedad
        
        if gatillo:
            estado["vel"][1] -= 0.4 # Impulso
            
        if abs(eje_x) > 0.15:
            estado["vel"][0] += eje_x * 0.2
            
        estado["vel"][0] *= 0.99 # Fricción
        estado["pos"][0] += estado["vel"][0]
        estado["pos"][1] += estado["vel"][1]

        # 3. DETECCIÓN DE COLISIONES
        nave_rect = pygame.Rect(estado["pos"][0], estado["pos"][1], 30, 30)
        
        if nave_rect.colliderect(plataforma):
            estado["terminado"] = True
            if estado["vel"][1] < 3.0:
                estado["mensaje"], estado["color_msg"] = "¡ATERRIZAJE EXITOSO!", VERDE
            else:
                estado["mensaje"], estado["color_msg"] = "¡CRASH! MUY RÁPIDO", ROJO
            estado["vel"] = [0, 0]

        if estado["pos"][1] > ALTO or estado["pos"][0] < 0 or estado["pos"][0] > ANCHO:
            estado["terminado"] = True
            estado["mensaje"], estado["color_msg"] = "FUERA DE RANGO", ROJO

    # 4. RENDERIZADO
    pantalla.fill(GRIS)
    pygame.draw.rect(pantalla, VERDE, plataforma)
    
    color_nave = (255, 165, 0) if gatillo else BLANCO
    pygame.draw.rect(pantalla, color_nave, (estado["pos"][0], estado["pos"][1], 30, 30))
    
    # UI de Instrucciones
    fuente = pygame.font.SysFont("Arial", 18)
    instrucciones = fuente.render("Presiona el botón del pulgar para reiniciar", True, (150, 150, 150))
    pantalla.blit(instrucciones, (10, ALTO - 30))
    
    if estado["mensaje"]:
        fuente_msg = pygame.font.SysFont("Arial", 48, bold=True)
        txt_msg = fuente_msg.render(estado["mensaje"], True, estado["color_msg"])
        pantalla.blit(txt_msg, (ANCHO // 2 - 200, ALTO // 2))

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()