"use client";

// ResumeCard — a single row in the repository browser.

import { downloadUrl, ResumeSummary } from "@/lib/api";

interface ResumeCardProps {
  resume: ResumeSummary;
  onDelete: (id: string) => void;
}

export default function ResumeCard({ resume, onDelete }: ResumeCardProps) {
  // Format the ISO timestamp into a friendly local date string.
  const created = new Date(resume.created_at).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  return (
    <div className="card resume-card">
      <div>
        <h3 style={{ margin: "0 0 4px" }}>
          {resume.full_name || resume.profile_name || "Unnamed candidate"}
        </h3>
        <p className="muted" style={{ margin: 0 }}>
          {resume.source_filename || "resume"} · added {created}
        </p>

        {/* Show up to a handful of skills as chips. */}
        <div style={{ marginTop: 8 }}>
          {resume.top_skills.length === 0 ? (
            <span className="muted">No skills detected</span>
          ) : (
            resume.top_skills.map((skill) => (
              <span key={skill} className="chip">
                {skill}
              </span>
            ))
          )}
        </div>

        <div className="btn-row">
          <a className="btn secondary" href={downloadUrl(resume.id, "json")}>
            JSON
          </a>
          <a className="btn secondary" href={downloadUrl(resume.id, "xml")}>
            XML
          </a>
        </div>
      </div>

      {/* Delete button calls back up to the parent to remove the resume. */}
      <button className="btn danger" onClick={() => onDelete(resume.id)}>
        Delete
      </button>
    </div>
  );
}
