import os
import base64
from flask import Flask, request, jsonify
from agent import get_response
from stt import transcribe
from tts import text_to_voice

app = Flask(__name__)

# Folder to temporarily store audio files
AUDIO_DIR = 'audio_tmp'
os.makedirs(AUDIO_DIR, exist_ok=True)


@app.route('/message', methods=['POST'])
def message():
    """
    Handles incoming WhatsApp messages from Node.js.

    For text messages:
    - Gets AI reply as text
    - Returns text reply

    For voice notes (ptt):
    - Receives base64-encoded audio from Node
    - Transcribes with Groq Whisper
    - Gets AI reply
    - Converts reply to OGG voice note
    - Returns base64-encoded OGG + transcription
    """
    data = request.json
    from_number = data.get('from')
    msg_type = data.get('type', 'chat')

    if msg_type == 'ptt':
        # Voice note handling
        audio_b64 = data.get('audio')
        if not audio_b64:
            return jsonify({'error': 'no audio'}), 400

        # Decode and save the incoming OGG
        ogg_in = os.path.join(AUDIO_DIR, f'{from_number}_in.ogg')
        with open(ogg_in, 'wb') as f:
            f.write(base64.b64decode(audio_b64))

        # Transcribe voice → text
        transcribed = transcribe(ogg_in)
        print(f"[VOICE IN] {from_number}: {transcribed}")

        # Get AI reply
        reply_text = get_response(from_number, transcribed)
        print(f"[VOICE OUT] {reply_text}")

        # Convert reply to OGG voice note
        ogg_out = os.path.join(AUDIO_DIR, f'{from_number}_out.ogg')
        text_to_voice(reply_text, ogg_out)

        # Read and encode the output OGG to base64 to send back to Node
        with open(ogg_out, 'rb') as f:
            audio_out_b64 = base64.b64encode(f.read()).decode('utf-8')

        # Cleanup
        os.remove(ogg_in)
        os.remove(ogg_out)

        return jsonify({
            'type': 'voice',
            'audio': audio_out_b64,
            'transcription': transcribed
        })

    else:
        # Text message handling
        body = data.get('body', '')
        print(f"[IN]  {from_number}: {body}")

        reply = get_response(from_number, body)
        print(f"[OUT] {reply}\n")

        return jsonify({'type': 'text', 'reply': reply})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Python backend running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
