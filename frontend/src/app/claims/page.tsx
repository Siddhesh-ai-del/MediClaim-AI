"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";

export default function ClaimsPage() {
  const [claims, setClaims] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api("/claims?page_size=50").then(d => setClaims(d.items || [])).catch(()=>{}).finally(()=>setLoading(false));
  }, []);
  if (loading) return <p>Loading...</p>;
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-bold">Claims</h1>
        <Link href="/claims/new" className="bg-blue-600 text-white px-3 py-1 rounded text-sm">New Claim</Link>
      </div>
      <table className="w-full text-sm border">
        <thead className="bg-gray-100">
          <tr><th className="p-2 text-left">Claim #</th><th>Status</th><th>Risk</th><th>Decision</th><th>Amount</th></tr>
        </thead>
        <tbody>
          {claims.map((c:any) => (
            <tr key={c.id} className="border-t">
              <td className="p-2"><Link className="text-blue-600" href={`/claims/${c.id}`}>{c.claim_number}</Link></td>
              <td className="p-2">{c.status}</td>
              <td className="p-2">{c.risk_score ?? "-"}</td>
              <td className="p-2">{c.recommended_decision ?? "-"}</td>
              <td className="p-2">{c.total_claimed_amount ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {claims.length === 0 && <p className="text-gray-500 mt-4">No claims yet.</p>}
    </div>
  );
}