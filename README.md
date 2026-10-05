# JARVIS HUD en vivo

HUD de los lentes JARVIS que corre en vivo en tu teléfono. La cámara, la detección de objetos, las alertas y la caja negra funcionan dentro del teléfono: el video no sale de ahí.

## Qué hace

| Función | Cómo funciona | Equivale en los lentes a |
|---|---|---|
| Detección en vivo | COCO-SSD (TensorFlow.js) en el teléfono: personas, vehículos, animales y ~80 objetos | YOLO en tu PC |
| Distancia aproximada | Calculada con la altura típica de cada cosa y la cámara | Sensor VL53L5CX (Fase 3) |
| “Se acerca” | Sigue cada objeto y avisa si crece rápido en la imagen | Alerta de JARVIS |
| Pitido direccional | Suena del lado del peligro (con audífonos) y vibra en Android | Motores hápticos en las patillas |
| Voz y comandos | “JARVIS, qué ves”, “briefing”, “guarda eso”, “silencio”, “hora” | Conducción ósea + palabra de activación |
| Briefing | Hora, batería, clima real (Open-Meteo) y lo que tienes enfrente | Briefing de la mañana |
| Caja negra | Grabación en bucle de ~30 s con el HUD, caras pixeladas y sello SHA-256 | microSD en los lentes |
| Describir | Envía un cuadro a Ollama en tu PC (opcional) | El cerebro local |

## Paso 1: Publicarla gratis con GitHub Pages (10 minutos)

1. Crea una cuenta gratis en **github.com**.
2. Arriba a la derecha toca **+ → New repository**.
   - Nombre: `jarvis-hud`
   - Visibilidad: **Public** (GitHub Pages gratis lo pide).
   - Toca **Create repository**.
3. En la página del repositorio toca **uploading an existing file** (o **Add file → Upload files**).
4. Arrastra estos 3 archivos: `index.html`, `manifest.json`, `icon.svg`. Toca **Commit changes**.
5. Ve a **Settings → Pages**.
   - En **Source** elige **Deploy from a branch**.
   - En **Branch** elige **main** y la carpeta **/ (root)**. Toca **Save**.
6. Espera 1–2 minutos y recarga esa página: aparece tu link, algo como
   `https://TU-USUARIO.github.io/jarvis-hud/`

## Paso 2: Usarla en tu teléfono

1. Abre el link en **Safari** (iPhone) o **Chrome** (Android).
2. Espera a que diga **Iniciar JARVIS** (descarga el modelo de ~5 MB la primera vez).
3. Toca **Iniciar JARVIS** y acepta los permisos de **cámara** y **movimiento** (brújula).
4. Ponte audífonos para oír de qué lado vienen las alertas.

Para que se abra a pantalla completa como una app:
- **iPhone:** botón Compartir → **Agregar a inicio**.
- **Android:** menú ⋮ → **Agregar a la pantalla principal**.

### Comandos de voz

Toca **Hablar** y di la orden (no hace falta decir “JARVIS” con el botón):

- **“¿Qué ves?”**: resumen de lo que tienes enfrente.
- **“Briefing”**: hora, batería, clima y entorno. La primera vez pide tu ubicación.
- **“Guarda eso”**: sella el evento (foto con HUD y, si la caja negra está activa, los últimos segundos de video).
- **“Describe”**: descripción completa usando tu PC (Paso 3).
- **“Silencio”** / **“Activa alertas”** / **“Hora”**.

En Android puedes activar **Escucha continua** en Ajustes y hablarle sin tocar nada: “JARVIS, ¿qué ves?”.

## Paso 3 (opcional): Conectar el cerebro de tu PC

Esto hace que **Describir** y las preguntas libres usen Ollama en tu PC, gratis.

1. En tu PC instala un modelo de visión:
   ```
   ollama pull qwen2.5vl:3b
   ```
2. Permite que tu página hable con Ollama. En Windows abre PowerShell y escribe (cambia TU-USUARIO):
   ```
   setx OLLAMA_ORIGINS "https://TU-USUARIO.github.io"
   ```
   Cierra Ollama desde la bandeja del sistema y ábrelo de nuevo.
3. Instala **Tailscale** (gratis) en tu PC y en tu teléfono, con la misma cuenta.
   En la consola de Tailscale activa **MagicDNS** y **HTTPS Certificates** (en DNS).
4. En tu PC, en PowerShell:
   ```
   tailscale serve --bg 11434
   ```
   Te muestra una dirección como `https://tu-pc.tu-red.ts.net`.
5. En la app: **Ajustes → Cerebro en tu PC**, pega esa dirección y toca **Probar conexión**.

El teléfono necesita una dirección **https** para hablar con tu PC; por eso se usa Tailscale y no la IP local.

## Límites a saber

- El modelo del teléfono es más simple que YOLO en tu RTX 5050: se equivoca más con objetos pequeños o lejanos.
- Las distancias son estimaciones con alturas típicas (persona 1.7 m, carro 1.5 m).
- La escucha continua solo funciona bien en Chrome de Android. En iPhone usa el botón **Hablar**.
- La vibración no existe en iPhone; ahí el aviso es el pitido direccional.
- Detecta “persona”, pero no reconoce quién es: el reconocimiento de caras registradas va en tu PC (InsightFace).
