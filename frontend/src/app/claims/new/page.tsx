"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";

export default function NewClaimPage() {
  const [claimNumber, setClaimNumber] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const [drag, setDrag] = useState(false);
  const router = useRouter();

  function onFiles(f: FileList | null) {
    if (!f) return;
    setFiles(Array.from(f));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (files.length === 0) { setMsg("Please select at least one file."); return; }
    setLoading(true);
    setMsg("");
    try {
      const fd = new FormData();
      fd.append("claim_number", claimNumber || `CLM-${Date.now()}`);
      for (const f of files) fd.append("files", f);
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002"}/api/v1/claims`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: fd,
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setMsg("✓ Claim created. Redirecting...");
      setTimeout(() => router.push(`/claims/${data.id}`), 800);
    } catch (e: any) {
      setMsg("Error: " + e.message.slice(0, 200));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <div style={{ maxWidth: 640 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>New Claim</h1>
        <p style={{ color: "#64748b", fontSize: 14, marginTop: 4, marginBottom: 20 }}>Upload a claim bundle for AI processing</p>
        <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div>
            <label style={{ fontSize: 13, fontWeight: 500, display: "block", marginBottom: 6 }}>Claim number (optional)</label>
            <input className="input" value={claimNumber} onChange={(e) => setClaimNumber(e.target.value)} placeholder="CLM-2026-0001" />
          </div>
          <div>
            <label style={{ fontSize: 13, fontWeight: 500, display: "block", marginBottom: 6 }}>Documents (PDF / PNG / JPEG, max 10 files, 20MB each)</label>
            <div
              onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
              onDragLeave={() => setDrag(false)}
              onDrop={(e) => { e.preventDefault(); setDrag(false); onFiles(e.dataTransfer.files); }}
              style={{
                border: `2px dashed ${drag ? "#4f46e5" : "#cbd5e1"}`,
                borderRadius: 12,
                padding: "40px 20px",
                textAlign: "center",
                background: drag ? "#eef2ff" : "white",
                cursor: "pointer",
                transition: "all 0.15s",
              }}
              onClick={() => document.getElementById("fileInput")?.click()}
            >
              <div style={{ fontSize: 36, marginBottom: 8 }}>📎</div>
              <div style={{ fontWeight: 500 }}>Drop files here or click to browse</div>
              <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 4 }}>PDF, PNG, JPEG</div>
              <input id="fileInput" type="file" multiple accept=".pdf,image/*" onChange={(e) => onFiles(e.target.files)} style={{ display: "none" }} />
            </div>
            {files.length > 0 && (
              <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 6 }}>
                {files.map((f, i) => (
                  <div key={i} style={{ display: "flex", justifyContent: "space-between", fontSize: 13, padding: "6px 10px", background: "#f1f5f9", borderRadius: 6 }}>
                    <span>{f.name}</span>
                    <span style={{ color: "#64748b" }}>{(f.size / 1024).toFixed(1)} KB</span>
                  </div>
                ))}
              </div>
            )}
          </div>
          {msg && <p style={{ fontSize: 13, color: msg.startsWith("Error") ? "#ef4444" : "#10b981" }}>{msg}</p>}
          <button disabled={loading} className="btn btn-primary" type="submit" style={{ alignSelf: "flex-start" }}>
            {loading ? "Uploading..." : "Submit Claim"}
          </button>
        </form>
      </div>
    </AppShell>
  );
}