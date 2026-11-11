"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import Link from "next/link";
import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

function riskBadge(score: number | null) {
  if (score == null) return <Badge variant="secondary">—</Badge>;
  if (score >= 70) return <Badge variant="destructive">{score}</Badge>;
  if (score >= 40) return <Badge className="bg-amber-100 text-amber-800 hover:bg-amber-100">{score}</Badge>;
  return <Badge className="bg-emerald-100 text-emerald-800 hover:bg-emerald-100">{score}</Badge>;
}

function statusBadge(status: string) {
  const variants: Record<string, any> = { adjudicated: "default", scored: "secondary", failed: "destructive" };
  return <Badge variant={variants[status] || "outline"}>{status}</Badge>;
}

export default function ClaimsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["claims"],
    queryFn: () => api("/claims?page_size=50"),
  });
  const claims = data?.items || [];

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Claims</h1>
          <p className="text-sm text-muted-foreground mt-1">Review, score and adjudicate insurance claims</p>
        </div>
        <Button onClick={() => (window.location.href = "/claims/new")}>+ New Claim</Button>
      </div>
      <Card className="overflow-hidden">
        {isLoading ? (
          <div className="p-6 space-y-3">
            {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}
          </div>
        ) : claims.length === 0 ? (
          <div className="p-12 text-center">
            <div className="text-4xl mb-3">📄</div>
            <p className="text-muted-foreground mb-4">No claims yet. Upload your first claim bundle.</p>
            <Button onClick={() => (window.location.href = "/claims/new")}>Upload Claim</Button>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Claim #</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Risk Score</TableHead>
                <TableHead>Decision</TableHead>
                <TableHead>Amount (INR)</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {claims.map((c: any) => (
                <TableRow key={c.id}>
                  <TableCell className="font-medium">{c.claim_number}</TableCell>
                  <TableCell>{statusBadge(c.status)}</TableCell>
                  <TableCell>{riskBadge(c.risk_score)}</TableCell>
                  <TableCell>{c.recommended_decision ? <Badge variant="outline">{c.recommended_decision}</Badge> : <span className="text-muted-foreground">—</span>}</TableCell>
                  <TableCell>{c.total_claimed_amount != null ? c.total_claimed_amount.toLocaleString("en-IN") : "—"}</TableCell>
                  <TableCell><Link href={`/claims/${c.id}`} className="text-primary text-sm font-medium hover:underline">View →</Link></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </AppShell>
  );
}