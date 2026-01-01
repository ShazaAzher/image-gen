# Image Generation App

A modern web application for generating images using the Ideogram API. Built with Node.js, Express, and vanilla JavaScript.

## Features

- 🎨 Generate images from text prompts using Ideogram AI
- 🚀 Fast image generation with configurable rendering speed
- 💻 Clean, modern user interface
- 🔒 Secure API key management with environment variables

## Prerequisites

- Node.js (v18 or higher recommended)
- npm (comes with Node.js)
- Ideogram API key ([Get one here](https://ideogram.ai/))

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ShazaAzher/claude-streamlit.git
cd claude-streamlit
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the root directory:
```bash
touch .env
```

4. Add your Ideogram API key to the `.env` file:
```
IDEOGRAM_API_KEY=your_api_key_here
PORT=3001
```

## Usage

1. Start the server:
```bash
node server.mjs
```

2. Open your browser and navigate to:
```
http://localhost:3001
```

3. Enter a text prompt describing the image you want to generate
4. Click the "Generate" button
5. The generated image will be displayed (once the API response is processed)

## Project Structure

```
claude-streamlit/
├── server.mjs          # Express server and API endpoints
├── index.html          # Frontend HTML/CSS/JavaScript
├── package.json        # Node.js dependencies
├── requirements.txt    # Python dependencies (not used in this project)
├── logo.png           # Header logo
├── footer_logo.png    # Footer logo
└── .env              # Environment variables (create this file)
```

## API Endpoints

### POST `/api/generate`

Generates an image based on a text prompt.

**Request Body:**
```json
{
  "prompt": "A beautiful sunset over mountains",
  "rendering_speed": "TURBO"
}
```

**Response:**
Returns the Ideogram API response containing the generated image data.

## Technologies Used

- **Node.js** - Runtime environment
- **Express** - Web framework
- **Multer** - Form data parsing
- **node-fetch** - HTTP client for API requests
- **dotenv** - Environment variable management

## Environment Variables

- `IDEOGRAM_API_KEY` - Your Ideogram API key (required)
- `PORT` - Server port (default: 3001)

## License

ISC

## Issues

If you encounter any problems, please open an issue on [GitHub](https://github.com/ShazaAzher/claude-streamlit/issues).
