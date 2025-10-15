import os
import openai
import ffmpeg
import requests
import asyncio
import atexit
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

# 🔐 Claves desde entorno
TOKEN = os.getenv("TOKEN")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")

bot = Bot(token=TOKEN)
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# 🎧 Convierte OGG a WAV
def convertir_ogg_a_wav(ogg_path, wav_path):
    ffmpeg.input(ogg_path).output(wav_path).run(overwrite_output=True)

# 🧠 Transcribe audio con Whisper API
def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]

# 🗣️ Genera voz con ElevenLabs
def generar_voz(texto):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": texto,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, headers=headers, json=data)
    with open("voz_femenina.mp3", "wb") as f:
        f.write(response.content)

# 🤖 Maneja mensajes de voz
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🎤 Mensaje de voz recibido")
    voice = await update.message.voice.get_file()
    ogg_path = await voice.download_to_drive()
    wav_path = "audio.wav"

    convertir_ogg_a_wav(ogg_path, wav_path)
    texto = transcribe_audio(wav_path)
    generar_voz(texto)

    await update.message.reply_audio(audio=open("voz_femenina.mp3", "rb"))

application.add_handler(MessageHandler(filters.VOICE, handle_voice))

# 🌐 Ruta para recibir webhooks
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)

    async def procesar():
        await application.update_queue.put(update)

    asyncio.run(procesar())
    return "OK"

# 🔗 Ruta para activar el webhook
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        return "RENDER_EXTERNAL_URL no está definido", 500

    async def activar():
        await bot.set_webhook(f"{url}/{TOKEN}")

    asyncio.run(activar())
    return f"✅ Webhook configurado en {url}/{TOKEN}"

# 🟢 Ruta de prueba opcional
@app.route("/ping", methods=["GET"])
def ping():
    return "Bot activo y escuchando", 200

# 🧼 Detiene el bot al cerrar
atexit.register(application.stop)

# 🚀 Inicia el bot y el servidor Flask
if __name__ == "__main__":
    application.initialize()
    application.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
