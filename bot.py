from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import whisper
import ffmpeg
import requests
import os
import openai

# Variables de entorno (puedes usar os.environ o un archivo config.py si lo prefieres)
TOKEN = os.getenv("8446586608:AAHqUrq0CzEU_HfvlnlW7WPY8sNLdhHJZao")
ELEVEN_API_KEY = os.getenv("1a53b0ca08a04fd6af805d759188191e")
VOICE_ID = os.getenv("f9DFWr0Y8aHd6VNMEdTt")

# Cargar modelo Whisper
model = whisper.load_model("tiny")

# Función para convertir OGG a WAV usando ffmpeg-python
def convertir_ogg_a_wav(ogg_path, wav_path):
    ffmpeg.input(ogg_path).output(wav_path).run(overwrite_output=True)

# Función para transcribir audio con Whisper
def transcribe_audio(file_path):
    audio_file = open(file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]


# Función para generar voz femenina con ElevenLabs
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

# Función principal del bot
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = await update.message.voice.get_file()
    ogg_path = await voice.download_to_drive()
    wav_path = "audio.wav"

    convertir_ogg_a_wav(ogg_path, wav_path)
    texto = transcribe_audio(wav_path)
    generar_voz(texto)

    await update.message.reply_audio(audio=open("voz_femenina.mp3", "rb"))

# Inicializar bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.run_polling()
