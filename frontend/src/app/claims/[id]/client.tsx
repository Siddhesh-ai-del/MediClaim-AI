"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function ClaimDetailClient({ id }: { id: string }) {
  const [claim, setClaim] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [overrideReason, setOverrideReason] = useState("");
  const [overrideDecision, setOverrideDecision] = useState("approve");

  async function load() {
    try { setClaim(await api(`/claims/${id}`)); } catch {}
    setLoading(false);
  }
  useEffect(() => { load(); const t = setInterval(load, 3000); return () => clearInterval(t); }, [id]);

  async function doOverride() {
    await api(`/claims/${id}/override`, { method: "POST", body: JSON.stringify({ decision: overrideDecision, amount: claim?.total_claimed_amount, reason: overrideReason }) });
    load();
  }
  async function rescore() {
    await api(`/claims/${id}/rescore`, { method: "POST" });
    load();
  }

  if (loading) return <p>Loading...</p>;
  if (!claim) return <p>Not found</p>;
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">{claim.claim_number} <span className="text-sm text-gray-500">({claim.status})</span></h1>
      <div className="grid grid-cols-2 gap-4">
        <div className="border rounded p-3 bg-white">
          <h2 className="font-semibold mb-2">Patient / Provider</h2>
          <p>Patient: {claim.patient?.name || "-"}</p>
          <p>Policy: {claim.policy_number || "-"}</p>
          <p>Admission: {claim.admission_date || "-"}</p>
          <p>Discharge: {claim.discharge_date || "-"}</p>
          <p>Amount: {claim.total_claimed_amount ?? "-"}</p>
          <p>Provider: {claim.provider?.name || "-"}</p>
        </div>
        <div className="border rounded p-3 bg-white">
          <h2 className="font-semibold mb-2">Risk & Decision</h2>
          <p>Risk score: {claim.risk_score ?? "-"} ({claim.risk_confidence_low}-{claim.risk_confidence_high})</p>
          <p>Recommended: {claim.recommended_decision || "-"} {claim.recommended_amount != null ? `(${claim.recommended_amount})` : ""}</p>
          <p>Final: {claim.final_decision || "-"}</p>
          <p>Reasons: {JSON.stringify(claim.recommended_reasons)}</p>
          <button onClick={rescore} className="mt-2 bg-gray-200 px-3 py-1 rounded text-sm">Re-score</button>
        </div>
      </div>
      <div className="border rounded p-3 bg-white">
        <h2 className="font-semibold mb-2">Flags</h2>
        {claim.flags?.length ? claim.flags.map((f:any,i:number)=><div key={i} className="text-sm border-b py-1"><b>{f.type}</b> [{f.severity}] — {f.evidence}</div>) : <p className="text-gray-500 text-sm">No flags</p>}
      </div>
      <div className="border rounded p-3 bg-white">
        <h2 className="font-semibold mb-2">Extracted Fields</h2>
        {claim.extraction?.fields?.map((f:any,i:number)=><div key={i} className="text-xs border-b py-1"><code>{f.field_path}</code>: {JSON.stringify(f.value)} (conf {f.confidence}) {f.human_corrected && <span className="text-green-600">corrected</span>}</div>)}
      </div>
      <div className="border rounded p-3 bg-white">
        <h2 className="font-semibold mb-2">Override Decision</h2>
        <select value={overrideDecision} onChange={e=>setOverrideDecision(e.target.value)} className="border p-1 rounded">
          <option value="approve">approve</option>
          <option value="reject">reject</option>
          <option value="partial">partial</option>
        </select>
        <input className="border p-1 rounded ml-2 w-64" value={overrideReason} onChange={e=>setOverrideReason(e.target.value)} placeholder="reason (min 10 chars)" />
        <button onClick={doOverride} className="ml-2 bg-blue-600 text-white px-3 py-1 rounded text-sm">Override</button>
      </div>
      <div className="border rounded p-3 bg-white">
        <h2 className="font-semibold mb-2">Files</h2>
        {claim.files?.map((f:any)=><div key={f.id} className="text-sm">{f.filename} — {f.status} ({f.ocr_engine})</div>)}
      </div>
    </div>
  );
}