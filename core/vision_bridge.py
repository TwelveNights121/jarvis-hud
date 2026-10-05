"""
Puente de ejemplo entre JARVIS Vision (teléfono / lentes) y el núcleo de JARVIS en tu PC.

Qué hace:
  - Abre un servidor WebSocket local (puerto 8765).
  - Recibe los eventos de JARVIS Vision: online, detections, alert, command, event_saved, scene.
  - Guarda las alertas y eventos en un registro (vision_log.jsonl).
  - Cuando llega una orden libre ("command" que JARVIS Vision no supo resolver),
    se la pasa a Ollama y devuelve la respuesta para que el teléfono la diga en voz alta.

Uso:
  pip install websockets requests
  python vision_bridge.py
  tailscale serve --bg --https=8443 http://localhost:8765
En JARVIS Vision → Ajustes → JARVIS Core:  wss://tu-pc.tu-red.ts.net:8443
"""
import asyncio
import json
import time

import requests
import websockets

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:7b"
LOG_FILE = "vision_log.jsonl"

SYSTEM_PROMPT = (
    "Eres JARVIS. Respondes en español, tratas al usuario de 'señor' y vas directo a lo útil en máximo "
    "3 frases. Recibes lo que detecta la cámara de sus lentes. A las personas solo las llamas 'persona'. "
    "Si algo que pide podría violar derechos de otras personas o la ley, no lo haces: propones la "
    "alternativa permitida más cercana que logre su objetivo."
)

last_scene = []


def log_event(msg: dict) -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")


def ask_ollama(question: str) -> str:
    scene = ", ".join(f"{o['etiqueta']} ({o['lado']})" for o in last_scene) or "nada relevante"
    body = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Ahora la cámara ve: {scene}.\nPregunta: {question}"},
        ],
    }
    try:
        r = requests.post(OLLAMA_URL, json=body, timeout=60)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
    except Exception as e:  # noqa: BLE001
        return f"No pude consultar el cerebro local: {e}"


async def handler(ws):
    global last_scene
    print("JARVIS Vision conectado")
    async for raw in ws:
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            continue
        kind, data = msg.get("type"), msg.get("data") or {}

        if kind == "detections":
            last_scene = data.get("objetos", [])
        elif kind in ("alert", "event_saved", "online", "hello"):
            log_event(msg)
            print(time.strftime("%H:%M:%S"), kind, data)
        elif kind == "command":
            log_event(msg)
            text = data.get("texto", "")
            # Las órdenes conocidas ya las resuelve el teléfono; aquí respondemos las preguntas libres.
            if text and not any(k in text.lower() for k in ("que ves", "qué ves", "briefing", "guarda", "hora", "silencio")):
                answer = await asyncio.to_thread(ask_ollama, text)
                await ws.send(json.dumps({"type": "say", "text": answer}, ensure_ascii=False))


async def main():
    async with websockets.serve(handler, "localhost", 8765, max_size=2**20):
        print("Puente de JARVIS Vision escuchando en ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
