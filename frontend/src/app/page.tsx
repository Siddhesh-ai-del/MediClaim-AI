import AppShell from "@/components/AppShell";
import Link from "next/link";

export default function Home() {
  return (
    <AppShell>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 32, fontWeight: 700, letterSpacing: "-0.02em" }}>MediClaim AI</h1>
        <p style={{ color: "#64748b", marginTop: 6, fontSize: 16 }}>AI-powered health insurance claim fraud detection and adjudication.</p>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16 }}>
        {[
          { title: "Claims", desc: "Review, score and adjudicate claims", href: "/claims", cta: "View claims" },
          { title: "Dashboard", desc: "Fraud KPIs and provider analytics", href: "/dashboard", cta: "Open dashboard" },
          { title: "New Claim", desc: "Upload a claim bundle for processing", href: "/claims/new", cta: "Upload" },
        ].map((c) => (
          <div key={c.title} className="card" style={{ padding: 24 }}>
            <h3 style={{ fontSize: 18, fontWeight: 600 }}>{c.title}</h3>
            <p style={{ color: "#64748b", fontSize: 14, marginTop: 6 }}>{c.desc}</p>
            <Link href={c.href} className="btn btn-primary" style={{ marginTop: 16, display: "inline-flex" }}>{c.cta}</Link>
          </div>
        ))}
      </div>
    </AppShell>
  );
}