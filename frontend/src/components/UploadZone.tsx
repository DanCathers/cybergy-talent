"use client"; // this component uses browser state + events

// UploadZone — a drag-and-drop / click-to-browse file input for PDF & DOCX.

import { useCallback, useRef, useState } from "react";

// Props: a callback invoked with the chosen File, plus a disabled flag.
interface UploadZoneProps {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

// Only these extensions are accepted client-side (backend re-validates too).
const ACCEPTED = [".pdf", ".docx"];

export default function UploadZone({ onFileSelected, disabled }: UploadZoneProps) {
  // Track whether a file is being dragged over the zone (for styling).
  const [dragging, setDragging] = useState(false);
  // A ref to the hidden <input> so clicking the zone opens the file dialog.
  const inputRef = useRef<HTMLInputElement>(null);

  // Validate the extension before handing the file up to the parent.
  const handleFile = useCallback(
    (file: File | undefined) => {
      if (!file) return;
      const lower = file.name.toLowerCase();
      const ok = ACCEPTED.some((ext) => lower.endsWith(ext));
      if (!ok) {
        alert("Please upload a PDF or DOCX file.");
        return;
      }
      onFileSelected(file);
    },
    [onFileSelected]
  );

  return (
    <div
      className={`upload-zone ${dragging ? "drag" : ""}`}
      // Clicking anywhere in the zone triggers the hidden file input.
      onClick={() => !disabled && inputRef.current?.click()}
      // Drag handlers toggle the highlight and read the dropped file.
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        if (!disabled) handleFile(e.dataTransfer.files?.[0]);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx"
        style={{ display: "none" }}
        disabled={disabled}
        onChange={(e) => handleFile(e.target.files?.[0])}
      />
      <div style={{ fontSize: "2rem" }}>📄</div>
      <p style={{ margin: "8px 0 0", fontWeight: 600 }}>
        {dragging ? "Drop your resume here" : "Drag & drop your resume, or click to browse"}
      </p>
      <p className="hint">Accepted formats: PDF, DOCX · Max 10&nbsp;MB</p>
    </div>
  );
}
