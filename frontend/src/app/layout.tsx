// Root layout — wraps every page with shared chrome (nav + footer).
// In the Next.js App Router, `layout.tsx` renders once and persists across
// page navigations.

import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

// Page metadata used for the <head> (title, description, SEO).
export const metadata: Metadata = {
  title: "Cybergy Talent — HR Open Standards Resume Intelligence",
  description:
    "Convert resumes into HR Open Standards v4.2.0 JSON/XML and let AI agents query the repository.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {/* Top navigation bar */}
        <nav className="nav">
          <div className="container nav-inner">
            <Link href="/" className="brand">
              Cybergy<span>Talent</span>
            </Link>
            <div className="nav-links">
              <Link href="/">Upload</Link>
              <Link href="/repository">Repository</Link>
              <Link href="/api-docs">API &amp; Agents</Link>
            </div>
          </div>
        </nav>

        {/* Page content */}
        <main className="container">{children}</main>

        {/* Global footer with the required HR Open Standards attribution */}
        <footer className="footer">
          <div className="container">
            <p>
              Copyright © The HR Open Standards Consortium. All Rights Reserved.{" "}
              <a href="http://www.hropenstandards.org">hropenstandards.org</a>
            </p>
            <p>
              This product implements and complies with the Version 4.2.0
              Specifications published by the HR Open Standards Consortium.
            </p>
            <p>Cybergy Talent · Built with Abacus AI · MIT Licensed</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
