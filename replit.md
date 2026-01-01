# Image Generation App

## Overview
A Node.js/Express application that serves an image generation frontend. Users can enter prompts to generate images using the Ideogram API.

## Project Structure
- `server.mjs` - Express server handling static file serving and API proxy to Ideogram
- `index.html` - Main frontend with prompt input and generation controls
- `logo.png` / `footer_logo.png` - Branding assets

## Tech Stack
- Node.js with Express
- Frontend: Vanilla HTML/CSS/JavaScript
- External API: Ideogram AI for image generation

## Running the App
The server runs on port 5000 and serves the frontend directly.

## Environment Variables
- `IDEOGRAM_API_KEY` - Required for image generation functionality

## Recent Changes
- 2026-01-01: Configured for Replit environment (port 5000, 0.0.0.0 binding)
