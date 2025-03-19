const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const express = require('express');
const multer = require('multer');
const WebSocket = require('ws');

const app = express();
const port = 3000;
const upload = multer({ dest: 'uploads/' });

const wss = new WebSocket.Server({ noServer: true });

app.use(express.static('uploads/public'));

wss.on('connection', (ws) => {
  console.log('WebSocket connection established');
  ws.on('message', (message) => {
    console.log(`Received message: ${message}`);
  });
});

// Handle WebSocket upgrade
const server = app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});

server.on('upgrade', (request, socket, head) => {
  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit('connection', ws, request);
  });
});

// Route for uploading PDF files
app.post('/upload', upload.single('pdf'), (req, res) => {
  const pdfPath = path.join(__dirname, 'uploads', req.file.filename);
  const outputDir = path.join(__dirname, 'ppt_jsons');

  // Log the start time for the entire process
  const startTime = Date.now();

  // Log the file path for debugging
  console.log(`Uploaded file path: ${pdfPath}`);

  // Spawn a child process to handle the PDF processing
  const process = spawn('python3', [path.join(__dirname, '..',  'ppt.py'), pdfPath]);

  process.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
    // Send real-time updates to the client
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(data.toString());
      }
    });
  });

  process.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
    // Send error updates to the client
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(`Error: ${data.toString()}`);
      }
    });
  });

  process.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
    if (code === 0) {
      // Log the end time for the entire process
      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000; // duration in seconds

      // Read the generated presentation links
      fs.readFile(path.join(outputDir, 'presentation_links.json'), 'utf8', (err, data) => {
        if (err) {
          res.status(500).send('Error reading presentation links.');
        } else {
          res.send(`Processing complete. Here are your presentation links:<br>${data.replace(/\n/g, '<br>')}<br>Total time: ${duration} seconds`);
        }
      });
    } else {
      res.status(500).send('Error processing the PDF.');
    }
  });
});