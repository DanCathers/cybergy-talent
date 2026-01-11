"use client";

// Home page — explains Cybergy Talent and provides the upload workflow.

import { useState } from "react";
import UploadZone from "@/components/UploadZone";
import ConversionResult from "@/components/ConversionResult";
import { uploadResume, UploadResponse } from "@/lib/api";

export default function HomePage() {
  // Component state: whether an upload is in progress, the result, and errors.
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Handle a selected file: upload it, then show the extraction result.
  async function handleFile(file: File) {
    setError(null);
    setResult(null);
    setUploading(true);
    try {
      const data = await uploadResume(file);
      setResult(data);
    } catch (err) {
      // Show a friendly error message from the thrown Error.
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <>
      {/* Hero: what it is and why it's innovative. */}
      <section className="hero">
        <span className="badge">HR Open Standards v4.2.0</span>
        <h1>Turn resumes into agent-ready intelligence.</h1>
        <p>
          Cybergy Talent converts PDF and Word resumes into standardized,
          machine-readable JSON and XML that conform to HR Open Standards — then
          exposes them through an API that AI agents can query directly.
        </p>
      </section>

      {/* Feature highlights */}
      <section className="section">
        <div className="features">
          <div className="card feature">
            <h3>🤖 AI-powered mapping</h3>
            <p>An LLM extracts and maps every resume section to the standard.</p>
          </div>
          <div className="card feature">
            <h3>📐 Standards-compliant</h3>
            <p>Outputs valid HR Open Standards PersonProfile JSON &amp; XML.</p>
          </div>
          <div className="card feature">
            <h3>🔌 MCP agent API</h3>
            <p>AI agents discover tools and query the repository over HTTP.</p>
          </div>
          <div className="card feature">
            <h3>🔒 DevSecOps built-in</h3>
            <p>Validated uploads, rate limits, and automated security scans.</p>
          </div>
        </div>
      </section>

      {/* Upload workflow */}
      <section className="section">
        <h2>Upload a resume</h2>
        <UploadZone onFileSelected={handleFile} disabled={uploading} />

        {/* Indeterminate progress bar while the AI mapping runs. */}
        {uploading && (
          <>
            <div className="progress">
              <div className="progress-bar" />
            </div>
            <p className="muted" style={{ marginTop: 8 }}>
              Extracting text and mapping to HR Open Standards…
            </p>
          </>
        )}

        {error && <p className="error">⚠️ {error}</p>}
      </section>

      {/* Show the result once conversion succeeds. */}
      {result && <ConversionResult resumeId={result.id} profile={result.profile} />}
    </>
  );
}
