import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))


def transcribe(audio_path: str) -> str:
    """Send an audio file to Groq Whisper and get back the transcribed text.

    audio_path: path to the .ogg file downloaded from WhatsApp
    returns: transcribed text string
    """
    with open(audio_path, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(
            model='whisper-large-v3',
            file=audio_file,
            response_format='text'
        )
    return transcription
