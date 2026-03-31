import asyncio
import subprocess
import os
import edge_tts


VOICE = 'en-US-AriaNeural'  # Natural sounding Microsoft voice


async def _synthesize(text: str, mp3_path: str):
    """Async function that calls Edge TTS and saves output as MP3."""
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(mp3_path)


def text_to_voice(text: str, output_path: str) -> str:
    """Convert text to a WhatsApp-compatible OGG voice note.

    Flow: text → Edge TTS → MP3 → ffmpeg → OGG (opus)

    text: the AI's reply text
    output_path: where to save the final .ogg file
    returns: output_path if successful
    """
    mp3_path = output_path.replace('.ogg', '.mp3')

    # Step 1: Generate MP3 using Edge TTS
    asyncio.run(_synthesize(text, mp3_path))

    # Step 2: Convert MP3 to OGG (opus) using ffmpeg
    # WhatsApp requires OGG with opus codec for voice notes
    subprocess.run([
        'ffmpeg', '-y',           # -y = overwrite output if exists
        '-i', mp3_path,           # input MP3
        '-c:a', 'libopus',        # encode with opus codec
        '-b:a', '64k',            # 64kbps bitrate (good quality, small size)
        output_path               # output OGG
    ], check=True, capture_output=True)

    # Clean up the temporary MP3
    os.remove(mp3_path)

    return output_path
