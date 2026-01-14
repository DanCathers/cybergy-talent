<div align="center">

# 🧠 Cybergy Talent

### AI-agent-queryable resume intelligence, built on HR Open Standards

Convert **PDF & DOCX resumes** into standardized, machine-readable
**HR Open Standards v4.2.0** JSON and XML — then let **AI agents query the
repository** through a clean REST + MCP API.

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![CI](https://i.ytimg.com/vi/Y1QyGD5oFUM/maxresdefault.jpg)
[![Security Scan](https://miro.medium.com/v2/resize:fit:1400/1*CxRm67bUlvPiQozf7ihtqA.png)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)

</div>

---

## What is Cybergy Talent?

Recruiting data is trapped in inconsistent resume documents. **Cybergy Talent**
solves that by using an LLM to read a resume and map it onto the
**HR Open Standards `PersonProfileType`** — the open, industry-backed schema for
representing a person's professional profile.

The result is a searchable repository of **standardized talent data** that is:

- **Interoperable** — valid HR Open Standards JSON & XML, ready for any HR system.
- **Agent-ready** — an **MCP-compatible** API so AI agents can discover and query
  candidates programmatically ("find me Python engineers with 5+ years").
- **Secure by design** — DevSecOps baked in: validated uploads, rate limiting,
  static analysis, container scanning, and automated dependency updates.

> Why it's innovative: most resume parsers dump ad-hoc JSON. Cybergy Talent
> targets a **published open standard** *and* exposes the data through the
> emerging **Model Context Protocol** pattern, making it a first-class data
> source for autonomous AI agents.

---

## ✨ Features

- 🤖 **AI-powered mapping** — an LLM extracts and maps every resume section.
- 📐 **Standards-compliant output** — HR Open Standards v4.2.0 JSON *and* XML.
- 🧩 **Design patterns done right** — Strategy (parsers) + Factory (converters).
- 📄 **Multi-format parsing** — PDF (PyMuPDF + pdfplumber) and DOCX (python-docx).
- 🔌 **MCP agent endpoints** — tool discovery, query, single-resume fetch, skills.
- 🔎 **Repository search** — by free text, skills, education, and experience.
- 🔒 **DevSecOps** — Bandit, Trivy, pip-audit, Dependabot, non-root containers.
- 🎨 **Clean Next.js frontend** — drag-and-drop upload, live preview, downloads.
- 🐳 **One-command startup** — full stack via Docker Compose.

---

## 🏗️ Architecture

Layered / Clean Architecture keeps each concern independent and testable:

```
                     ┌─────────────────────────────┐
                     │        Next.js Frontend       │
                     │  Upload · Repository · Docs   │
                     └───────────────┬───────────────┘
                                     │ HTTP (REST + MCP)
                     ┌───────────────▼───────────────┐
                     │      FastAPI (async) API       │
                     │  api/v1: resumes · convert ·   │
                     │          search · mcp          │
                     ├───────────────────────────────┤
                     │        Service Layer           │
                     │  resume · conversion · search  │
                     ├───────────────┬───────────────┤
                     │   Parsers     │  Converters    │
                     │  (Strategy)   │  (Factory)     │
                     │  PDF · DOCX   │  JSON · XML    │
                     ├───────────────┴───────────────┤
                     │   Schemas (Pydantic)           │
                     │   HR Open Standards mapping    │
                     ├───────────────────────────────┤
                     │   SQLAlchemy (async) + Alembic │
                     └───────────────┬───────────────┘
                                     │
                     ┌───────────────▼───────────────┐
                     │        PostgreSQL 15           │
                     └───────────────────────────────┘
        AI mapping ──►  Abacus AI LLM (OpenAI-compatible, gpt-4o)
```

**Design patterns**

| Pattern    | Where                              | Why |
|------------|------------------------------------|-----|
| Strategy   | `parsers/` (PDF vs DOCX)           | Swap file-type algorithms behind one interface |
| Factory    | `parser_factory`, `converter_factory` | Centralize object creation by type/format |
| Repository/Service | `services/`                | Keep business logic out of the API routers |

---

## 🧰 Tech Stack

| Layer        | Technology |
|--------------|-----------|
| Backend      | Python 3.11, FastAPI (async), Uvicorn |
| Validation   | Pydantic v2, pydantic-settings |
| Parsing      | PyMuPDF (fitz), pdfplumber, python-docx |
| AI mapping   | Abacus AI LLM (OpenAI-compatible endpoint), `gpt-4o` |
| Output       | JSON (stdlib), XML (lxml) |
| Database     | PostgreSQL 15, SQLAlchemy 2 (async), Alembic |
| Frontend     | Next.js 14 (App Router), React 18, TypeScript |
| Security     | slowapi (rate limits), python-magic, security headers |
| DevSecOps    | GitHub Actions, Bandit, Trivy, pip-audit, Dependabot |
| Containers   | Docker, Docker Compose (non-root images) |

---

## 🚀 Quick Start (Docker Compose)

The fastest way to run the whole stack (Postgres + backend + frontend):

```bash
# 1) Clone
git clone https://github.com/DanCathers/cybergy-talent.git
cd cybergy-talent

# 2) Provide your Abacus AI API key (used for AI mapping)
export ABACUS_API_KEY="your_abacus_api_key_here"
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"

# 3) Launch everything
docker compose up --build
```

Then open:

- **Frontend:** http://localhost:3000
- **API docs (Swagger):** http://localhost:8000/docs
- **MCP tool schema:** http://localhost:8000/api/v1/mcp/schema

### Local development (hot reload)

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Running the backend without Docker

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit .env with your values
alembic upgrade head          # create the database schema
uvicorn app.main:app --reload
```

---

## 📚 API Documentation

Interactive docs are generated automatically by FastAPI:

- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`
- **OpenAPI JSON:** `/openapi.json`

### Core REST endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/resumes/upload` | Upload a PDF/DOCX, parse, AI-map, store |
| `GET`  | `/api/v1/resumes/` | List resumes (paginated) |
| `GET`  | `/api/v1/resumes/{id}` | Get one resume (full profile) |
| `DELETE` | `/api/v1/resumes/{id}` | Delete a resume |
| `GET`  | `/api/v1/resumes/{id}/download/json` | Download HR Open Standards JSON |
| `GET`  | `/api/v1/resumes/{id}/download/xml` | Download HR Open Standards XML |
| `POST` | `/api/v1/search/` | Search by text, skills, education, experience |
| `POST` | `/api/v1/convert/text` | Map raw text to a profile (no storage) |

---

## 🔌 MCP Agent Integration

Cybergy Talent exposes **MCP-compatible** endpoints so AI agents can discover
and query the repository. Every response uses a consistent envelope:
`{ "status", "data", "metadata" }`.

| Method | Path | Purpose |
|--------|------|---------|
| `GET`  | `/api/v1/mcp/schema` | Discover available tools + input schemas |
| `POST` | `/api/v1/mcp/query` | Query by natural language and/or skills |
| `GET`  | `/api/v1/mcp/resume/{id}` | Fetch a resume as full HR Open Standards JSON |
| `GET`  | `/api/v1/mcp/skills` | Aggregated skill list across all resumes |

**Example agent query:**

```bash
curl -X POST http://localhost:8000/api/v1/mcp/query \
  -H "Content-Type: application/json" \
  -d '{"query": "python backend engineers", "skills": ["python"], "limit": 5}'
```

```json
{
  "status": "ok",
  "data": { "results": [ { "id": "…", "full_name": "…", "skills": ["python", "fastapi"] } ] },
  "metadata": { "total_matches": 1, "returned": 1 }
}
```

---

## 📐 HR Open Standards Compliance

This project implements the **`PersonProfileType`** data model from
[HR Open Standards](http://www.hropenstandards.org) v4.2.0, covering name,
communication, education, employment, certifications, licenses, skills
(competencies), affiliations, publications, patents, military service, and
references.

Every generated JSON and XML document embeds the required notices:

```json
{
  "_attribution": "Copyright © The HR Open Standards Consortium. All Rights Reserved. http://www.hropenstandards.org",
  "_compliance": "This product implements and complies with the Version 4.2.0 Specifications as published by the HR Open Standards Consortium at http://www.hropenstandards.org"
}
```

> **Attribution:** Copyright © The HR Open Standards Consortium. All Rights
> Reserved. http://www.hropenstandards.org
>
> **Compliance:** This product implements and complies with the Version 4.2.0
> Specifications as published by the HR Open Standards Consortium at
> http://www.hropenstandards.org

Reference schemas are included under [`schemas/`](./schemas) for traceability.
The HR Open Standards specifications remain the property of the HR Open
Standards Consortium and are governed by their license — separate from the MIT
license covering this project's own source code.

---

## 🔒 Security (DevSecOps)

- ✅ Uploads validated by **both** file extension and MIME type
- ✅ 10&nbsp;MB upload size limit; empty-file rejection
- ✅ Per-IP **rate limiting** on the upload endpoint (slowapi)
- ✅ Hardening **security headers** middleware on every response
- ✅ All configuration from **environment variables** (no secrets in code)
- ✅ Docker images run as a **non-root** user
- ✅ CI: **flake8 / black / isort**, **Bandit** static analysis, **pytest**
- ✅ Weekly **Trivy** image scan + **pip-audit** dependency audit
- ✅ **Dependabot** for pip, npm, and GitHub Actions

---

## 🧪 Testing

```bash
cd backend
pytest --cov=app
```

The test suite covers the parser/converter factories and verifies that every
generated document carries the required HR Open Standards attribution.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository and create a feature branch.
2. Make your changes with tests and clear commit messages.
3. Ensure `flake8`, `black --check`, `isort --check`, and `pytest` all pass.
4. Open a pull request describing your change.

---

## 📄 License

Cybergy Talent's source code is released under the **[MIT License](./LICENSE)**.

The HR Open Standards schemas are © The HR Open Standards Consortium and are
used under their own license — see the [LICENSE](./LICENSE) third-party notice
and [`schemas/README.md`](./schemas/README.md).

---

<div align="center">

Built with ❤️ and **[Abacus AI](https://abacus.ai)** · Created by
[Dan Cathers](https://github.com/DanCathers)

</div>
