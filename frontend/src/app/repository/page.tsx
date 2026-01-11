"use client";

// Repository page — browse, download, and delete stored resumes.

import { useCallback, useEffect, useState } from "react";
import ResumeCard from "@/components/ResumeCard";
import { deleteResume, listResumes, ResumeSummary } from "@/lib/api";

export default function RepositoryPage() {
  const [resumes, setResumes] = useState<ResumeSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load resumes from the backend. Wrapped in useCallback so it's stable.
  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listResumes();
      setResumes(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load resumes.");
    } finally {
      setLoading(false);
    }
  }, []);

  // Run `load` once when the component first mounts.
  useEffect(() => {
    load();
  }, [load]);

  // Delete a resume then refresh the list.
  async function handleDelete(id: string) {
    if (!confirm("Delete this resume? This cannot be undone.")) return;
    try {
      await deleteResume(id);
      // Optimistically remove it from local state for a snappy UI.
      setResumes((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete resume.");
    }
  }

  return (
    <>
      <section className="hero" style={{ paddingBottom: 16 }}>
        <h1>Resume Repository</h1>
        <p>Every uploaded resume, stored as HR Open Standards data.</p>
      </section>

      <section className="section">
        {loading && <p className="muted">Loading…</p>}
        {error && <p className="error">⚠️ {error}</p>}

        {!loading && !error && resumes.length === 0 && (
          <div className="card">
            <p className="muted" style={{ margin: 0 }}>
              No resumes yet. Head to the Upload page to add your first one.
            </p>
          </div>
        )}

        <div className="resume-grid">
          {resumes.map((resume) => (
            <ResumeCard key={resume.id} resume={resume} onDelete={handleDelete} />
          ))}
        </div>
      </section>
    </>
  );
}
