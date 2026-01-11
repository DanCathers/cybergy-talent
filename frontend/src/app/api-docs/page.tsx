"use client";

// API & Agents page — links to the interactive API docs and explains how AI
// agents can query the repository through the MCP-compatible endpoints.

import { apiUrl } from "@/lib/api";

export default function ApiDocsPage() {
  return (
    <>
      <section className="hero" style={{ paddingBottom: 16 }}>
        <h1>API &amp; AI Agent Integration</h1>
        <p>Everything an agent needs to discover and query Cybergy Talent.</p>
      </section>

      <section className="section">
        <div className="card">
          <h2 style={{ marginTop: 0 }}>Interactive API documentation</h2>
          <p className="muted">
            The backend ships with auto-generated OpenAPI docs (Swagger UI).
          </p>
          <div className="btn-row">
            {/* These open the FastAPI docs served by the backend. */}
            <a className="btn" href={apiUrl("/docs")} target="_blank" rel="noreferrer">
              Open Swagger UI
            </a>
            <a
              className="btn secondary"
              href={apiUrl("/redoc")}
              target="_blank"
              rel="noreferrer"
            >
              Open ReDoc
            </a>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="card">
          <h2 style={{ marginTop: 0 }}>MCP-compatible agent endpoints</h2>
          <p className="muted">
            AI agents can discover capabilities and query the repository using a
            consistent <code>{"{ status, data, metadata }"}</code> envelope.
          </p>
          <ul>
            <li>
              <code>GET /api/v1/mcp/schema</code> — discover available tools
            </li>
            <li>
              <code>POST /api/v1/mcp/query</code> — search by natural language or skills
            </li>
            <li>
              <code>GET /api/v1/mcp/resume/&#123;id&#125;</code> — full HR Open Standards JSON
            </li>
            <li>
              <code>GET /api/v1/mcp/skills</code> — aggregated skills across all resumes
            </li>
          </ul>
          <div className="btn-row">
            <a
              className="btn secondary"
              href={apiUrl("/api/v1/mcp/schema")}
              target="_blank"
              rel="noreferrer"
            >
              View MCP tool schema
            </a>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="card">
          <h2 style={{ marginTop: 0 }}>Example agent query</h2>
          <pre className="code">{`curl -X POST ${
            process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
          }/api/v1/mcp/query \\
  -H "Content-Type: application/json" \\
  -d '{"query": "python backend engineers", "skills": ["python"], "limit": 5}'`}</pre>
        </div>
      </section>
    </>
  );
}
