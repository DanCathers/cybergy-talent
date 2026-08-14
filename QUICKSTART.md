# Cybergy Talent — Quick Start Guide

This guide will get Cybergy Talent running on your local machine in under 5 minutes using Docker.

## Prerequisites

- **Docker Desktop** installed and running on your PC
- **Git** (to clone the repository)
- An **Abacus AI API key** (you already have one)

## Step 1 — Clone the Repository

```bash
git clone https://github.com/DanCathers/cybergy-talent.git
cd cybergy-talent
```

## Step 2 — Set Up Environment Variables

### Backend Environment Variables

Create a file `backend/.env` with the following content:

```env
# Database connection (Docker Compose will create this)
DATABASE_URL=postgresql://cybergy:cybergy123@postgres:5432/cybergy_talent

# Abacus AI Configuration
ABACUS_AI_ENDPOINT=https://apps.abacus.ai/api/v0
OPENAI_API_KEY=your_abacus_api_key_here

# Security (generate a random secret key)
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Optional settings
MAX_UPLOAD_SIZE_MB=10
ALLOWED_ORIGINS=http://localhost:3000
```

**⚠️ Important:** Replace `your_abacus_api_key_here` with your actual Abacus AI API key.

### Frontend Environment Variables

Create a file `frontend/.env.local` with:

```env
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
```

## Step 3 — Run with Docker Compose

From the project root directory:

```bash
# Start all services (PostgreSQL, Backend, Frontend)
docker-compose -f docker-compose.dev.yml up --build
```

This command will:
- Build the Docker images
- Start PostgreSQL database
- Run database migrations (create tables)
- Start the FastAPI backend on port 8000
- Start the Next.js frontend on port 3000

The first build takes 3-5 minutes. Subsequent starts are much faster.

## Step 4 — Access the Application

Once all services are running, open your browser to:

- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **Backend Health Check:** http://localhost:8000/health

## What You Can Do

### 1. Upload a Resume
- Drag and drop a PDF or DOCX resume onto the upload zone
- The AI will parse and map it to HR Open Standards
- Download the JSON and XML outputs

### 2. Browse the Repository
- Click "Repository" in the navigation
- See all uploaded and processed resumes

### 3. Explore the API
- Visit http://localhost:8000/docs
- Try out the REST endpoints interactively
- See the MCP-compatible agent query endpoints

## Stopping the Application

Press `Ctrl+C` in the terminal, then run:

```bash
docker-compose -f docker-compose.dev.yml down
```

To completely remove the database and start fresh:

```bash
docker-compose -f docker-compose.dev.yml down -v
```

## Troubleshooting

### Port Already in Use
If you see "port 3000 is already allocated" or similar:
- Stop any other applications using ports 3000, 8000, or 5432
- Or edit `docker-compose.dev.yml` to use different ports

### Database Connection Errors
If the backend can't connect to PostgreSQL:
- Wait 10-15 seconds after starting — PostgreSQL takes time to initialize
- Check logs: `docker-compose -f docker-compose.dev.yml logs postgres`

### Build Errors
If the Docker build fails:
- Ensure Docker Desktop has enough resources (4GB+ RAM recommended)
- Try: `docker system prune -a` to clean up old images, then rebuild

## Next Steps

Once it's running locally:
- Test with your own resume
- Modify the code and see live changes (backend requires restart, frontend hot-reloads)
- When ready, deploy to your Hetzner VPS using the same docker-compose setup

---

**Need help?** Check the main [README.md](README.md) for detailed documentation.
