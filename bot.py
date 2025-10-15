import os
import openai
import ffmpeg
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, filters, ContextTypes

# 🔐 Claves desde entorno
TOKEN = os.getenv("TOKEN")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=4, use_context=True)

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
    voice = await update.message.voice.get_file()
    ogg_path = await voice.download_to_drive()
    wav_path = "audio.wav"

    convertir_ogg_a_wav(ogg_path, wav_path)
    texto = transcribe_audio(wav_path)
    generar_voz(texto)

    await update.message.reply_audio(audio=open("voz_femenina.mp3", "rb"))

dispatcher.add_handler(MessageHandler(filters.VOICE, handle_voice))

# 🌐 Ruta para recibir webhooks
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

# 🚀 Establece el webhook al iniciar
@app.before_first_request
def set_webhook():
    url = os.getenv("RENDER_EXTERNAL_URL")  # Render la define automáticamente
    bot.set_webhook(f"{url}/{TOKEN}")

# 🟢 Ejecuta el servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
