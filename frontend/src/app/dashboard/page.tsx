"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import AppShell from "@/components/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function DashboardPage() {
  const { data: kpi, isLoading } = useQuery({
    queryKey: ["kpis"],
    queryFn: () => api("/dashboard/kpis"),
  });

  if (isLoading || !kpi) return (
    <AppShell>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24" />)}
      </div>
    </AppShell>
  );

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Claims overview and fraud analytics</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KpiCard label="Claims Processed" value={kpi.claims_processed} color="text-indigo-600" />
        <KpiCard label="Pending" value={kpi.claims_pending} color="text-amber-600" />
        <KpiCard label="Fraud Flagged" value={kpi.fraud_flagged_count} color="text-red-600" />
        <KpiCard label="Amount at Risk" value={`₹${kpi.amount_at_risk?.toLocaleString("en-IN")}`} color="text-emerald-600" />
      </div>
      <Card>
        <CardHeader><CardTitle>Decision Rates</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-8">
            {Object.entries(kpi.decision_rates || {}).map(([k, v]: any) => (
              <div key={k}>
                <div className="text-xs text-muted-foreground capitalize">{k}</div>
                <div className="text-2xl font-bold">{(v * 100).toFixed(0)}%</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}

function KpiCard({ label, value, color }: { label: string; value: any; color: string }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="text-xs text-muted-foreground font-medium">{label}</div>
        <div className={`text-3xl font-bold mt-2 ${color}`}>{value}</div>
      </CardContent>
    </Card>
  );
}