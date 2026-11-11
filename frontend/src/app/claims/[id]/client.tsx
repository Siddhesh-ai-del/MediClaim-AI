"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import AppShell from "@/components/AppShell";
import Link from "next/link";

export default function ClaimDetailClient({ id }: { id: string }) {
  const [claim, setClaim] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [overrideReason, setOverrideReason] = useState("");
  const [overrideDecision, setOverrideDecision] = useState("approve");

  async function load() {
    try { setClaim(await api(`/claims/${id}`)); } catch {}
    setLoading(false);
  }
  useEffect(() => { load(); const t = setInterval(load, 4000); return () => clearInterval(t); }, [id]);

  async function doOverride() {
    await api(`/claims/${id}/override`, { method: "POST", body: JSON.stringify({ decision: overrideDecision, amount: claim?.total_claimed_amount, reason: overrideReason }) });
    load();
  }
  async function rescore() {
    await api(`/claims/${id}/rescore`, { method: "POST" });
    load();
  }

  if (loading) return <AppShell><div className="skeleton" style={{ height: 200 }} /></AppShell>;
  if (!claim) return <AppShell><p>Claim not found.</p></AppShell>;

  const riskColor = (claim.risk_score ?? 0) >= 70 ? "#ef4444" : (claim.risk_score ?? 0) >= 40 ? "#f59e0b" : "#10b981";

  return (
    <AppShell>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div>
          <Link href="/claims" style={{ fontSize: 13, color: "#64748b" }}>← Back to claims</Link>
          <h1 style={{ fontSize: 24, fontWeight: 700, marginTop: 4 }}>{claim.claim_number}</h1>
        </div>
        <StatusBadge status={claim.status} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        <div className="card" style={{ padding: 24 }}>
          <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>Patient & Provider</h2>
          <InfoRow label="Patient" value={claim.patient?.name || "—"} />
          <InfoRow label="Age / Gender" value={`${claim.patient?.age ?? "—"} / ${claim.patient?.gender ?? "—"}`} />
          <InfoRow label="Policy No." value={claim.policy_number || "—"} />
          <InfoRow label="Admission" value={claim.admission_date || "—"} />
          <InfoRow label="Discharge" value={claim.discharge_date || "—"} />
          <InfoRow label="Claimed Amount" value={claim.total_claimed_amount != null ? `₹${claim.total_claimed_amount.toLocaleString("en-IN")}` : "—"} />
          <InfoRow label="Provider" value={claim.provider?.name || "—"} />
        </div>
        <div className="card" style={{ padding: 24, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
          <div style={{ fontSize: 13, color: "#64748b", marginBottom: 8 }}>Fraud Risk Score</div>
          <div className="risk-ring" style={{ background: `${riskColor}15`, color: riskColor, border: `3px solid ${riskColor}` }}>
            {claim.risk_score ?? "—"}
          </div>
          <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 8 }}>Confidence: {claim.risk_confidence_low}–{claim.risk_confidence_high}</div>
          <div style={{ marginTop: 12, fontSize: 14, fontWeight: 600 }}>{claim.recommended_decision?.toUpperCase() || "PENDING"}</div>
          {claim.recommended_amount != null && <div style={{ fontSize: 13, color: "#64748b" }}>₹{claim.recommended_amount.toLocaleString("en-IN")}</div>}
          <button onClick={rescore} className="btn btn-secondary" style={{ marginTop: 12, fontSize: 12 }}>Re-score</button>
        </div>
      </div>

      {claim.recommended_reasons?.length > 0 && (
        <div className="card" style={{ padding: 20, marginBottom: 16 }}>
          <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>Recommendation Reasons</h2>
          {claim.recommended_reasons.map((r: any, i: number) => (
            <div key={i} style={{ fontSize: 13, padding: "6px 0", borderBottom: "1px solid #f1f5f9" }}>
              <b>{r.text}</b> <span style={{ color: "#94a3b8" }}>— {r.evidence}</span>
            </div>
          ))}
        </div>
      )}

      <div className="card" style={{ padding: 20, marginBottom: 16 }}>
        <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>Fraud Flags ({claim.flags?.length || 0})</h2>
        {claim.flags?.length ? claim.flags.map((f: any, i: number) => (
          <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #f1f5f9" }}>
            <div>
              <span className={`badge ${f.severity === "high" ? "badge-danger" : f.severity === "medium" ? "badge-warning" : "badge-neutral"}`}>{f.type}</span>
              <span style={{ marginLeft: 8, fontSize: 13 }}>{f.evidence}</span>
            </div>
            <span style={{ fontSize: 11, color: "#94a3b8" }}>{f.source}</span>
          </div>
        )) : <p style={{ color: "#94a3b8", fontSize: 13 }}>No fraud flags detected.</p>}
      </div>

      <div className="card" style={{ padding: 20, marginBottom: 16 }}>
        <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>Extracted Fields</h2>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          {claim.extraction?.fields?.map((f: any, i: number) => (
            <div key={i} style={{ fontSize: 12, padding: "6px 10px", background: "#f8fafc", borderRadius: 6 }}>
              <code style={{ color: "#4f46e5" }}>{f.field_path}</code>
              <div style={{ marginTop: 2, fontWeight: 500 }}>{JSON.stringify(f.value)}</div>
              <div style={{ fontSize: 10, color: "#94a3b8" }}>conf: {f.confidence?.toFixed?.(2) ?? f.confidence} {f.human_corrected && "· corrected"}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card" style={{ padding: 20, marginBottom: 16 }}>
        <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>Override Decision</h2>
        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
          <select className="input" style={{ width: 140 }} value={overrideDecision} onChange={(e) => setOverrideDecision(e.target.value)}>
            <option value="approve">Approve</option>
            <option value="reject">Reject</option>
            <option value="partial">Partial</option>
          </select>
          <input className="input" style={{ flex: 1, minWidth: 200 }} value={overrideReason} onChange={(e) => setOverrideReason(e.target.value)} placeholder="Reason (min 10 chars)" />
          <button onClick={doOverride} className="btn btn-primary">Override</button>
        </div>
      </div>

      <div className="card" style={{ padding: 20 }}>
        <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>Files</h2>
        {claim.files?.map((f: any) => (
          <div key={f.id} style={{ fontSize: 13, padding: "6px 0", borderBottom: "1px solid #f1f5f9", display: "flex", justifyContent: "space-between" }}>
            <span>{f.filename}</span>
            <span style={{ color: "#64748b" }}>{f.status} · {f.ocr_engine || "—"} · {f.page_count || 0} pages</span>
          </div>
        ))}
      </div>
    </AppShell>
  );
}

function InfoRow({ label, value }: { label: string; value: any }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid #f1f5f9", fontSize: 13 }}>
      <span style={{ color: "#64748b" }}>{label}</span>
      <span style={{ fontWeight: 500 }}>{value}</span>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = { queued: "badge-neutral", processing: "badge-info", extracted: "badge-info", scored: "badge-warning", adjudicated: "badge-success", failed: "badge-danger", reviewed: "badge-success" };
  return <span className={`badge ${map[status] || "badge-neutral"}`}>{status}</span>;
}