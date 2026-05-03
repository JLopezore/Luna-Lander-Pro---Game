***

# UNSIS Space Lab: Prototipo de Interacción Humano-Computadora

Este proyecto es un entorno de pruebas interactivo desarrollado en Python y Pygame, diseñado para evaluar conceptos fundamentales de **Interacción Humano-Computadora (IHC)** mediante el uso de periféricos de entrada genéricos (joysticks) en entornos aislados con Docker.

## 🧠 Conceptos de IHC Aplicados

A diferencia de un videojuego convencional, este sistema está programado para documentar, analizar y compensar la interacción entre el usuario y las limitaciones del hardware:

1. **Filtro Asimétrico y Mapeo de Hardware (Calibración):** Se implementó un algoritmo de normalización matemática con zonas muertas variables para compensar la degradación física del potenciómetro del joystick (específicamente una lectura máxima de 6080 en el eje X derecho). Esto restaura el 100% de la usabilidad del software sin requerir reemplazo de hardware.
2. **Retroalimentación Multimodal Compensatoria:** Al carecer de soporte de *Force Feedback* a nivel Kernel para hardware genérico, se aplicó un principio heurístico de compensación:
    * **Visual:** Efectos de *Screen Shake* (temblor de cámara) y destellos de pantalla para indicar cambios críticos de estado (colisiones).
    * **Auditiva:** Generación de audio sintético en tiempo real mediante ondas senoidales y ruido blanco para confirmar acciones (disparos) sin depender de archivos multimedia externos, optimizando el tamaño del contenedor.
3. **Optimización de Carga Cognitiva:** Rediseño de la interfaz a una resolución de 1024x768 para reducir la densidad visual. Se implementó un diseño de "plataforma" de alto contraste para destacar la identidad institucional en un entorno visualmente saturado.
4. **Persistencia y Motivación:** Integración de un sistema de guardado de telemetría (`resultados_combate_ihc.txt`) y un récord histórico visible en el HUD para medir la curva de aprendizaje y apelar a la motivación extrínseca del usuario.
5. **Mitigación de Input Lag:** Configuración de la tasa de muestreo y tamaño del buffer de ALSA (`pre_init` a 512 bytes) para evitar bloqueos en el hilo principal que causen latencia en la lectura de las entradas físicas.

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

* **Palanca Analógica (Ejes X/Y):** Control de navegación espacial (con sensibilidad ajustada asimétricamente por software).
* **Botón 0 (Gatillo Principal):** Accionador de láser sintético.
* **Botón 1 (Botón Secundario):** Reinicio inmediato del estado del sistema.
***