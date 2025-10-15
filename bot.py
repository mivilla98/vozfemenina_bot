import os
import openai
import ffmpeg
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

# 🔐 Claves desde entorno
TOKEN = os.getenv("TOKEN")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")

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

# 🚀 Inicia el bot en modo webhook
async def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    url = os.getenv("RENDER_EXTERNAL_URL")
    webhook_url = f"{url}/{TOKEN}"

    await application.bot.set_webhook(webhook_url)
    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
