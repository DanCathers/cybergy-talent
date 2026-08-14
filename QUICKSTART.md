# Cybergy Talent — Quick Start Guide

This guide gets Cybergy Talent running on your local machine in under 5 minutes using Docker.

## Prerequisites

- **Docker Desktop** installed and **running** on your PC
- **Git** (to clone the repository)
- An **Abacus AI API key**

## Step 1 — Clone the Repository

```bash
git clone https://github.com/DanCathers/cybergy-talent.git
cd cybergy-talent
```

## Step 2 — Create Your `.env` File

Docker Compose needs your Abacus AI API key. Create a file named `.env` in the
**project root** (the same folder as `docker-compose.yml`) by copying the example:

**Windows (PowerShell):**
```powershell
copy .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

Then open `.env` in a text editor and set your real values:

```env
ABACUS_API_KEY=your_actual_abacus_api_key_here
SECRET_KEY=any-long-random-string-you-like
```

> **Note:** This `.env` file is git-ignored — your secrets will never be committed.

## Step 3 — Start Everything

From the project root, run:

```bash
docker compose up --build
```

> **Important:** Use `docker compose up --build` (the base file).
> Do **not** run `docker-compose -f docker-compose.dev.yml up` on its own —
> that file is only an optional add-on for hot-reload and cannot start the app
> by itself.

This command will:
- Build the backend and frontend Docker images
- Start PostgreSQL, wait until it's healthy
- Automatically create the database tables on backend startup
- Start the FastAPI backend on port 8000
- Start the Next.js frontend on port 3000

The first build takes 3–5 minutes. Later starts are much faster.

### Optional: Hot-Reload Development Mode

If you want to edit code and see changes without rebuilding, combine both files:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

## Step 4 — Open the Application

Once the logs settle and show the servers running, open your browser to:

- **Frontend (main app):** http://localhost:3000
- **Backend API Docs (Swagger):** http://localhost:8000/docs
- **Backend Health Check:** http://localhost:8000/health

## What You Can Do

### 1. Upload a Resume
- Drag and drop a PDF or DOCX resume onto the upload zone
- The AI maps it to HR Open Standards
- Download the JSON and XML outputs

### 2. Browse the Repository
- Click "Repository" in the navigation to see processed resumes

### 3. Explore the API
- Visit http://localhost:8000/docs to try the REST and MCP endpoints interactively

## Stopping the Application

Press `Ctrl+C` in the terminal, then run:

```bash
docker compose down
```

To also wipe the database and start completely fresh:

```bash
docker compose down -v
```

## Troubleshooting

### "service backend has neither an image nor a build context specified"
You ran the dev override file by itself. Use `docker compose up --build`
instead (see Step 3).

### "port is already allocated"
Something else is using port 3000, 8000, or 5432. Stop that program, or edit
the `ports:` lines in `docker-compose.yml` to use different host ports.

### AI mapping fails / empty results
Your `ABACUS_API_KEY` is missing or incorrect in the project-root `.env`.
The app will still start and parse files, but the AI mapping step needs a valid key.

### Backend can't connect to the database
PostgreSQL takes a few seconds to initialize. Compose waits for a healthy
database automatically, but if you see connection errors, give it 10–15
seconds and check logs:
```bash
docker compose logs postgres
```

### Build errors
- Ensure Docker Desktop has at least 4GB RAM allocated
- Try a clean rebuild: `docker compose build --no-cache`

## Next Steps

Once it runs locally:
- Test with your own resume
- When ready, deploy the same Docker setup to a VPS (Hetzner, etc.)

---

**Need help?** See the main [README.md](README.md) for full documentation.
