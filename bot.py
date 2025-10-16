import os
import openai
import ffmpeg
import requests
from telegram import Update
from telegram.ext import filters
import nest_asyncio
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
    try:
        print("🎤 Mensaje de voz recibido")

        print("📦 Tipo de mensaje:", update.message)
        print("📦 voice:", update.message.voice)
        print("📦 audio:", update.message.audio)
        print("📦 video_note:", update.message.video_note)
        voice = await update.message.voice.get_file()
        print("📥 Archivo de voz obtenido")

        ogg_path = await voice.download_to_drive()
        print(f"📁 Audio descargado en: {ogg_path}")

        wav_path = "audio.wav"
        convertir_ogg_a_wav(ogg_path, wav_path)
        print("🔊 Audio convertido a WAV")

        texto = transcribe_audio(wav_path)
        print(f"📝 Transcripción: {texto}")

        generar_voz(texto)
        print("🗣️ Voz generada")

        await update.message.reply_audio(audio=open("voz_femenina.mp3", "rb"))
        print("📤 Audio enviado al usuario")

    except Exception as e:
        print(f"❌ Error en handle_voice: {e}")

# 🚀 Inicia el bot en modo webhook
async def main():
    application = Application.builder().token(TOKEN).build()
    voice_filter = filters.VOICE | filters.AUDIO | filters.VIDEO_NOTE
    application.add_handler(MessageHandler(voice_filter, handle_voice))

    url = os.getenv("RENDER_EXTERNAL_URL")
    webhook_url = f"{url}/{TOKEN}"

    await application.bot.set_webhook(webhook_url)
    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=webhook_url
    )

nest_asyncio.apply()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
