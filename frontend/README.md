# Quiz App

A React-based quiz application with dynamic question handling and real-time feedback.

## Setup

```bash
npm install
```

## Run

```bash
npm start
```

## Features

- Interactive quiz interface
- Dynamic question rendering
- Score tracking
- Responsive design with Tailwind CSS
- Particle background animation
- Three main interactive pages:
  - Login page with user authentication
  - Quiz interface with timed questions
  - Leaderboard with player rankings

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Login.js        # User authentication component
│   │   ├── Quiz.js         # Main quiz interface
│   │   ├── Leaderboard.js  # Leaderboard display
│   │   ├── UserInputTest.js # User input testing component
│   │   └── ParticlesBackground.js    # Background animation component
│   ├── styles/
│   │   └── index.css       # Global styles and Tailwind imports
│   ├── App.js
│   └── index.js
├── public/
│   ├── index.html
│   └── manifest.json
└── tailwind.config.js
```

## Technologies

- React.js
- Tailwind CSS
- Node.js
- tsParticles for background animation

## Development

The app runs on `http://localhost:3000` in development mode with hot-reload enabled.

### Particle Background Setup

The particle background is implemented using tsParticles. To configure:

1. Ensure tsParticles is installed:
```bash
npm install tsparticles react-tsparticles
```

2. Import and use the ParticlesBackground component in your pages:
```javascript
import ParticlesBackground from './components/ParticlesBackground';

// In your component:
<ParticlesBackground />
```

## Building for Production

```bash
npm run build
```

## Navigation

The app consists of four main pages:
1. **Login Page**: Entry point where users enter their name and email
2. **Quiz Page**: Interactive quiz interface with timed questions and hints
3. **Leaderboard Page**: Displays player rankings and animated score display
4. **User Input Test Page**: Testing interface for user inputs

Each page is responsive and features the animated particle background.