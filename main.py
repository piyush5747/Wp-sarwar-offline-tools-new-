const express = require("express");
const fs = require("fs");
const path = require("path");
const pino = require("pino");
const multer = require("multer");
const {
  default: Gifted_Tech,
  useMultiFileAuthState,
  delay,
  makeCacheableSignalKeyStore,
  Browsers,
} = require("maher-zubair-baileys");

const app = express();
const PORT = 5000;

// Create necessary directories
if (!fs.existsSync("uploads")) {
  fs.mkdirSync("uploads");
}
if (!fs.existsSync("sessions")) {
  fs.mkdirSync("sessions");
}

const upload = multer({ dest: "uploads/" });

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static("public"));

// Store active clients
const activeClients = new Map();

// Improved UI HTML
const htmlTemplate = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WhatsApp Multi-User Sender</title>
  <style>
    :root {
      --primary: #25D366;
      --secondary: #128C7E;
      --accent: #34B7F1;
      --light: #DCF8C6;
      --dark: #075E54;
      --text: #333;
      --bg: #f0f2f5;
    }
    
    * {
      box-sizing: border-box;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    body {
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 20px;
      line-height: 1.6;
    }
    
    .container {
      max-width: 1000px;
      margin: 0 auto;
      padding: 20px;
    }
    
    header {
      text-align: center;
      margin-bottom: 30px;
    }
    
    h1, h2, h3 {
      color: var(--dark);
    }
    
    .logo {
      font-size: 2.5rem;
      color: var(--primary);
      margin-bottom: 10px;
    }
    
    .panel {
      background: white;
      border-radius: 10px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      padding: 25px;
      margin-bottom: 30px;
    }
    
    .form-group {
      margin-bottom: 20px;
    }
    
    label {
      display: block;
      margin-bottom: 8px;
      font-weight: 600;
      color: var(--dark);
    }
    
    input, select, button, textarea {
      width: 100%;
      padding: 12px 15px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 16px;
      transition: all 0.3s;
    }
    
    input:focus, select:focus, textarea:focus {
      border-color: var(--primary);
      outline: none;
      box-shadow: 0 0 0 3px rgba(37, 211, 102, 0.2);
    }
    
    button {
      background: var(--primary);
      color: white;
      border: none;
      font-weight: 600;
      cursor: pointer;
      margin-top: 10px;
    }
    
    button:hover {
      background: var(--secondary);
    }
    
    .result-box {
      padding: 15px;
      background: var(--light);
      border-radius: 6px;
      margin-top: 20px;
      word-break: break-all;
    }
    
    .session-list {
      margin-top: 30px;
    }
    
    .session-item {
      padding: 15px;
      background: white;
      border-radius: 6px;
      margin-bottom: 10px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.05);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .session-id {
      font-weight: bold;
      color: var(--secondary);
    }
    
    .session-number {
      color: var(--dark);
    }
    
    .status-connected {
      color: var(--primary);
      font-weight: bold;
    }
    
    .status-disconnected {
      color: #ff6b6b;
    }
    
    .action-btn {
      padding: 8px 15px;
      font-size: 14px;
      width: auto;
    }
    
    .btn-disconnect {
      background: #ff6b6b;
    }
    
    .btn-disconnect:hover {
      background: #ff5252;
    }
    
    .file-input-label {
      display: block;
      padding: 12px 15px;
      background: #f8f9fa;
      border: 1px dashed #ddd;
      border-radius: 6px;
      text-align: center;
      cursor: pointer;
      margin-bottom: 10px;
    }
    
    .file-input-label:hover {
      background: #e9ecef;
    }
    
    .hidden {
      display: none;
    }
    
    .tab-container {
      margin-bottom: 20px;
    }
    
    .tab-buttons {
      display: flex;
      border-bottom: 1px solid #ddd;
    }
    
    .tab-button {
      padding: 10px 20px;
      background: none;
      border: none;
      border-bottom: 3px solid transparent;
      cursor: pointer;
      font-weight: 600;
      color: var(--text);
      width: auto;
    }
    
    .tab-button.active {
      border-bottom-color: var(--primary);
      color: var(--primary);
    }
    
    .tab-content {
      display: none;
      padding: 20px 0;
    }
    
    .tab-content.active {
      display: block;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo"> PIYUSH <3🎨WhatsApp Multi-Sender</div>
      <p>Send messages to multiple recipients with delay between messages</p>
    </header>
    
    <div class="tab-container">
      <div class="tab-buttons">
        <button class="tab-button active" data-tab="connect">Connect WhatsApp</button>
        <button class="tab-button" data-tab="send">Send Messages</button>
        <button class="tab-button" data-tab="sessions">Active Sessions</button>
      </div>
      
      <div id="connect-tab" class="tab-content active">
        <div class="panel">
          <h2>Generate Pairing Code</h2>
          <form id="pairing-form" action="/code" method="GET">
            <div class="form-group">
              <label for="number">WhatsApp Number (with country code)</label>
              <input type="text" id="number" name="number" placeholder="e.g. 919876543210" required>
            </div>
            <button type="submit">Generate Pairing Code</button>
          </form>
          
          <div id="pairing-result" class="result-box hidden"></div>
        </div>
      </div>
      
      <div id="send-tab" class="tab-content">
        <div class="panel">
          <h2>Send Messages</h2>
          <form id="message-form" action="/send-message" method="POST" enctype="multipart/form-data">
            <div class="form-group">
              <label for="sessionId">Your Session ID</label>
              <input type="text" id="sessionId" name="sessionId" placeholder="Enter your session ID" required>
            </div>
            
            <div class="form-group">
              <label for="targetType">Target Type</label>
              <select id="targetType" name="targetType" required>
                <option value="">-- Select Target Type --</option>
                <option value="number">Target Number</option>
                <option value="group">Group UID</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="target">Target Number / Group UID</label>
              <input type="text" id="target" name="target" placeholder="Enter Target Number / Group UID" required>
            </div>
            
            <div class="form-group">
              <label for="messageFile">Message File (TXT)</label>
              <label for="messageFile" class="file-input-label">
                Choose File (TXT format with one message per line)
              </label>
              <input type="file" id="messageFile" name="messageFile" accept=".txt" required style="display: none;">
            </div>
            
            <div class="form-group">
              <label for="delaySec">Delay Between Messages (seconds)</label>
              <input type="number" id="delaySec" name="delaySec" min="1" value="5" required>
            </div>
            
            <button type="submit">Start Sending Messages</button>
          </form>
          
          <div id="message-result" class="result-box hidden"></div>
        </div>
      </div>
      
      <div id="sessions-tab" class="tab-content">
        <div class="panel">
          <h2>Active Sessions</h2>
          <div class="session-list" id="session-list">
            <!-- Sessions will be listed here -->
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    // Tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
      button.addEventListener('click', () => {
        // Remove active class from all buttons and tabs
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
        
        // Add active class to clicked button and corresponding tab
        button.classList.add('active');
        const tabId = button.getAttribute('data-tab') + '-tab';
        document.getElementById(tabId).classList.add('active');
      });
    });
    
    // Handle pairing form submission
    document.getElementById('pairing-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const form = e.target;
      const resultDiv = document.getElementById('pairing-result');
      
      try {
        const response = await fetch(form.action + '?' + new URLSearchParams(new FormData(form)));
        const data = await response.text();
        
        resultDiv.innerHTML = data;
        resultDiv.classList.remove('hidden');
        
        // Extract session ID from the response if available
        const sessionMatch = data.match(/Session ID: (\w+)/);
        if (sessionMatch) {
          document.getElementById('sessionId').value = sessionMatch[1];
          // Switch to send tab
          document.querySelector('[data-tab="send"]').click();
        }
      } catch (error) {
        resultDiv.innerHTML = '<h3>Error: ' + error.message + '</h3>';
        resultDiv.classList.remove('hidden');
      }
    });
    
    // Handle message form submission
    document.getElementById('message-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const form = e.target;
      const resultDiv = document.getElementById('message-result');
      const formData = new FormData(form);
      
      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: formData
        });
        
        const data = await response.text();
        resultDiv.innerHTML = data;
        resultDiv.classList.remove('hidden');
      } catch (error) {
        resultDiv.innerHTML = '<h3>Error: ' + error.message + '</h3>';
        resultDiv.classList.remove('hidden');
      }
    });
    
    // Function to load active sessions
    async function loadSessions() {
      try {
        const response = await fetch('/active-sessions');
        const sessions = await response.json();
        
        const sessionList = document.getElementById('session-list');
        sessionList.innerHTML = '';
        
        if (sessions.length === 0) {
          sessionList.innerHTML = '<p>No active sessions found</p>';
          return;
        }
        
        sessions.forEach(session => {
          const sessionItem = document.createElement('div');
          sessionItem.className = 'session-item';
          sessionItem.innerHTML = \`
            <div>
              <span class="session-id">\${session.sessionId}</span>
              <span class="session-number">(\${session.number})</span>
              <span class="\${session.connected ? 'status-connected' : 'status-disconnected'}">
                \${session.connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <button class="action-btn btn-disconnect" data-session="\${session.sessionId}">Disconnect</button>
          \`;
          sessionList.appendChild(sessionItem);
        });
        
        // Add event listeners to disconnect buttons
        document.querySelectorAll('.btn-disconnect').forEach(btn => {
          btn.addEventListener('click', async () => {
            const sessionId = btn.getAttribute('data-session');
            try {
              const response = await fetch('/disconnect?sessionId=' + sessionId);
              const result = await response.text();
              alert(result);
              loadSessions();
            } catch (error) {
              alert('Error disconnecting session: ' + error.message);
            }
          });
        });
      } catch (error) {
        console.error('Error loading sessions:', error);
      }
    }
    
    // Load sessions when sessions tab is clicked
    document.querySelector('[data-tab="sessions"]').addEventListener('click', loadSessions);
  </script>
</body>
</html>
`;

app.get("/", (req, res) => {
  res.send(htmlTemplate);
});

// Generate pairing code and create session
app.get("/code", async (req, res) => {
  const number = req.query.number.replace(/[^0-9]/g, "");
  const sessionId = generateSessionId();
  const sessionPath = path.join("sessions", sessionId);

  if (!fs.existsSync(sessionPath)) {
    fs.mkdirSync(sessionPath, { recursive: true });
  }

  try {
    const { state, saveCreds } = await useMultiFileAuthState(sessionPath);
    
    const waClient = Gifted_Tech({
      auth: {
        creds: state.creds,
        keys: makeCacheableSignalKeyStore(state.keys, pino({ level: "fatal" }).child({ level: "fatal" })),
      },
      printQRInTerminal: false,
      logger: pino({ level: "fatal" }).child({ level: "fatal" }),
      browser: Browsers.macOS("Desktop"),
    });

    if (!waClient.authState.creds.registered) {
      await delay(1500);
      const code = await waClient.requestPairingCode(number);
      
      // Store the client in the activeClients map
      activeClients.set(sessionId, {
        client: waClient,
        number: number,
        connected: true
      });

      // Handle connection updates
      waClient.ev.on("creds.update", saveCreds);
      waClient.ev.on("connection.update", async (update) => {
        const { connection, lastDisconnect } = update;
        
        if (connection === "open") {
          console.log(`WhatsApp connected for session ${sessionId}`);
          activeClients.set(sessionId, {
            ...activeClients.get(sessionId),
            connected: true
          });
        } else if (connection === "close") {
          console.log(`WhatsApp disconnected for session ${sessionId}`);
          activeClients.set(sessionId, {
            ...activeClients.get(sessionId),
            connected: false
          });
          
          // Attempt to reconnect if not logged out
          if (lastDisconnect?.error?.output?.statusCode !== 401) {
            await delay(10000);
            waClient.connect();
          }
        }
      });

      res.send(`
        <h3>Pairing Code: ${code}</h3>
        <h3>Session ID: ${sessionId}</h3>
        <p>Save this Session ID to use for sending messages</p>
        <p><a href="/" onclick="document.querySelector('[data-tab=\\'send\\']').click(); return false;">Go to Send Messages</a></p>
      `);
    } else {
      // If already registered, just store the client
      activeClients.set(sessionId, {
        client: waClient,
        number: number,
        connected: true
      });
      
      res.send(`
        <h3>Already registered with this number</h3>
        <h3>Session ID: ${sessionId}</h3>
        <p>Save this Session ID to use for sending messages</p>
        <p><a href="/" onclick="document.querySelector('[data-tab=\\'send\\']').click(); return false;">Go to Send Messages</a></p>
      `);
    }
  } catch (err) {
    console.error("Error in pairing:", err);
    res.send(`
      <h3 style="color: red;">Error: ${err.message || "Failed to generate pairing code"}</h3>
      <p><a href="/">Try Again</a></p>
    `);
  }
});

// Send messages endpoint
app.post("/send-message", upload.single("messageFile"), async (req, res) => {
  const { sessionId, target, targetType, delaySec } = req.body;
  const filePath = req.file?.path;

  if (!sessionId || !target || !filePath || !delaySec || !targetType) {
    return res.send(`
      <h3 style="color: red;">Error: Missing required fields</h3>
      <p><a href="/">Go Back</a></p>
    `);
  }

  // Check if session exists
  if (!activeClients.has(sessionId)) {
    return res.send(`
      <h3 style="color: red;">Error: Invalid Session ID or session not active</h3>
      <p><a href="/" onclick="document.querySelector('[data-tab=\\'connect\\']').click(); return false;">Generate New Session</a></p>
    `);
  }

  const { client, connected } = activeClients.get(sessionId);
  
  if (!connected) {
    return res.send(`
      <h3 style="color: red;">Error: WhatsApp is not connected for this session</h3>
      <p>Try reconnecting or create a new session</p>
      <p><a href="/" onclick="document.querySelector('[data-tab=\\'connect\\']').click(); return false;">Generate New Session</a></p>
    `);
  }

  try {
    const messages = fs.readFileSync(filePath, "utf-8")
      .split("\n")
      .filter(msg => msg.trim() !== "");
    
    const recipient = targetType === "group" 
      ? target + "@g.us" 
      : target + "@s.whatsapp.net";

    // Start sending messages in a loop (non-blocking)
    sendMessagesLoop(client, recipient, messages, delaySec * 1000)
      .catch(err => console.error("Error in message loop:", err));

    res.send(`
      <h3 style="color: green;">Message sending started successfully!</h3>
      <p>Messages will be sent in a loop with ${delaySec} seconds delay between each message.</p>
      <p>Total messages loaded: ${messages.length}</p>
      <p><a href="/" onclick="document.querySelector('[data-tab=\\'sessions\\']').click(); return false;">View Active Sessions</a></p>
    `);
  } catch (error) {
    console.error("Error sending messages:", error);
    res.send(`
      <h3 style="color: red;">Error: ${error.message || "Failed to send messages"}</h3>
      <p><a href="/">Go Back</a></p>
    `);
  }
});

// Get active sessions
app.get("/active-sessions", (req, res) => {
  const sessions = Array.from(activeClients.entries()).map(([sessionId, data]) => ({
    sessionId,
    number: data.number,
    connected: data.connected
  }));
  res.json(sessions);
});

// Disconnect session
app.get("/disconnect", (req, res) => {
  const { sessionId } = req.query;
  
  if (!sessionId || !activeClients.has(sessionId)) {
    return res.send("Invalid session ID");
  }

  try {
    const { client } = activeClients.get(sessionId);
    client.end();
    activeClients.delete(sessionId);
    
    // Optionally: Delete session folder
    // fs.rmdirSync(path.join("sessions", sessionId), { recursive: true });
    
    res.send(`Session ${sessionId} disconnected successfully`);
  } catch (err) {
    res.send(`Error disconnecting session: ${err.message}`);
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

// Helper function to generate random session ID
function generateSessionId() {
  return Math.random().toString(36).substring(2, 15) + 
         Math.random().toString(36).substring(2, 15);
}

// Function to send messages in a loop
async function sendMessagesLoop(client, recipient, messages, delayMs) {
  let index = 0;
  
  while (true) {
    const msg = messages[index];
    try {
      await client.sendMessage(recipient, { text: msg });
      console.log(`Sent: ${msg} to ${recipient}`);
    } catch (err) {
      console.error(`Failed to send message: ${err.message}`);
      // Wait longer if there's an error
      await delay(delayMs * 2);
      continue;
    }
    
    index = (index + 1) % messages.length;
    await delay(delayMs);
  }
}