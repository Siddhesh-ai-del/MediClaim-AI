"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import AppShell from "@/components/AppShell";

export default function ClaimsPage() {
  const [claims, setClaims] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api("/claims?page_size=50").then((d) => setClaims(d.items || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);
  return (
    <AppShell>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700 }}>Claims</h1>
          <p style={{ color: "#64748b", fontSize: 14, marginTop: 4 }}>Review, score and adjudicate insurance claims</p>
        </div>
        <Link href="/claims/new" className="btn btn-primary">+ New Claim</Link>
      </div>
      <div className="card" style={{ overflow: "hidden" }}>
        {loading ? (
          <div style={{ padding: 40, textAlign: "center", color: "#94a3b8" }}>Loading claims...</div>
        ) : claims.length === 0 ? (
          <div style={{ padding: 60, textAlign: "center" }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>📄</div>
            <p style={{ color: "#64748b" }}>No claims yet. Upload your first claim bundle.</p>
            <Link href="/claims/new" className="btn btn-primary" style={{ marginTop: 16, display: "inline-flex" }}>Upload Claim</Link>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr><th>Claim #</th><th>Status</th><th>Risk Score</th><th>Decision</th><th>Amount (INR)</th><th></th></tr>
            </thead>
            <tbody>
              {claims.map((c: any) => (
                <tr key={c.id}>
                  <td style={{ fontWeight: 500 }}>{c.claim_number}</td>
                  <td><StatusBadge status={c.status} /></td>
                  <td><RiskBadge score={c.risk_score} /></td>
                  <td>{c.recommended_decision ? <span className="badge badge-info">{c.recommended_decision}</span> : <span style={{ color: "#94a3b8" }}>—</span>}</td>
                  <td>{c.total_claimed_amount != null ? c.total_claimed_amount.toLocaleString("en-IN") : "—"}</td>
                  <td><Link href={`/claims/${c.id}`} style={{ color: "#4f46e5", fontSize: 13, fontWeight: 500 }}>View →</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </AppShell>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = { queued: "badge-neutral", processing: "badge-info", extracted: "badge-info", scored: "badge-warning", adjudicated: "badge-success", failed: "badge-danger", reviewed: "badge-success" };
  return <span className={`badge ${map[status] || "badge-neutral"}`}>{status}</span>;
}

function RiskBadge({ score }: { score: number | null }) {
  if (score == null) return <span style={{ color: "#94a3b8" }}>—</span>;
  const cls = score >= 70 ? "badge-danger" : score >= 40 ? "badge-warning" : "badge-success";
  return <span className={`badge ${cls}`}>{score}</span>;
}