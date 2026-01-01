// server.js
import express from "express";
import multer from "multer";
import fetch from "node-fetch"; // or built-in fetch in Node 20+
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

dotenv.config();

const app = express();
const port = 5000;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
});

app.use(express.static(__dirname)); // so logo.png & footer_logo.png are accessible

// For parsing multipart/form-data
const upload = multer();

// Endpoint for generating images
app.post("/api/generate", upload.none(), async (req, res) => {
  try {
    const { prompt, rendering_speed } = req.body;

    if (!prompt) return res.status(400).json({ error: "Prompt is required" });

    // Prepare FormData for Ideogram API
    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("rendering_speed", rendering_speed || "TURBO");

    const response = await fetch("https://api.ideogram.ai/v1/ideogram-v3/generate", {
      method: "POST",
      headers: {
        "Api-Key": process.env.IDEOGRAM_API_KEY,
      },
      body: formData,
    });

    if (!response.ok) {
      const errText = await response.text();
      return res.status(response.status).send(errText);
    }

    const result = await response.json();
    res.json(result);

  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal server error" });
  }
});

app.listen(port, "0.0.0.0", () => {
  console.log(`Server listening at http://0.0.0.0:${port}`);
});