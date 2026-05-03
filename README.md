***

# UNSIS Space Lab: Lunar Lander Pro - Prototipo de Interacción Humano-Computadora

Este proyecto es un entorno de pruebas interactivo de aterrizaje lunar desarrollado en Python y Pygame, diseñado para evaluar conceptos fundamentales de **Interacción Humano-Computadora (IHC)** mediante el uso de periféricos de entrada genéricos (joysticks Acteck) en entornos aislados con Docker.

## 🧠 Conceptos de IHC Aplicados

A diferencia de un videojuego convencional, este sistema está programado para documentar, analizar y compensar la interacción entre el usuario y las limitaciones del hardware:

1. **Filtro Asimétrico y Mapeo de Hardware (Calibración):** Se implementó un algoritmo de normalización matemática con zonas muertas asimétricas (0.15 en ambos lados) que compensa la respuesta no lineal del joystick Acteck:
    - Eje X izquierdo: $(x + 0.15) / 0.85$ para mayor sensibilidad en giro izquierdo.
    - Eje X derecho: $\min(1.0, (x - 0.15) / 0.45)$ para evitar saturación en giro derecho.
    - Eje Y: Zona muerta de 0.15 para activaciones intencionales sin ruido analógico.
    
    Esto restaura el 100% de usabilidad sin requerir recalibración de hardware.

2. **Retroalimentación Multimodal Compensatoria:** Al carecer de soporte de *Force Feedback* a nivel Kernel para hardware genérico, se aplicó un principio heurístico de compensación:
    * **Visual:** Efectos de *Screen Shake* (temblor de cámara) en colisiones y destellos para indicar cambios críticos de estado.
    * **Auditiva:** Generación de audio sintético en tiempo real mediante ondas senoidales y ruido blanco (propulsor, choque, éxito, ambiente) para retroalimentación táctil-auditiva sin depender de archivos externos.

3. **Sistema de Puntuación y Persistencia:** Integración de un modelo de puntaje acumulativo (100 puntos base + bono por combustible restante) con almacenamiento persistente de récord histórico (`record_ihc.txt`) visible en el HUD para medir la curva de aprendizaje y motivación extrínseca.

4. **Telemetría e Identidad Institucional:** Almacenamiento automático de resultados en `resultados_ihc.txt` (timestamp, nivel, resultado, velocidad, combustible). Se incluye una base espacial visual con logo UNSIS (PNG) y respaldo a texto para mantener branding institucional.

5. **Mitigación de Input Lag:** Configuración de buffer de ALSA a 1024 bytes para estabilidad, combinado con filtro de ejes en tiempo real para evitar bloqueos en la lectura de entradas físicas.

## ⚙️ Requisitos del Sistema

* **Sistema Operativo:** Distribución Linux (probado en entornos basados en Debian/Ubuntu).
* **Contenedor:** Docker y Docker Compose.
* **Hardware:** Joystick analógico genérico (ej. Acteck AGJ-4000) conectado por USB.

## 🚀 Instrucciones de Ejecución

Debido a que el proyecto se ejecuta dentro de un contenedor Docker aislado, es necesario otorgar permisos temporales al sistema gráfico (X11) y asegurar que el dispositivo de audio no esté bloqueado por el anfitrión.

1. **Liberar canal de audio:** Asegúrate de cerrar reproductores de música o navegadores en el sistema anfitrión que puedan estar ocupando la tarjeta de sonido (`/dev/snd`).
2. **Otorgar permisos de video:** En la terminal de tu máquina local, ejecuta:
   ```bash
   xhost +local:docker
   ```
3. **Construir y levantar el contenedor:** Navega a la carpeta del proyecto y ejecuta:
   ```bash
   docker compose up --build
   ```

## 🎮 Controles de la Interfaz

### Joystick Acteck
* **Palanca X (Izquierda/Derecha):** Movimiento lateral de la nave (con filtro asimétrico para máxima precisión).
* **Palanca Y (Arriba/Abajo):** Empujar hacia arriba activa propulsores; hacia abajo no tiene efecto en vuelo.
* **Botón 0 (Gatillo Principal):** Enciende el motor/propulsor.
* **Botón 1 (Botón Secundario):** Reinicia el nivel actual o avanza al siguiente.

### Controles Alternativos (Teclado)
* **Flechas o A/D:** Movimiento lateral.
* **Arriba, Espacio o W:** Propulsores.
* **Enter:** Reinicia o avanza al siguiente nivel.
* **R:** Reinicia rápido.
***