# AI Girlfriend Chat - React Frontend

A modern React frontend for the Energy-Aware AI Girlfriend Conversation System.

## Features

- 🎨 **Modern UI**: Beautiful, responsive design with smooth animations
- 💬 **Real-time Chat**: Instant messaging with the AI girlfriend
- 📊 **Energy Monitoring**: Visual energy indicators and status
- 📈 **Session Metrics**: Detailed conversation analytics
- 🎯 **Session Management**: Start, stop, and monitor conversations
- 📱 **Mobile Responsive**: Works on all device sizes

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Python backend running on port 5000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. The app will open at `http://localhost:3000`

### Building for Production

```bash
npm run build
```

## API Endpoints

The frontend communicates with the Flask backend via these endpoints:

- `POST /api/start` - Start a new conversation
- `POST /api/send` - Send a message
- `POST /api/stop` - Stop the conversation
- `GET /api/metrics` - Get session metrics
- `GET /api/health` - Health check

## Components

- **App.tsx** - Main application component
- **ChatMessage.tsx** - Individual chat message display
- **ChatInput.tsx** - Message input with send functionality
- **EnergyIndicator.tsx** - Energy status visualization
- **SessionControls.tsx** - Session management controls
- **MetricsModal.tsx** - Detailed metrics display

## Styling

The app uses CSS modules with a modern design featuring:
- Gradient backgrounds
- Glassmorphism effects
- Smooth animations
- Responsive grid layouts
- Custom scrollbars

## Development

### Available Scripts

- `npm start` - Start development server
- `npm test` - Run tests
- `npm run build` - Build for production
- `npm run eject` - Eject from Create React App

### Project Structure

```
src/
├── components/          # React components
├── services/           # API service layer
├── types.ts           # TypeScript type definitions
├── App.tsx            # Main app component
├── App.css            # Main styles
└── index.tsx          # App entry point
```