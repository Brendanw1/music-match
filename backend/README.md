# Music Match Backend

Python FastAPI backend for the Music Match application.

## Setup

```bash
# Install dependencies
poetry install

# Run development server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Structure

- `/app` - Main application code
  - `/feature_extraction` - Audio feature extraction
  - `/clustering` - Music clustering algorithms
  - `/quiz` - Quiz logic and endpoints
  - `/recommendations` - Recommendation engine
  - `/api` - API routes
  - `/models` - Data models
  - `/db` - Database operations
