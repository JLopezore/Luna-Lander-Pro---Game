import pygame
import sys

# Inicializar motor y submódulo de joystick
pygame.init()
pygame.joystick.init()

# Configuraciones de pantalla
ANCHO = 800
ALTO = 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Laboratorio IHC - Lunar Lander")
reloj = pygame.time.Clock()

# Detección del hardware
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
if not joysticks:
    print("Por favor, conecta el Acteck AGJ-4000.")
    sys.exit()

mi_joystick = joysticks[0]
mi_joystick.init()
print(f"Hardware detectado: {mi_joystick.get_name()}")

# --- VARIABLES DE LA NAVE ---
nave_x = ANCHO // 2
nave_y = ALTO // 2
velocidad = 7
tamaño_nave = 40

# IHC: Zona muerta (Deadzone)
# Los joysticks físicos nunca regresan exactamente a 0.0, siempre tienen un micro-desvío.
# Ignoramos cualquier valor menor a 0.15 para que la nave no se mueva sola.
zona_muerta = 0.15 

# Bucle principal del juego
corriendo = True
while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False
            
    # 1. Leer entradas físicas
    eje_x = mi_joystick.get_axis(0)
    eje_y = mi_joystick.get_axis(1)
    gatillo = mi_joystick.get_button(0)

    # 2. Lógica de movimiento (Aplicando zona muerta)
    if abs(eje_x) > zona_muerta:
        nave_x += eje_x * velocidad
        
    if abs(eje_y) > zona_muerta:
        nave_y += eje_y * velocidad

    # 3. Límites de la pantalla (Para que no se escape)
    if nave_x < 0: nave_x = 0
    if nave_x > ANCHO - tamaño_nave: nave_x = ANCHO - tamaño_nave
    if nave_y < 0: nave_y = 0
    if nave_y > ALTO - tamaño_nave: nave_y = ALTO - tamaño_nave

    # 4. Feedback Visual (IHC)
    # Cambiamos el color de la nave si presiona el gatillo (simulando propulsores)
    if gatillo:
        color_nave = (255, 100, 100) # Rojo (Acelerando)
    else:
        color_nave = (100, 200, 255) # Azul (Modo reposo)

    # 5. Renderizado
    pantalla.fill((30, 30, 30)) # Limpiar rastro anterior
    pygame.draw.rect(pantalla, color_nave, (nave_x, nave_y, tamaño_nave, tamaño_nave))
    
    # Dibujar las coordenadas en la terminal para que veas los valores en crudo
    print(f"X: {eje_x:.2f} | Y: {eje_y:.2f} | Gatillo: {gatillo}", end="\r")

    pygame.display.flip()
    reloj.tick(60) # Mantener a 60 FPS

pygame.quit()