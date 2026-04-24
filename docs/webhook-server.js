const http = require('http');
const { execSync } = require('child_process');
const { URL } = require('url');

// Configuration
const PORT = 3001;
const TELEGRAM_CHAT_ID = '8231412720';
const BOT_TOKEN = '8389460997:AAHFzJ4Yf3y4brxFMViuo8rrWDguw7ndsEA';

// Store latest response
let latestResponse = { text: '', timestamp: 0 };

// Simple HTTP server
const server = http.createServer(async (req, res) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  const url = new URL(req.url, `http://localhost:${PORT}`);
  
  // Health check
  if (url.pathname === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', webhook: 'active' }));
    return;
  }
  
  // Telegram Webhook - receives messages from Telegram
  if (url.pathname === '/webhook' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', async () => {
      try {
        const update = JSON.parse(body);
        
        // Only process messages from our chat
        if (update.message && update.message.chat.id.toString() === TELEGRAM_CHAT_ID) {
          const text = update.message.text;
          console.log('Received from Telegram:', text);
          
          // Don't respond to commands here - let me respond via the voice chat
          // Just acknowledge
          console.log('Message received - user should use voice chat to get response');
        }
        
        res.writeHead(200);
        res.end('OK');
      } catch (e) {
        console.error('Webhook error:', e);
        res.writeHead(500);
        res.end('Error');
      }
    });
    return;
  }
  
  // Chat endpoint - send message and get AI response
  if (url.pathname === '/chat' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', async () => {
      try {
        const { message } = JSON.parse(body);
        console.log('User said:', message);
        
        // Send message to me on Telegram
        const encodedMessage = encodeURIComponent(`🎤 VOICE CHAT:\n\n"${message}"\n\n💬 Reply to this message so I can respond!`);
        execSync(`curl -s "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage?chat_id=${TELEGRAM_CHAT_ID}&text=${encodedMessage}&parse_mode=HTML"`, { stdio: 'pipe' });
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          status: 'sent',
          message: 'Message sent! Reply on Telegram, then say "read" to hear my response.'
        }));
      } catch (e) {
        console.error('Error:', e);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }
  
  // Poll for AI response
  if (url.pathname === '/poll' && req.method === 'GET') {
    const lastUpdate = parseInt(url.searchParams.get('last')) || 0;
    
    // Check for new responses - user needs to reply on Telegram
    // For now, we'll use a simpler approach
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      response: latestResponse.text,
      timestamp: latestResponse.timestamp
    }));
    return;
  }
  
  // Manual send response endpoint - I can call this to send response
  if (url.pathname === '/respond' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const { text } = JSON.parse(body);
        latestResponse = { text, timestamp: Date.now() };
        
        // Send to Telegram
        const encoded = encodeURIComponent(`🔊 VOICE RESPONSE:\n\n${text}`);
        execSync(`curl -s "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage?chat_id=${TELEGRAM_CHAT_ID}&text=${encoded}&parse_mode=HTML"`, { stdio: 'pipe' });
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'sent' }));
      } catch (e) {
        res.writeHead(500);
        res.end('Error');
      }
    });
    return;
  }
  
  res.writeHead(404);
  res.end('Not found');
});

server.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════════╗
║        Voice Chat Webhook Server with Telegram!            ║
╠═══════════════════════════════════════════════════════════════╣
║  Server: http://localhost:${PORT}                              ║
║  Webhook: https://329a-103-21-15-114.ngrok-free.app/webhook ║
║  Telegram: Connected                                          ║
╚═══════════════════════════════════════════════════════════════╝

🎤 READY! Open voice-chat-connected.html to start!
  `);
});

process.on('SIGINT', () => {
  console.log('\nShutting down...');
  server.close();
  process.exit();
});
