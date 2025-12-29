# Running the VLA Documentation Locally

## Quick Start

To run the Vision-Language-Action (VLA) documentation website locally:

### Prerequisites
- Node.js (version >= 20.0)
- npm (version >= 8.0)

### Installation and Setup

1. Navigate to the website directory:
```bash
cd docs/docs/website
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open your browser to [http://localhost:3000](http://localhost:3000) to view the site

### Available Commands

- `npm start` - Start the development server with hot reloading
- `npm run build` - Build the static website for production
- `npm run serve` - Serve the built website locally
- `npm run clear` - Clear the Docusaurus cache

### Module 4: Vision-Language-Action (VLA) Robot Control

The VLA module is available at:
- [http://localhost:3000/docs/module-4-vla-robot-control](http://localhost:3000/docs/module-4-vla-robot-control)

The module includes:
- Chapter 1: Voice-to-Action
- Chapter 2: LLM-Based Planning
- Chapter 3: Capstone – Autonomous Humanoid
- Architecture overview, glossary, and troubleshooting guides

### Troubleshooting

If you encounter issues:
1. Make sure all dependencies are installed with `npm install`
2. Clear the cache with `npm run clear` if pages aren't updating
3. Check that Node.js version meets the requirements