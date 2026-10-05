# JARVIS Vision

**v0.1.0 · prototipo** · El módulo de visión del sistema JARVIS.

Convierte la cámara de un teléfono (y en el futuro, la de los lentes JARVIS) en un HUD en vivo: detecta lo que tienes enfrente, te avisa si algo se acerca y le pasa todo al núcleo de JARVIS. El video se analiza dentro del teléfono y no sale de ahí.

## Qué hace la v0.1.0

| Función | Cómo |
|---|---|
| Detección en vivo | COCO-SSD (TensorFlow.js) en el teléfono: personas, vehículos, animales y ~80 objetos |
| Seguimiento | Cada objeto tiene un id estable y se sabe si se acerca |
| Distancia aproximada | Altura típica de cada clase + campo de visión de la cámara |
| Alertas direccionales | Voz + pitido del lado del peligro (audífonos) + vibración en Android |
| Comandos de voz | “qué ves”, “briefing”, “guarda eso”, “silencio”, “hora” |
| Briefing | Hora, batería, clima real (Open-Meteo) y escena |
| Caja negra | Bucle de ~30 s con HUD, caras pixeladas y sello SHA-256 |
| Privacidad | Las personas solo se marcan como “no registrada” |
| Modo compatible | Si la GPU del teléfono falla, cambia sola a CPU |
| Integración | Eventos para JARVIS Core por WebSocket, `postMessage` o `window.JarvisVision` |

**Límites conocidos:** el modelo del teléfono tarda en reaccionar (sobre todo en modo compatible), las distancias son estimaciones y no reconoce quién es cada persona.

## Usarlo

Abre la página publicada en Safari (iPhone) o Chrome (Android), toca **Iniciar JARVIS** y acepta cámara y movimiento. Para tenerlo como app: Compartir → **Agregar a inicio**.

Probarlo en la Mac: arrastra `index.html` a Chrome.

## Integración con JARVIS Core

Todos los mensajes tienen la misma forma:

```json
{ "source": "jarvis-vision", "version": "0.1.0", "type": "alert", "ts": 1791230000000, "data": { } }
```

**Lo que envía JARVIS Vision**

| type | Cuándo | data |
|---|---|---|
| `online` | Al iniciar | `camara`, `resolucion`, `motor` |
| `hello` | Al conectarse al Core | `capacidades` |
| `detections` | 2 veces por segundo | `fps`, `objetos[]` |
| `alert` | Algo se acerca, vehículo muy cerca u objeto cortante | `texto`, `urgente`, `clase`, `etiqueta`, `pan` (-1 izq · +1 der), `distancia_m` |
| `command` | El usuario dio una orden de voz | `texto` |
| `event_saved` | Se selló un evento de la caja negra | `id`, `foto_sha256`, `con_video` |
| `scene` | Respuesta a `get_scene` | `objetos[]`, `resumen` |

Cada objeto: `{ id, clase, etiqueta, tipo, confianza, distancia_m, lado, caja:[x,y,w,h] }` (caja normalizada de 0 a 1).

**Lo que acepta JARVIS Vision**

| type | Efecto |
|---|---|
| `{ "type": "say", "text": "…" }` | Lo dice en voz alta y lo muestra |
| `{ "type": "command", "text": "qué ves" }` | Ejecuta una orden como si se hubiera dicho |
| `{ "type": "alert", "text": "…" }` | Muestra una alerta con pitido |
| `{ "type": "get_scene" }` | Responde con un mensaje `scene` |

**Tres formas de conectarse**

1. **WebSocket** (recomendado): Ajustes → JARVIS Core → `wss://…`. Ejemplo listo en [`core/vision_bridge.py`](core/vision_bridge.py), que registra eventos y responde preguntas con Ollama.
2. **iframe**: si otra página de JARVIS lo incrusta, recibe los eventos por `postMessage`, y le puede enviar mensajes con `target: "jarvis-vision"`.
3. **En la misma página**: `JarvisVision.on('alert', m => …)`, `JarvisVision.say('…')`, `JarvisVision.scene()`.

Desde una página `https` solo se puede conectar a `wss://`. Con Tailscale: `tailscale serve --bg --https=8443 http://localhost:8765`.

## Hoja de ruta

- **v0.2** · Conexión estable con JARVIS Core y Ollama · reconocimiento de caras registradas con permiso (en el PC).
- **v0.3** · Memoria episódica (dónde viste tus cosas) · lectura y traducción de letreros.
- **v1.0** · Cámara de los lentes (XIAO ESP32-S3) en vez del teléfono · YOLO en la RTX 5050.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | Toda la app |
| `manifest.json`, `icon.svg` | Para instalarla como app |
| `core/vision_bridge.py` | Puente de ejemplo con el núcleo de JARVIS en tu PC |
