const venom = require('venom-bot');
const express = require('express');
const bodyParser = require('body-parser');

let venomClient = null;

venom
  .create({ session: 'session-name', headless: 'new' })
  .then((client) => {
    venomClient = client;
    startExpressServer();
  });

function startExpressServer() {
  const app = express();
  app.use(bodyParser.json());

  // Endpoint untuk menerima pesan dari Flask
  app.post('/send-message', (req, res) => {
    const { message } = req.body;
    if (!message) {
      return res.status(400).send('Message is required');
    }

    // Kirim ke nomor target (ubah sesuai kebutuhan)
    venomClient.sendText('6281217870716@c.us', message)
      .then(() => res.send('Pesan terkirim'))
      .catch(err => res.status(500).send(err));
  });

  app.listen(3000, () => console.log('📡 Server bot listening on port 3000'));
}
