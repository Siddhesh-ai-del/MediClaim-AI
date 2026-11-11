"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const nav = [
  { href: "/", label: "Overview", icon: "◆" },
  { href: "/dashboard", label: "Dashboard", icon: "  " },
  { href: "/claims", label: "Claims", icon: "  " },
  { href: "/claims/new", label: "New Claim", icon: "+" },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <aside className="sidebar" style={{ position: "sticky", top: 0, height: "100vh" }}>
        <div style={{ padding: "4px 12px 16px", fontSize: 18, fontWeight: 700, color: "#4f46e5" }}>MediClaim AI</div>
        <div style={{ fontSize: 11, color: "#94a3b8", padding: "0 12px 16px", textTransform: "uppercase", letterSpacing: "0.08em" }}>Navigation</div>
        {nav.map((n) => (
          <Link key={n.href} href={n.href} className={`sidebar-link ${pathname === n.href ? "active" : ""}`}>
            <span style={{ width: 18, textAlign: "center" }}>{n.icon}</span>
            {n.label}
          </Link>
        ))}
        <div style={{ marginTop: "auto", padding: "16px 12px 0", borderTop: "1px solid #e2e8f0" }}>
          <Link href="/login" className="sidebar-link">Sign out / Login</Link>
        </div>
      </aside>
      <main style={{ flex: 1, padding: "28px 32px", maxWidth: 1200, margin: "0 auto" }}>{children}</main>
    </div>
  );
}