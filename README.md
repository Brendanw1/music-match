# music-match

A music taste clustering application that analyzes audio features and provides personalized recommendations.

## Monorepo Structure

```
music-match/
├── backend/          # Python FastAPI backend
│   ├── app/
│   │   ├── feature_extraction/  # Audio feature extraction
│   │   ├── clustering/          # Music clustering algorithms
│   │   ├── quiz/                # Quiz logic
│   │   ├── recommendations/     # Recommendation engine
│   │   ├── api/                 # API routes
│   │   ├── models/              # Data models
│   │   └── db/                  # Database operations
│   ├── pyproject.toml           # Poetry dependencies
│   └── Dockerfile
├── frontend/         # Vite React TypeScript frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── Quiz/
│   │   │   ├── Results/
│   │   │   ├── Recommendations/
│   │   │   ├── Visualizations/
│   │   │   └── ui/
│   │   ├── hooks/               # Custom hooks
│   │   ├── api/                 # API client
│   │   └── types/               # TypeScript types
│   ├── package.json             # npm dependencies
│   └── Dockerfile
├── docker-compose.yml
└── .gitignore
```

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:5173
```

### Manual Setup

#### Backend

```bash
cd backend

# Install dependencies with Poetry
poetry install

# Run development server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## Technologies

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Essentia** - Audio analysis
- **scikit-learn** - Machine learning
- **NumPy** - Numerical computing
- **Pandas** - Data analysis
- **Pydantic** - Data validation
- **aiosqlite** - Async SQLite

### Frontend
- **Vite** - Build tool
- **React** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Router DOM** - Routing
- **Recharts** - Data visualization

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check

## Development

### Backend

```bash
# Format code
poetry run black .

# Lint code
poetry run flake8

# Type check
poetry run mypy .
```

### Frontend

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## License

MIT
