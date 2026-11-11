"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function DashboardPage() {
  const [kpi, setKpi] = useState<any>(null);
  useEffect(() => { api("/dashboard/kpis").then(setKpi).catch(()=>{}); }, []);
  if (!kpi) return <p>Loading...</p>;
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Dashboard</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="border rounded p-3 bg-white"><div className="text-xs text-gray-500">Claims processed</div><div className="text-2xl font-bold">{kpi.claims_processed}</div></div>
        <div className="border rounded p-3 bg-white"><div className="text-xs text-gray-500">Pending</div><div className="text-2xl font-bold">{kpi.claims_pending}</div></div>
        <div className="border rounded p-3 bg-white"><div className="text-xs text-gray-500">Fraud flagged</div><div className="text-2xl font-bold">{kpi.fraud_flagged_count}</div></div>
        <div className="border rounded p-3 bg-white"><div className="text-xs text-gray-500">Amount at risk</div><div className="text-2xl font-bold">{kpi.amount_at_risk}</div></div>
      </div>
      <div className="border rounded p-3 bg-white">
        <h2 className="font-semibold mb-2">Decision rates</h2>
        <pre className="text-sm">{JSON.stringify(kpi.decision_rates, null, 2)}</pre>
      </div>
    </div>
  );
}