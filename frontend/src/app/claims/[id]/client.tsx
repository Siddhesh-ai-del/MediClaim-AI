"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import AppShell from "@/components/AppShell";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useState } from "react";

export default function ClaimDetailClient({ id }: { id: string }) {
  const qc = useQueryClient();
  const { data: claim, isLoading } = useQuery({
    queryKey: ["claim", id],
    queryFn: () => api(`/claims/${id}`),
    refetchInterval: 4000,
  });

  const [overrideReason, setOverrideReason] = useState("");
  const [overrideDecision, setOverrideDecision] = useState("approve");

  const overrideMut = useMutation({
    mutationFn: () => api(`/claims/${id}/override`, { method: "POST", body: JSON.stringify({ decision: overrideDecision, amount: claim?.total_claimed_amount, reason: overrideReason }) }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["claim", id] }); setOverrideReason(""); },
  });
  const rescoreMut = useMutation({
    mutationFn: () => api(`/claims/${id}/rescore`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["claim", id] }),
  });

  if (isLoading) return <AppShell><Skeleton className="h-40 w-full" /></AppShell>;
  if (!claim) return <AppShell><p>Claim not found.</p></AppShell>;

  const riskColor = (claim.risk_score ?? 0) >= 70 ? "text-red-600" : (claim.risk_score ?? 0) >= 40 ? "text-amber-600" : "text-emerald-600";

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link href="/claims" className="text-sm text-muted-foreground hover:underline">← Back to claims</Link>
          <h1 className="text-2xl font-bold tracking-tight mt-1">{claim.claim_number}</h1>
        </div>
        <Badge variant={claim.status === "adjudicated" ? "default" : claim.status === "failed" ? "destructive" : "secondary"}>{claim.status}</Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <Card>
          <CardHeader><CardTitle>Patient & Provider</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-sm">
            <InfoRow label="Patient" value={claim.patient?.name || "—"} />
            <InfoRow label="Age / Gender" value={`${claim.patient?.age ?? "—"} / ${claim.patient?.gender ?? "—"}`} />
            <InfoRow label="Policy No." value={claim.policy_number || "—"} />
            <InfoRow label="Admission" value={claim.admission_date || "—"} />
            <InfoRow label="Discharge" value={claim.discharge_date || "—"} />
            <InfoRow label="Claimed Amount" value={claim.total_claimed_amount != null ? `₹${claim.total_claimed_amount.toLocaleString("en-IN")}` : "—"} />
            <InfoRow label="Provider" value={claim.provider?.name || "—"} />
          </CardContent>
        </Card>
        <Card className="flex flex-col items-center justify-center p-6">
          <div className="text-xs text-muted-foreground mb-2">Fraud Risk Score</div>
          <div className={`w-24 h-24 rounded-full flex items-center justify-center text-2xl font-bold border-4 ${riskColor}`} style={{ borderColor: "currentColor" }}>
            {claim.risk_score ?? "—"}
          </div>
          <div className="text-xs text-muted-foreground mt-2">Confidence: {claim.risk_confidence_low}–{claim.risk_confidence_high}</div>
          <div className="font-semibold mt-2">{claim.recommended_decision?.toUpperCase() || "PENDING"}</div>
          {claim.recommended_amount != null && <div className="text-sm text-muted-foreground">₹{claim.recommended_amount.toLocaleString("en-IN")}</div>}
          <Button variant="outline" size="sm" className="mt-3" onClick={() => rescoreMut.mutate()} disabled={rescoreMut.isPending}>Re-score</Button>
        </Card>
      </div>

      {claim.recommended_reasons?.length > 0 && (
        <Card className="mb-4">
          <CardHeader><CardTitle>Recommendation Reasons</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {claim.recommended_reasons.map((r: any, i: number) => (
              <div key={i} className="text-sm border-b pb-2 last:border-0">
                <b>{r.text}</b> <span className="text-muted-foreground">— {r.evidence}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card className="mb-4">
        <CardHeader><CardTitle>Fraud Flags ({claim.flags?.length || 0})</CardTitle></CardHeader>
        <CardContent>
          {claim.flags?.length ? claim.flags.map((f: any, i: number) => (
            <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
              <div className="flex items-center gap-2">
                <Badge variant={f.severity === "high" ? "destructive" : f.severity === "medium" ? "secondary" : "outline"}>{f.type}</Badge>
                <span className="text-sm">{f.evidence}</span>
              </div>
              <span className="text-xs text-muted-foreground">{f.source}</span>
            </div>
          )) : <p className="text-sm text-muted-foreground">No fraud flags detected.</p>}
        </CardContent>
      </Card>

      <Card className="mb-4">
        <CardHeader><CardTitle>Extracted Fields</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {claim.extraction?.fields?.map((f: any, i: number) => (
              <div key={i} className="text-xs p-2 rounded bg-muted">
                <code className="text-primary">{f.field_path}</code>
                <div className="font-medium mt-1">{JSON.stringify(f.value)}</div>
                <div className="text-muted-foreground mt-1">conf: {f.confidence?.toFixed?.(2) ?? f.confidence} {f.human_corrected && "· corrected"}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="mb-4">
        <CardHeader><CardTitle>Override Decision</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-2 items-center flex-wrap">
            <select className="h-9 rounded-md border border-input bg-background px-3 text-sm" value={overrideDecision} onChange={(e) => setOverrideDecision(e.target.value)}>
              <option value="approve">Approve</option>
              <option value="reject">Reject</option>
              <option value="partial">Partial</option>
            </select>
            <Input className="flex-1 min-w-[200px]" value={overrideReason} onChange={(e) => setOverrideReason(e.target.value)} placeholder="Reason (min 10 chars)" />
            <Button onClick={() => overrideMut.mutate()} disabled={overrideMut.isPending || overrideReason.length < 10}>Override</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Files</CardTitle></CardHeader>
        <CardContent className="space-y-1">
          {claim.files?.map((f: any) => (
            <div key={f.id} className="flex justify-between text-sm py-1 border-b last:border-0">
              <span>{f.filename}</span>
              <span className="text-muted-foreground">{f.status} · {f.ocr_engine || "—"} · {f.page_count || 0} pages</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </AppShell>
  );
}

function InfoRow({ label, value }: { label: string; value: any }) {
  return (
    <div className="flex justify-between py-1.5 border-b last:border-0 text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}