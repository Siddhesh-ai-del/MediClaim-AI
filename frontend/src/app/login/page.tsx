"use client";
import { useState } from "react";
import { login } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("admin@demo.med");
  const [password, setPassword] = useState("AdminPass123!");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      router.push("/claims");
    } catch (e: any) {
      setErr("Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  }
  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "linear-gradient(135deg, #eef2ff 0%, #f8fafc 100%)" }}>
      <div className="card" style={{ width: 400, padding: 40 }}>
        <div style={{ textAlign: "center", marginBottom: 28 }}>
          <div style={{ fontSize: 24, fontWeight: 700, color: "#4f46e5" }}>MediClaim AI</div>
          <div style={{ color: "#64748b", fontSize: 14, marginTop: 4 }}>Sign in to your account</div>
        </div>
        <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <div>
            <label style={{ fontSize: 13, fontWeight: 500, display: "block", marginBottom: 6 }}>Email</label>
            <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" />
          </div>
          <div>
            <label style={{ fontSize: 13, fontWeight: 500, display: "block", marginBottom: 6 }}>Password</label>
            <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
          </div>
          {err && <p style={{ color: "#ef4444", fontSize: 13 }}>{err}</p>}
          <button disabled={loading} className="btn btn-primary" type="submit" style={{ width: "100%", marginTop: 6 }}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <div style={{ marginTop: 20, fontSize: 12, color: "#94a3b8", textAlign: "center" }}>
          Demo: admin@demo.med / AdminPass123!
        </div>
      </div>
    </div>
  );
}