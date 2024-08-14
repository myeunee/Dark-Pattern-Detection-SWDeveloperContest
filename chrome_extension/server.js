const express = require('express');
const cors = require('cors'); 
const fs = require('fs');
const { mongoDB } = require("./config/mongo_db");

const app = express();
const port = 3000;

mongoDB();

app.use(cors());
app.use(express.json({ limit: '50mb' }));

app.post('/dark-pattern/detection', (req, res) => {
    const textData = req.body.textData;
    if (!textData) {
        return res.status(400).json({ error: 'No text data provided' });
    }

    console.log('Received text data:', textData);

    const filePath = 'received_text.json';
    fs.writeFile(filePath, JSON.stringify(textData, null, 2), (err) => {
        if (err) {
            console.error('Error writing file:', err);
            return res.status(500).json({ error: 'Failed to save file' });
        }
        res.json({ message: 'Text received and file saved successfully!' });
    });
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
