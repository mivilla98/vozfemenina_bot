from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import whisper, requests, os
from pydub import AudioSegment

TOKEN = "8446586608:AAHqUrq0CzEU_HfvlnlW7WPY8sNLdhHJZao"
ELEVEN_API_KEY = "1a53b0ca08a04fd6af805d759188191e"
VOICE_ID = "f9DFWr0Y8aHd6VNMEdTt"

model = whisper.load_model("base")

def transcribe_audio(file_path):
    result = model.transcribe(file_path, language="es")
    return result["text"]

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

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = await update.message.voice.get_file()
    ogg_path = await voice.download_to_drive()
    wav_path = "audio.wav"
    AudioSegment.from_ogg(ogg_path).export(wav_path, format="wav")

    texto = transcribe_audio(wav_path)
    generar_voz(texto)

    await update.message.reply_audio(audio=open("voz_femenina.mp3", "rb"))

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.run_polling()
