"use client";

// ConversionResult — shows the extracted HR Open Standards profile as a JSON
// preview and offers JSON / XML download buttons.

import { downloadUrl, PersonProfile } from "@/lib/api";

interface ConversionResultProps {
  resumeId: string;
  profile: PersonProfile;
}

export default function ConversionResult({ resumeId, profile }: ConversionResultProps) {
  // Pretty-print the profile for the preview panel.
  const prettyJson = JSON.stringify(profile, null, 2);

  return (
    <div className="card section">
      <h2 style={{ marginTop: 0 }}>✅ Extraction complete</h2>
      <p className="muted">
        Your resume has been mapped to the HR Open Standards v4.2.0
        PersonProfileType. Download it as JSON or XML below.
      </p>

      {/* Download buttons link straight to the backend download endpoints. */}
      <div className="btn-row">
        <a className="btn" href={downloadUrl(resumeId, "json")}>
          ⬇️ Download JSON
        </a>
        <a className="btn secondary" href={downloadUrl(resumeId, "xml")}>
          ⬇️ Download XML
        </a>
      </div>

      <h3>Preview</h3>
      {/* The <pre> preserves whitespace so the JSON stays readable. */}
      <pre className="code">{prettyJson}</pre>
    </div>
  );
}
