const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const PYTHON_BACKEND = process.env.PYTHON_BACKEND_URL || 'http://localhost:5000';

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        executablePath: process.env.CHROME_PATH || 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
    }
});

client.on('qr', (qr) => {
    console.log('\nScan this QR code with WhatsApp on your phone:\n');
    qrcode.generate(qr, { small: true });
    console.log('\nGo to WhatsApp > Linked Devices > Link a Device\n');
});

client.on('ready', () => {
    console.log('\n[OK] WhatsApp connected! Agent is running.\n');
});

client.on('disconnected', (reason) => {
    console.log(`[WARN] Disconnected (${reason}) — reconnecting...`);
    client.initialize();
});

const ALLOWED_NUMBER = '96176931343@c.us';

client.on('message', async (msg) => {
    if (msg.fromMe) return;
    if (msg.from.endsWith('@g.us')) return;
    if (msg.from !== ALLOWED_NUMBER) return;

    // Handle text messages
    if (msg.type === 'chat') {
        console.log(`[IN]  ${msg.from}: ${msg.body}`);
        try {
            const response = await axios.post(`${PYTHON_BACKEND}/message`, {
                from: msg.from,
                body: msg.body,
                type: 'chat'
            }, { timeout: 30000 });

            await msg.reply(response.data.reply);
            console.log(`[OUT] ${response.data.reply}\n`);

        } catch (error) {
            console.error('[ERR]', error.message);
            await msg.reply("Sorry, I'm having trouble right now. Try again.");
        }
    }

    // Handle voice notes (ptt = push to talk)
    if (msg.type === 'ptt') {
        console.log(`[VOICE IN] from ${msg.from}`);
        try {
            // Download the voice note from WhatsApp
            const media = await msg.downloadMedia();

            // Send audio to Python as base64
            const response = await axios.post(`${PYTHON_BACKEND}/message`, {
                from: msg.from,
                type: 'ptt',
                audio: media.data  // already base64 from whatsapp-web.js
            }, { timeout: 60000 }); // 60s for voice processing

            // Send back as a voice note
            const replyMedia = new MessageMedia(
                'audio/ogg; codecs=opus',
                response.data.audio,
                'reply.ogg'
            );

            await msg.reply(replyMedia, null, { sendAudioAsVoice: true });
            console.log(`[VOICE OUT] Transcription: ${response.data.transcription}\n`);

        } catch (error) {
            console.error('[ERR]', error.message);
            await msg.reply("Sorry, I couldn't process your voice note. Try again.");
        }
    }
});

console.log('Starting WhatsApp client...');
client.initialize();
