// API client for the Cybergy Talent backend.
//
// A thin, typed wrapper around `fetch` so components don't repeat URL and
// error-handling boilerplate. The base URL comes from an environment variable
// so the same build works locally and in Docker.

// `NEXT_PUBLIC_` vars are exposed to the browser by Next.js at build time.
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

// ---- Types mirroring the backend Pydantic schemas (subset) ----
export interface ResumeSummary {
  id: string;
  profile_name: string | null;
  full_name: string | null;
  top_skills: string[];
  source_filename: string | null;
  created_at: string;
}

export interface ResumeListResponse {
  items: ResumeSummary[];
  total: number;
  page: number;
  page_size: number;
}

// The HR Open Standards profile is deeply nested; we type it loosely on the
// frontend since we mostly display it as formatted JSON.
export interface PersonProfile {
  [key: string]: unknown;
}

export interface UploadResponse {
  id: string;
  message: string;
  profile: PersonProfile;
}

// Build a full URL for a given API path.
export function apiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

// Upload a resume file and return the parsed + mapped profile.
export async function uploadResume(file: File): Promise<UploadResponse> {
  // FormData sends the file as multipart/form-data (what FastAPI expects).
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(apiUrl("/api/v1/resumes/upload"), {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    // Surface the backend's error detail to the UI when available.
    const detail = await safeDetail(response);
    throw new Error(detail || `Upload failed (HTTP ${response.status}).`);
  }
  return (await response.json()) as UploadResponse;
}

// Fetch a paginated list of stored resumes.
export async function listResumes(
  page = 1,
  pageSize = 20
): Promise<ResumeListResponse> {
  const response = await fetch(
    apiUrl(`/api/v1/resumes/?page=${page}&page_size=${pageSize}`),
    { cache: "no-store" } // always fetch fresh data
  );
  if (!response.ok) throw new Error(`Failed to load resumes (HTTP ${response.status}).`);
  return (await response.json()) as ResumeListResponse;
}

// Delete a resume by id.
export async function deleteResume(id: string): Promise<void> {
  const response = await fetch(apiUrl(`/api/v1/resumes/${id}`), {
    method: "DELETE",
  });
  if (!response.ok && response.status !== 204) {
    throw new Error(`Failed to delete resume (HTTP ${response.status}).`);
  }
}

// Build the download URL for a resume in a given format ("json" | "xml").
export function downloadUrl(id: string, fmt: "json" | "xml"): string {
  return apiUrl(`/api/v1/resumes/${id}/download/${fmt}`);
}

// Try to read a JSON error detail from a failed response.
async function safeDetail(response: Response): Promise<string | null> {
  try {
    const data = await response.json();
    return typeof data?.detail === "string" ? data.detail : null;
  } catch {
    return null;
  }
}
