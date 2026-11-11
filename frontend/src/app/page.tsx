"use client";
import AppShell from "@/components/AppShell";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  const items = [
    { title: "Claims", desc: "Review, score and adjudicate insurance claims", href: "/claims", cta: "View claims" },
    { title: "Dashboard", desc: "Fraud KPIs and provider analytics", href: "/dashboard", cta: "Open dashboard" },
    { title: "New Claim", desc: "Upload a claim bundle for AI processing", href: "/claims/new", cta: "Upload" },
  ];
  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">MediClaim AI</h1>
        <p className="text-muted-foreground mt-2">AI-powered health insurance claim fraud detection and adjudication.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {items.map((c) => (
          <Card key={c.title}>
            <CardHeader><CardTitle>{c.title}</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">{c.desc}</p>
              <Button onClick={() => (window.location.href = c.href)}>{c.cta}</Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </AppShell>
  );
}