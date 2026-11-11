"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import AppShell from "@/components/AppShell";

export default function DashboardPage() {
  const [kpi, setKpi] = useState<any>(null);
  useEffect(() => { api("/dashboard/kpis").then(setKpi).catch(() => {}); }, []);
  if (!kpi) return <AppShell><div className="skeleton" style={{ height: 200 }} /></AppShell>;
  return (
    <AppShell>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>Dashboard</h1>
        <p style={{ color: "#64748b", fontSize: 14, marginTop: 4 }}>Claims overview and fraud analytics</p>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginBottom: 24 }}>
        <StatCard label="Claims Processed" value={kpi.claims_processed} accent="#4f46e5" />
        <StatCard label="Pending" value={kpi.claims_pending} accent="#f59e0b" />
        <StatCard label="Fraud Flagged" value={kpi.fraud_flagged_count} accent="#ef4444" />
        <StatCard label="Amount at Risk (INR)" value={kpi.amount_at_risk?.toLocaleString("en-IN")} accent="#10b981" />
      </div>
      <div className="card" style={{ padding: 24 }}>
        <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 12 }}>Decision Rates</h2>
        <div style={{ display: "flex", gap: 24 }}>
          {Object.entries(kpi.decision_rates || {}).map(([k, v]: any) => (
            <div key={k}>
              <div style={{ fontSize: 12, color: "#64748b", textTransform: "capitalize" }}>{k}</div>
              <div style={{ fontSize: 22, fontWeight: 700 }}>{(v * 100).toFixed(0)}%</div>
            </div>
          ))}
        </div>
      </div>
    </AppShell>
  );
}

function StatCard({ label, value, accent }: { label: string; value: any; accent: string }) {
  return (
    <div className="card stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={{ color: accent }}>{value}</div>
    </div>
  );
}