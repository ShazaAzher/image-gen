// server.mjs
import express from "express";
import multer from "multer";
import fetch from "node-fetch";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
import session from "express-session";

dotenv.config();

const app = express();
const port = 5000;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(__dirname));
app.use(express.static(path.join(process.cwd(), "public")));
app.use(session({
  secret: process.env.SESSION_SECRET || "default_secret",
  resave: false,
  saveUninitialized: true,
  cookie: { secure: false } // Set to true if using https
}));

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
});

// For parsing multipart/form-data
const upload = multer();

// Endpoint for history
app.get("/api/history", (req, res) => {
  if (!req.session.messages) {
    req.session.messages = [];
  }
  res.json(req.session.messages);
});

// Endpoint for generating images
app.post("/api/generate", upload.none(), async (req, res) => {
  try {
    const { prompt } = req.body;

    if (!prompt) return res.status(400).json({ error: "Prompt is required" });

    if (!req.session.messages) {
      req.session.messages = [];
    }

    // Find the last assistant message with an image
    const lastAssistantMsg = [...req.session.messages].reverse().find(m => m.role === "assistant" && m.images && m.images.length > 0);
    const lastImageUrl = lastAssistantMsg ? lastAssistantMsg.images[0].url : null;

    // Add user message to history
    req.session.messages.push({ role: "user", content: prompt });

    // Prepare FormData for Ideogram API as per docs
    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("rendering_speed", "TURBO");
    
    // If there's a previous image, use it as a style reference to maintain consistency
    if (lastImageUrl) {
      try {
        const imageRes = await fetch(lastImageUrl);
        const imageBlob = await imageRes.blob();
        formData.append("style_reference_images", imageBlob, "reference.png");
        formData.append("style_reference_image_fidelity", "50"); 
      } catch (e) {
        console.error("Failed to attach reference image:", e);
      }
    }

    const response = await fetch("https://api.ideogram.ai/v1/ideogram-v3/generate", {
      method: "POST",
      headers: {
        "Api-Key": process.env.IDEOGRAM_API_KEY,
      },
      body: formData,
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error("Ideogram API Error:", errText);
      return res.status(response.status).send(errText);
    }

    const result = await response.json();
    
    // Add assistant response to history
    const assistantMsg = { 
      role: "assistant", 
      content: "Here is your generated image.",
      images: result.data // Assuming result.data contains the image objects
    };
    req.session.messages.push(assistantMsg);

    res.json({ message: assistantMsg, history: req.session.messages });

  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal server error" });
  }
});

app.listen(port, "0.0.0.0", () => {
  console.log(`Server listening at http://0.0.0.0:${port}`);
});